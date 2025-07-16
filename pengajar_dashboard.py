import pandas as pd
import streamlit as st

st.title("Dashboard Pengajar dengan Nilai Tertinggi")

file = "Data Instruktur.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
# kalau kolomnya misalnya 'Diklat', rename:
sheet_2025 = sheet_2025.rename(columns={"Diklat": "Nama Diklat"})
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024 = sheet_2024.rename(columns={"Diklat": "Nama Diklat"})
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata", "Nama diklat": "Nama Diklat"})
sheet_2023['Tahun'] = 2023

# Gabungkan
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Dropdown Mata Ajar
mata_ajar = st.selectbox("Pilih Mata Ajar", sorted(all_data['Mata Ajar'].dropna().unique()))

# Filter dan hitung
filtered = all_data[all_data['Mata Ajar'] == mata_ajar].copy()
filtered['Rata-Rata'] = pd.to_numeric(filtered['Rata-Rata'], errors='coerce')

pivot = filtered.groupby(['Tahun', 'Nama Diklat', 'Instruktur'])['Rata-Rata'].mean().reset_index()
pivot_sorted = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False]).reset_index(drop=True)
pivot_sorted['Rank'] = pivot_sorted.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)

st.write(f"Pengajar dengan nilai rata-rata tertinggi untuk mata ajar: {mata_ajar}")
st.dataframe(pivot_sorted[['Tahun', 'Rank', 'Nama Diklat', 'Instruktur', 'Rata-Rata']])
