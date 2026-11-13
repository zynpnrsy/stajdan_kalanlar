#UYGULAMA ADLARINA GÖRE # her 3 tool içinde ayrı int sayfası açıyor

import pandas as pd
import plotly.express as px


df = pd.read_excel("Z:\BELGELERIM\STJ9BTO\My Documents\Desktop\kodlar\yuzde_olusturma/grafik2.xlsx")

df.columns = df.columns.str.strip()

#  metrikler (1-0'lı kolon adları)
metrikler = ['APPDYNAMICS_SAYISI', 'INSTANA_SAYISI', 'ATERNITY_SAYISI']


for metrik in metrikler:
    # Grup ve say
    grouped = df.groupby(['Uygulama_Kodu', 'Sunucu_Fonksiyonu'])[metrik].sum().reset_index()

    # Grafik başlığı 
    baslik = metrik.replace('_AJAN SAYILARI', '')

    # Grafik oluştur
    fig = px.bar(
        grouped,
        x='Uygulama_Kodu',
        y=metrik,
        color='Sunucu_Fonksiyonu',
        title=f'{baslik} Kullanımı (Sunucu Fonksiyonu Bazında)',
        barmode='group',
        text=metrik
    )

    fig.update_layout(yaxis_title='Kullanım Sayısı')
    fig.show()
