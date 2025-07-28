import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import os

st.set_page_config(page_title="Dashboard Pengajar", layout="wide")

st.title("📊 Dashboard Penilaian Instruktur")
file_path = "data instruktur asli.xlsx"

# Cek apakah file ada
if not os.path.exists(file_path):
    st.error("❌ File 'data instruktur asli.xlsx' tidak ditemukan.")
    st.stop()

# Baca semua sheet Excel
sheets = pd.read_excel(file_path, sheet_name=None)
df = pd.concat(sheets.values(), ignore_index=True)

# Cek kolom penting
required_columns = ['Nama Diklat', 'Mata Ajar', 'Rata-Rata', 'Nama Instruktur']
if not all(col in df.columns for col in required_columns):
    st.error("❌ Kolom yang dibutuhkan tidak ditemukan di file Excel.")
    st.stop()

# Bersihkan data
df.dropna(subset=['Nama Diklat', 'Mata Ajar', 'Rata-Rata', 'Nama Instruktur'], inplace=True)
df['Rata-Rata'] = pd.to_numeric(df['Rata-Rata'], errors='coerce')

# Kelompokkan Nama Diklat berdasarkan kemiripan
grouped_diklat = {}
threshold = 85

for diklat in df['Nama Diklat'].unique():
    found = False
    for key in grouped_diklat:
        if fuzz.token_sort_ratio(diklat, key) >= threshold:
            grouped_diklat[key].append(diklat)
            found = True
            break
    if not found:
        grouped_diklat[diklat] = [diklat]

# Dropdown diklat
selected_group = st.selectbox("📌 Pilih Nama Diklat", list(grouped_diklat.keys()))
filtered_df = df[df['Nama Diklat'].isin(grouped_diklat[selected_group])]

# Dropdown mata ajar
selected_mata_ajar = st.selectbox("📘 Pilih Mata Ajar", filtered_df['Mata Ajar'].unique())

# Tampilkan tabel ranking
result = filtered_df[filtered_df['Mata Ajar'] == selected_mata_ajar]
result_sorted = result.sort_values(by='Rata-Rata', ascending=False)

st.subheader("🏅 Ranking Instruktur")
st.dataframe(result_sorted[['Nama Instruktur', 'Rata-Rata']].reset_index(drop=True))
