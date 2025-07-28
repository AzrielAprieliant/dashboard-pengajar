import streamlit as st
import pandas as pd
import os
from rapidfuzz import fuzz

# --- Judul App ---
st.title("📊 Dashboard Penilaian Instruktur")

# --- Cek file ada atau tidak ---
file_path = "data instruktur asli.xlsx"

if not os.path.exists(file_path):
    st.error(f"File '{file_path}' tidak ditemukan. Pastikan file ada di direktori yang sama dengan script.")
    st.stop()

# --- Baca semua sheet ---
all_sheets = pd.read_excel(file_path, sheet_name=None)
data = pd.concat(all_sheets.values(), ignore_index=True)

# --- Cek kolom penting ---
if 'Nama Diklat' not in data.columns or 'Mata Ajar' not in data.columns or 'Rata-Rata' not in data.columns:
    st.error("Kolom 'Nama Diklat', 'Mata Ajar', atau 'Rata-Rata' tidak ditemukan.")
    st.stop()

# --- Bersihkan data ---
data.dropna(subset=['Nama Diklat', 'Mata Ajar', 'Rata-Rata'], inplace=True)

# --- Kelompokkan nama diklat berdasarkan kemiripan string (RapidFuzz) ---
grouped_diklat = {}
threshold = 85  # tingkat kemiripan minimum

for diklat in data['Nama Diklat'].unique():
    found = False
    for group in grouped_diklat:
        if fuzz.token_sort_ratio(diklat, group) >= threshold:
            grouped_diklat[group].append(diklat)
            found = True
            break
    if not found:
        grouped_diklat[diklat] = [diklat]

# --- Dropdown pilih grup diklat ---
selected_diklat_group = st.selectbox("📌 Pilih Nama Diklat", list(grouped_diklat.keys()))
selected_diklat_names = grouped_diklat[selected_diklat_group]

# --- Filter data berdasarkan pilihan diklat ---
filtered_data = data[data['Nama Diklat'].isin(selected_diklat_names)]

# --- Dropdown mata ajar ---
mata_ajar_options = filtered_data['Mata Ajar'].unique()
selected_mata_ajar = st.selectbox("📘 Pilih Mata Ajar", mata_ajar_options)

# --- Tampilkan data sesuai pilihan ---
final_data = filtered_data[filtered_data['Mata Ajar'] == selected_mata_ajar]
final_data_sorted = final_data.sort_values(by='Rata-Rata', ascending=False)

# --- Tampilkan tabel dan ranking ---
st.subheader("🏆 Ranking Instruktur")
st.dataframe(final_data_sorted[['Nama Instruktur', 'Rata-Rata']].reset_index(drop=True))
