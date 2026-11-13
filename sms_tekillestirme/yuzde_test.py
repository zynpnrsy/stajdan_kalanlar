import re

def replace_percentages(text):
    # %10, % 10, 10%, 10 %, 90.50%, %90.50 gibi tüm varyasyonları kapsar
    pattern = r'(%\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?\s*%)'
    return re.sub(pattern, '<YUZDE>', text)

# Test örnekleri
texts = [
    "%10 kritik",           # başta, boşluksuz
    "% 10 kritik",          # başta, boşluklu
    "kritik 10%",           # sonda, boşluksuz
    "kritik 10 %",          # sonda, boşluklu
    "kritik 90.50%",        # float değer
    "kritik %90.50",        # float başta
    "uyarı  99.99 % > eşik" # karmaşık yapı
]

# Test sonuçlarını yazdır
for text in texts:
    print(f"Orijinal : {text}")
    print(f"Dönüştü  : {replace_percentages(text)}\n")
