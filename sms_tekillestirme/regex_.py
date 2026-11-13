#çalışan son kod. 

import pandas as pd
import re
import pyodbc
from collections import defaultdict

def normalize_sms_to_template(sms_text: str) -> str:
    """
    - IP adresleri ve sunucu kodları korunur
    - Mesaj içerisindeki değişkenler etiketlere dönüştürülür
    """
    template = sms_text

    # 1. IP adreslerini koru (map ile yaparsak daha stabil olur)
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ip_matches = list(re.finditer(ip_pattern, template))
    ip_placeholders = {}

    for i, match in enumerate(ip_matches):
        ip = match.group()
        placeholder = f"<IP{i}>"
        ip_placeholders[placeholder] = ip
        template = template.replace(ip, placeholder)

    # 2. (sync host_XXXX) hosttan sonra gelen sayı için
    template = re.sub(r'(sync host)(_[a-f0-9]{6,})', r'\1_<DEGISKEN_H>', template, flags=re.IGNORECASE)

    # 3. hash onesyncsvden sonra gelen sayı için
    template = re.sub(r'(\b\w+)_([a-f0-9]{6,})', r'\1_<DEGISKEN_O>', template)

    # 4. yüzdeler: %10, % 10, 10%, 10 %, 90.50%, %90.50 gibi tüm varyasyonları kapsar
    template = re.sub(r'(%\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?\s*%)', '<YUZDE>', template)

    # 5. Ondalıklı sayılar
    template = re.sub(r'\b\d+\.\d+\b', '<FLOAT_DEGER>', template)

    # 6. Sunucu adları korunur
    server_pattern = r'\by\d{2}\b'
    protected_servers = re.findall(server_pattern, template)
    for i, server in enumerate(protected_servers):
        template = template.replace(server, f"<SERVER{i}>")

    # 7. Kalan tam sayılar
    template = re.sub(r'\b\d+\b', '<INT_DEGER>', template)

    # 8. Sunucu adlarını geri koy
    for i, server in enumerate(protected_servers):
        template = template.replace(f"<SERVER{i}>", server)

    # 9. IP adreslerini geri koy
    for placeholder, ip in ip_placeholders.items():
        template = template.replace(placeholder, ip)

    # 10. Temizlik
    template = re.sub(r'\s+', ' ', template).strip().lower()

    return template

def fetch_messages_from_mssql(server, database, table, column):
    """
    MSSQL'den Windows Authentication ile mesajları çeker.
    """
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        f"Server={server};"
        f"Database={database};"
        "Trusted_Connection=yes;"
    )

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    query = f"SELECT {column} FROM {table}"
    cursor.execute(query)
    messages = [row[0] for row in cursor.fetchall()]
    conn.close()
    return messages

def create_normalized_table(server, database, new_table_name):
    """
    Normalize edilmiş mesajları kaydetmek için tabloyu oluşturur.
    """
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        f"Server={server};"
        f"Database={database};"
        "Trusted_Connection=yes;"
    )

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute(f"""
    IF OBJECT_ID('{new_table_name}', 'U') IS NULL
    BEGIN
        CREATE TABLE {new_table_name} (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            NormalizedTemplate NVARCHAR(MAX),
            OriginalMessages NVARCHAR(MAX)
        )
    END
    """)

    conn.commit()
    conn.close()

def insert_grouped_data(server, database, new_table_name, grouped_data):
    """
    Normalize edilmiş ve gruplanmış verileri tabloya ekler.
    """
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        f"Server={server};"
        f"Database={database};"
        "Trusted_Connection=yes;"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    for template, messages in grouped_data.items():
        joined_messages = ' ;; '.join(messages)
        cursor.execute(
            f"INSERT INTO {new_table_name} (NormalizedTemplate, OriginalMessages) VALUES (?, ?)",
            (template, joined_messages)
        )
    conn.commit()
    conn.close()

def main():
    # MSSQL ayarları
    server = "10.60.160.116"
    database = "ASKAutomation"
    source_table = "ServiceMessageDetailsFiltered"
    source_column = "Message_Content"
    target_table = "NormalizedSMSMessages"

    print("MSSQL'den mesajlar alınıyor.")
    sms_messages = fetch_messages_from_mssql(server, database, source_table, source_column)
    print(f"{len(sms_messages)} mesaj çekildi.")

    print("Mesajlar normalize ediliyor ve gruplanıyor.")
    grouped = defaultdict(list)
    for msg in sms_messages:
        template = normalize_sms_to_template(msg)
        grouped[template].append(msg)
    print(f"{len(grouped)} farklı şablon tespit edildi.")

    print("Hedef tablo kontrol ediliyor/oluşturuluyor.")
    create_normalized_table(server, database, target_table)

    print("Gruplanmış veriler tabloya kaydediliyor.")
    insert_grouped_data(server, database, target_table, grouped)

    print("Tüm işlem başarıyla tamamlandı.")

if __name__ == "__main__":
    main()
