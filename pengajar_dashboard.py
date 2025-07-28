import streamlit as st
import pandas as pd
import os
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Dashboard Instruktur", layout="wide")

# --- Judul ---
st.title("📊 Dashboard Penilaian Instruktur")

# --- Cek file ---
file_path = "data instruktur asli.xlsx"
if not os.path.exists(file_path):
    st.error(f"File '{file_path}' tidak ditemukan. Harap unggah file dengan nama tersebut.")
    st.stop()

# --- Baca semua sheet ---
all_sheets = pd.read_excel(file_path, sheet_name=None)
data = pd.concat(all_sheets.values(), ignore_index=True)

# --- Bersihkan data ---
data = data.rename(columns=lambda x: x.strip())
if 'Nama Diklat' not in data.columns or 'Mata Ajar' not in data.columns or 'Rata-Rata' not in data.columns:
    st.error("File harus memiliki kolom: 'Nama Diklat', 'Mata Ajar', dan 'Rata-Rata'")
    st.stop()

# --- Kelompokkan Nama Diklat mirip ---
diklat_names = data['Nama Diklat'].dropna().unique().tolist()
grouped_diklat = {}

for name in diklat_names:
    found = False
    for group in grouped_diklat:
        if fuzz.partial_ratio(name.lower(), group.lower()) > 85:
            grouped_diklat[group].append(name)
            found = True
            break
    if not found:
        grouped_diklat[name] = [name]
        
# --- Pilih nama diklat terkelompok ---
selected_diklat_group = st.selectbox("📌 Pilih Nama Diklat", list(grouped_diklat.keys()))
selected_diklat_names = grouped_diklat[selected_diklat_group]

# --- Filter data ---
filtered_data = data[data['Nama Diklat'].isin(selected_diklat_names)]

# --- Pilih mata ajar ---
available_mata_ajar = filtered_data['Mata Ajar'].dropna().unique()
selected_mata_ajar = st.selectbox("📚 Pilih Mata Ajar", available_mata_ajar)

# --- Tampilkan data nilai ---
nilai_data = filtered_data[filtered_data['Mata Ajar'] == selected_mata_ajar]
nilai_data = nilai_data.sort_values(by='Rata-Rata', ascending=False)

st.subheader("📈 Tabel Nilai Instruktur")
st.dataframe(nilai_data[['Nama Diklat', 'Mata Ajar', 'Rata-Rata']].reset_index(drop=True))

# --- Tampilkan ranking ---
st.subheader("🏅 Ranking Instruktur (berdasarkan Rata-Rata)")
for idx, row in nilai_data.iterrows():
    st.markdown(f"**{idx+1}. {row['Nama Diklat']}** - Rata-Rata: {row['Rata-Rata']}")
