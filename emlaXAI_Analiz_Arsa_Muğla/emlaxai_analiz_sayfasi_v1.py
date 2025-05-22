
import streamlit as st
import pandas as pd
import unicodedata
import geopandas as gpd
import os
from streamlit.components.v1 import html

st.set_page_config(page_title="emlaXAI Pro - Bölgesel Analiz", layout="wide")
st.title("📊 emlaXAI Pro - Bölgesel Analiz Paneli")

# --------------------- 🔍 ARAMA BARI ---------------------
# Türkiye illeri
iller = sorted([
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin",
    "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur",
    "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan",
    "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul",
    "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir",
    "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş",
    "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas",
    "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"
])

# İlçe ve mahalle örneği (şimdilik sadece Muğla çalışır)
ilceler_mugla = ["Bodrum", "Menteşe", "Fethiye", "Marmaris", "Milas", "Datça", "Ortaca", "Köyceğiz", "Yatağan", "Dalaman", "Kavaklıdere", "Seydikemer", "Ula"]
mahalleler_ornek = ["Tüm Mahalleler", "Merkez", "Akyaka", "Torba", "Gümüşlük"]

# ----------------------------- 🧩 Arama Barı -----------------------------
with st.container():
    st.markdown("""
        <style>
        .css-1kyxreq {padding: 2rem 3rem 0rem 3rem;} /* Container iç kenar boşluğu */
        </style>
        """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns([1.7, 1.7, 1.7, 1.7, 1.7, 0.4])
    
    with col1:
        il = st.selectbox("İl", iller, index=iller.index("Muğla"))
    with col2:
        ilce = st.selectbox("İlçe", ilceler_mugla if il == "Muğla" else ["İlçe seç"])
    with col3:
        mahalle = st.selectbox("Mahalle", mahalleler_ornek)
    with col4:
        emlak_tipi = st.selectbox("Emlak Tipi", ["Arsa", "Konut", "İşyeri", "Devremülk"])
    with col5:
        durum = st.selectbox("Durum", ["Satılık", "Kiralık"])
    with col6:
        st.markdown("<div style='padding-top: 28px;'>", unsafe_allow_html=True)
        ara = st.button("Ara")
        st.markdown("</div>", unsafe_allow_html=True)





# 🧠 Filtreleme Sonucu (örnek olarak Muğla Arsa Satılık'ta analiz başlatılıyor)
if ara and il == "Muğla" and emlak_tipi == "Arsa" and durum == "Satılık":
    st.markdown("### 📌 Muğla Satılık Arsa Analizi")
    st.success(f"Seçim: {il} / {ilce} / {mahalle} / {emlak_tipi} / {durum}")
    # Analiz, grafik ve harita kodları buraya



# --------------------- 📍 HARİTA ---------------------
with open("emlaXAI_Analiz_Arsa_Muğla/googlemaps_heatmap.html", "r", encoding="utf-8") as f:
    html_content = f.read()
html(html_content, height=530, width=1800)

# --------------------- 📊 ANALİZ ---------------------
s_df = pd.read_csv("emlaXAI_Analiz_Arsa_Muğla/mugla_satilik_arsa.csv")
e_df = pd.read_csv("emlaXAI_Analiz_Arsa_Muğla/mugla_ilceler_arsa_fiyatlari.csv")

s_fiyat_col = "fiyat"
s_m2_col = "m2"
s_ilce_col = "İlçe"
e_ilce_col = "İlçe"
e_fiyat_col = "Nisan 2025 (₺/m²)"

duzeltmeler = {
    "Kavaklidere": "Kavaklıdere",
    "Koycegiz": "Köyceğiz",
    "Mentese": "Menteşe",
    "Datca": "Datça",
    "Yatagan": "Yatağan"
}
s_df[s_ilce_col] = s_df[s_ilce_col].replace(duzeltmeler)
e_df[e_ilce_col] = e_df[e_ilce_col].replace(duzeltmeler)
s_df[s_fiyat_col] = pd.to_numeric(s_df[s_fiyat_col], errors="coerce")
s_df[s_m2_col] = pd.to_numeric(s_df[s_m2_col], errors="coerce")
s_df = s_df.dropna(subset=[s_fiyat_col, s_m2_col, s_ilce_col])
s_df["fiyat_m2"] = s_df[s_fiyat_col] / s_df[s_m2_col]
s_grouped = s_df.groupby(s_ilce_col)["fiyat_m2"].mean().reset_index()
s_grouped.columns = ["İlçe", "sahibinden_fiyat"]
e_df[e_fiyat_col] = pd.to_numeric(e_df[e_fiyat_col], errors="coerce")
e_grouped = e_df[[e_ilce_col, e_fiyat_col]].copy()
e_grouped.columns = ["İlçe", "endeksa_fiyat"]
df = pd.merge(s_grouped, e_grouped, on="İlçe", how="outer")

df["EmlaXAI Ortalama m² Fiyatı"] = df.apply(
    lambda row: (row["sahibinden_fiyat"] + row["endeksa_fiyat"]) / 2
    if pd.notnull(row["sahibinden_fiyat"]) and pd.notnull(row["endeksa_fiyat"])
    else row["sahibinden_fiyat"] if pd.notnull(row["sahibinden_fiyat"])
    else row["endeksa_fiyat"], axis=1)

df["ilce_normalize"] = df["İlçe"].apply(lambda x: unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode('utf-8').lower().replace(" ", "") if pd.notnull(x) else "")
df = df.drop_duplicates(subset="ilce_normalize").sort_values("İlçe").reset_index(drop=True)
df["Ortalama Fiyat"] = pd.to_numeric(df["EmlaXAI Ortalama m² Fiyatı"], errors="coerce") * 1000
max_fiyat = df["Ortalama Fiyat"].max()
min_fiyat = df["Ortalama Fiyat"].min()
df["deger_puan"] = df["Ortalama Fiyat"].apply(
    lambda x: int(((x - min_fiyat) / (max_fiyat - min_fiyat)) * 100) if pd.notnull(x) else 0
)
def yapay_zeka_puani(puan):
    if puan >= 80: return "⭐⭐⭐⭐⭐"
    elif puan >= 60: return "⭐⭐⭐⭐☆"
    elif puan >= 40: return "⭐⭐⭐☆☆"
    elif puan >= 20: return "⭐⭐☆☆☆"
    else: return "⭐☆☆☆☆"
df["Yapay Zeka Puanı"] = df["deger_puan"].apply(yapay_zeka_puani)
ortalama_fiyat = df["Ortalama Fiyat"].mean()
std_fiyat = df["Ortalama Fiyat"].std()
df["ivme_deger"] = df["Ortalama Fiyat"].apply(lambda x: (x - ortalama_fiyat) / std_fiyat)
def yorum_etiketi(ivme):
    if ivme > 1: return "🚀 Yükselişte"
    elif ivme > 0: return "📈 Hafif Artış"
    elif ivme == 0: return "⚖️ Durgun"
    elif ivme > -1: return "📉 Hafif Düşüş"
    else: return "⏸️ Durgun"
df["Piyasa İvmesi"] = df["ivme_deger"].apply(yorum_etiketi)
df["EmlaXAI Ortalama m² Fiyatı"] = pd.to_numeric(df["EmlaXAI Ortalama m² Fiyatı"], errors="coerce").apply(lambda x: f"{x:,.0f} TL" if pd.notnull(x) else "-")
df["Ortalama Fiyat"] = df["Ortalama Fiyat"].apply(lambda x: f"{x:,.0f} TL" if pd.notnull(x) else "-")

st.subheader("📌 Seçilen Bölgeye Ait Analiz Tablosu")
st.dataframe(df[["İlçe", "EmlaXAI Ortalama m² Fiyatı", "Ortalama Fiyat", "Yapay Zeka Puanı", "Piyasa İvmesi"]], use_container_width=True)
