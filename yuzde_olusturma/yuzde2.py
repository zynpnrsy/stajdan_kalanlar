#foto kaydeden kod. tek tek her uygulama kodu adı için kaydediyor.
import pandas as pd
import matplotlib.pyplot as plt
import os 

df = pd.read_excel("Z:\BELGELERIM\STJ9BTO\My Documents\Desktop\kodlar\yuzde_olusturma/grafik2.xlsx") 

df_filtered = df[df["Sunucu_Fonksiyonu"].str.lower().isin(["Production","Production-Dmz"])]

df_alarm = df_filtered[df_filtered["Uygulama_Kodu"].str.contains("ALARM", case=False, na=False)]
df_anka = df_filtered[df_filtered["Uygulama_Kodu"].str.contains("ANKA", case=False, na=False)]
df_mobil = df_filtered[df_filtered["Uygulama_Kodu"].str.contains("MOBİL", case=False, na=False)]
df_mobil = df_filtered[df_filtered["Uygulama_Kodu"].str.contains("ADK", case=False, na=False)]
df_mobil = df_filtered[df_filtered["Uygulama_Kodu"].str.contains("API", case=False, na=False)]

os.makedirs("grafikler",exist_ok=True)

uygulama_gruplari = df.groupby("Uygulama_Kodu")


metrikler = ['APPDYNAMICS_SAYISI', 'INSTANA_SAYISI', 'ATERNITY_SAYISI']


for uygulama_kodu, grup in uygulama_gruplari:
    toplam_satir = len(grup)
    
    yuzdeler = {}
    for metrik in metrikler:
        yuzde = grup[metrik].sum() / toplam_satir * 100
        yuzdeler[metrik] = yuzde


    plt.figure(figsize=(6, 4))
    plt.bar(yuzdeler.keys(), yuzdeler.values(), color=["#2E8B57", "#4682B4", "#DAA520"])
    plt.ylim(0, 100)
    plt.ylabel("Yüzde (%)")
    plt.title(f"{uygulama_kodu} - Ajan Kullanım Yüzdeleri")
    for i, v in enumerate(yuzdeler.values()):
        plt.text(i, v + 2, f"{v:.1f}%", ha='center', fontsize=10)


    plt.tight_layout()
    plt.savefig(f"{uygulama_kodu}_ajan_yuzdeleri.png")
    plt.close()

print("Grafikler PNG olarak kaydedildi.")

