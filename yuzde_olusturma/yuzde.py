#internet sitesine gönderiyor. ama instana-appdynamics-aternity için bir pie chart yaptı.
# + terminalde kullanım sayıları çıkıyor

import pandas as pd

df = pd.read_excel("Z:\BELGELERIM\STJ9BTO\My Documents\Desktop\kodlar\yuzde_olusturma/grafik2.xlsx")

df.columns = df.columns.str.strip()

# Hangi metrik 
metrikler = ['APPDYNAMICS_SAYISI', 'INSTANA_SAYISI', 'ATERNITY_SAYISI']


toplam_row = len(df)

sonuclar=[]

for metrik in metrikler:
    adet = df[metrik].sum()
    yuzde = df[metrik].mean()*100
    sonuclar.append( {
        "UYGULAMA":metrik.replace("_SAYISI", ""),
        "KULLANIM SAYISI": int(adet),
        "KULLANIM YUZDE": round(yuzde ,2)
         })
df_sonuc = pd.DataFrame(sonuclar)
print(df_sonuc)

import plotly.express as px
fig = px.pie(df_sonuc, values ="KULLANIM YUZDE",names="UYGULAMA",
             title="UYGULAMA KULLANIM DAGILIM", hole=0.4)

fig.show()
    