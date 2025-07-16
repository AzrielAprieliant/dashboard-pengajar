import pandas as pd
import streamlit as st

st.title("Dashboard Pengajar dengan Nilai Tertinggi ")

# Baca file Excel
file = "Data Instruktur.xlsx"

# Baca per sheet + tambahkan kolom Tahun
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

# Gabung data
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Pastikan Rata-Rata numeric
all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# Dropdown hanya untuk Mata Ajar
mata_ajar = st.selectbox("Pilih Mata Ajar", all_data['Mata Ajar'].dropna().unique())

# Filter data sesuai pilihan
filtered = all_data[all_data['Mata Ajar'] == mata_ajar]

# Buang data yang NaN di Rata-Rata (biar aman)
filtered = filtered.dropna(subset=['Rata-Rata'])

# Hitung rata-rata per instruktur per tahun
pivot = filtered.groupby(['Tahun', 'Instruktur'])['Rata-Rata'].mean().reset_index()

# Urutkan
pivot_sorted = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False]).reset_index(drop=True)

# Tambah kolom Rank per Tahun
pivot_sorted['Rank'] = pivot_sorted.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False)
pivot_sorted['Rank'] = pivot_sorted['Rank'].fillna(0).astype(int)

# Urutkan ulang agar rank naik
pivot_sorted = pivot_sorted.sort_values(by=['Tahun', 'Rank'])

# Tampilkan
st.write(f"Pengajar dengan nilai rata-rata tertinggi untuk mata ajar: **{mata_ajar}** (Semua Tahun)")
st.dataframe(pivot_sorted[['Tahun', 'Rank', 'Instruktur', 'Rata-Rata']])


