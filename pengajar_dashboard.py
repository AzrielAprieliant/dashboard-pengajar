import streamlit as st
import pandas as pd
from io import BytesIO
import requests

st.set_page_config(page_title="Dashboard Instruktur", layout="wide")

# --- 1. Load data dari GitHub ---
@st.cache_data
def load_data():
    url = "https://github.com/AzrielAprieliant/dashboard-pengajar/raw/main/Data%20Instruktur%20asli.xlsx"
    response = requests.get(url)
    xls = pd.ExcelFile(BytesIO(response.content))
    all_data = pd.concat([xls.parse(sheet) for sheet in xls.sheet_names], ignore_index=True)
    return all_data

df = load_data()

# --- 2. Bersihkan kolom dan pastikan format ---
df = df.rename(columns=lambda x: x.strip())
df["Nama Diklat"] = df["Nama Diklat"].astype(str).str.strip()
df["Mata Ajar"] = df["Mata Ajar"].astype(str).str.strip()
df["Rata-Rata"] = pd.to_numeric(df["Nilai"], errors="coerce")

# --- 3. Buat 'Awalan' dari Nama Diklat (3 kata pertama) ---
def ambil_awalan(nama, n_kata=3):
    return " ".join(nama.split()[:n_kata]).lower()

df["Awalan"] = df["Nama Diklat"].apply(lambda x: ambil_awalan(x, n_kata=3))
awalan_counts = df["Awalan"].value_counts()

# --- 4. Gabungkan Nama Diklat Berdasarkan Awalan ---
def nama_diklat_gabungan(row):
    awalan = row["Awalan"]
    if awalan_counts[awalan] > 1:
        return awalan.title()
    else:
        return row["Nama Diklat"]

df["Nama Diklat Gabungan"] = df.apply(nama_diklat_gabungan, axis=1)

# --- 5. UI Dropdown ---
st.title("📊 Dashboard Instruktur Nilai Tertinggi")

pilihan_diklat = st.selectbox("📘 Pilih Nama Diklat", sorted(df["Nama Diklat Gabungan"].unique()))
filtered_diklat = df[df["Nama Diklat Gabungan"] == pilihan_diklat]

pilihan_mata_ajar = st.selectbox("📚 Pilih Mata Ajar", sorted(filtered_diklat["Mata Ajar"].unique()))
filtered_mata_ajar = filtered_diklat[filtered_diklat["Mata Ajar"] == pilihan_mata_ajar]

# --- 6. Ranking Instruktur berdasarkan rata-rata nilai ---
ranking = (
    filtered_mata_ajar.groupby("Nama Instruktur")["Nilai"]
    .mean()
    .reset_index()
    .sort_values(by="Nilai", ascending=False)
)

ranking.index = range(1, len(ranking) + 1)

st.markdown("### 🥇 Ranking Instruktur berdasarkan Nilai Rata-Rata")
st.dataframe(ranking, use_container_width=True)
