import pandas as pd
import streamlit as st

st.title("Pengajar dengan Nilai Tertinggi")

# === 1. Baca data dari file Excel ===
file = "Data Instruktur.xlsx"

# Baca setiap sheet & tambahkan kolom Tahun
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

# === 2. Gabungkan semua sheet jadi satu dataframe ===
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Pastikan kolom Rata-Rata numeric (kalau ada string kosong atau "-", jadi NaN)
all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# === 3. Dropdown Nama Diklat ===
nama_diklat = st.selectbox("Pilih Nama Diklat", sorted(all_data['Nama Diklat'].dropna().unique()))

# Filter dulu berdasarkan diklat yang dipilih
filtered_diklat = all_data[all_data['Nama Diklat'] == nama_diklat]

# === 4. Dropdown Mata Ajar ===
mata_ajar = st.selectbox("Pilih Mata Ajar", sorted(filtered_diklat['Mata Ajar'].dropna().unique()))

# Filter lagi berdasarkan mata ajar
filtered = filtered_diklat[filtered_diklat['Mata Ajar'] == mata_ajar]

# === 5. Hitung rata-rata per instruktur per tahun ===
pivot = filtered.groupby(['Tahun', 'Instruktur'])['Rata-Rata'].mean().reset_index()

# Buang NaN sebelum ranking
pivot = pivot.dropna(subset=['Rata-Rata'])

# Urutkan supaya rapi (tahun terbaru dulu)
pivot_sorted = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False]).reset_index(drop=True)

# Tambahkan kolom Rank per Tahun
pivot_sorted['Rank'] = pivot_sorted.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).fillna(0).astype(int)

# Ganti nama kolom jadi 'Rata-Rata' jadi 'nilai'
pivot_sorted = pivot_sorted.rename(columns={'Rata-Rata : 'Nilai})

# === 6. Tampilkan hasil ===
st.write(f"Pengajar dengan nilai rata-rata tertinggi untuk Diklat: **{nama_diklat}**, Mata Ajar: **{mata_ajar}**")
st.dataframe(pivot_sorted[['Tahun', 'Rank', 'Instruktur', 'Nilai']])
