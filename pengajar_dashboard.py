import pandas as pd
import streamlit as st

st.title("Dashboard Pengajar dengan Nilai Tertinggi (dengan Nama Diklat)")

# Baca file
file = "Data Instruktur.xlsx"

# Baca sheet dan tambahkan kolom Tahun
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

# Gabungkan semua data
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Pilih Mata Ajar
mata_ajar = st.selectbox("Pilih Mata Ajar", sorted(all_data['Mata Ajar'].dropna().unique()))

# Filter data sesuai pilihan Mata Ajar
filtered = all_data[all_data['Mata Ajar'] == mata_ajar].copy()
filtered['Rata-Rata'] = pd.to_numeric(filtered['Rata-Rata'], errors='coerce')

# Hitung rata-rata nilai per instruktur, nama diklat, dan tahun
pivot = filtered.groupby(['Tahun', 'Nama Diklat', 'Instruktur'])['Rata-Rata'].mean().reset_index()

# Urutkan dari yang tertinggi
pivot_sorted = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False]).reset_index(drop=True)

# Tambahkan kolom Rank per Tahun
pivot_sorted['Rank'] = pivot_sorted.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)

# Tampilkan
st.write(f"Pengajar dengan nilai rata-rata tertinggi untuk mata ajar: {mata_ajar}")
st.dataframe(pivot_sorted[['Tahun', 'Rank', 'Nama Diklat', 'Instruktur', 'Rata-Rata']])



