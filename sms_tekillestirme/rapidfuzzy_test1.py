#faz2 olarak threshol belirlenerek çalışan kod 

import pyodbc
from rapidfuzz import fuzz

# 1. MSSQL bağlantısı
def connect_mssql():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localdb\\ZDBdeneme;'  #  localhost ya da localdb
        'DATABASE=ASKAutomation;'
        'Trusted_Connection=yes;'  # Windows Authentication 
        # 'UID=sa;PWD=sifre123;'  # SQL Authentication 
    )

# 2. Tablodan mesajları çek
def fetch_sms(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Message_Content FROM ServiceMessageDetailsFiltered WHERE IsDeleted = 0")
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def create_output_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sysobjects WHERE name='grouped_sms' AND xtype='U'
        )
        CREATE TABLE grouped_sms (
            id INT IDENTITY(1,1) PRIMARY KEY,
            representative_message NVARCHAR(MAX),
            all_messages NVARCHAR(MAX)
        )
    """)
    conn.commit()

# 4. RapidFuzz ile benzer içerikleri grupla
def group_messages(contents, threshold=90):
    grouped = []
    visited = set()

    for i in range(len(contents)):
        if i in visited:
            continue
        current = contents[i]
        group = [current]
        visited.add(i)

        for j in range(i + 1, len(contents)):
            if j in visited:
                continue
            score = fuzz.token_set_ratio(current, contents[j])
            if score >= threshold:
                group.append(contents[j])
                visited.add(j)

        grouped.append(group)

    return grouped

# 5. Grupları SQL'e kaydet
def save_to_sql(conn, groups):
    cursor = conn.cursor()
    for group in groups:
        representative = group[0]  # İlk mesaj temsilci
        all_messages = "; ".join(group)
        cursor.execute(
            "INSERT INTO grouped_sms (representative, all_messages) VALUES (?, ?)",
            (representative, all_messages)
        )
    conn.commit()

# 6. Ana fonksiyon
def main():
    conn = connect_mssql()
    create_output_table(conn)

    print("Veriler çekiliyor")
    contents = fetch_sms(conn)
    print(f"{len(contents)} mesaj alındı.")

    print("Gruplama yapılıyor")
    groups = group_messages(contents, threshold=95)
    print(f"{len(groups)} grup bulundu.")

    print("SQL'e yazılıyor")
    save_to_sql(conn, groups)

    conn.close()
    print("Tamamlandı! grouped_sms tablosuna kaydedildi.")

if __name__ == "__main__":
    main()
