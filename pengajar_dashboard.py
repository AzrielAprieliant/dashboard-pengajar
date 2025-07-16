import pandas as pd
import streamlit as st

# Judul dashboard
st.title("Dashboard Pengajar dengan Nilai Tertinggi")

# Load data dari file Excel
file = "Data Instruktur.xlsx"

# Baca semua sheet
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")

# Samakan nama kolom di sheet 2023
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})

# Gabungkan semua data
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Rata-Rata"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Rata-Rata"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Rata-Rata"]]
], ignore_index=True)

# Dropdown pilih Mata Ajar
mata_ajar = st.selectbox("Pilih Mata Ajar", all_data['Mata Ajar'].unique())

# Filter data sesuai pilihan
filtered = all_data[all_data['Mata Ajar'] == mata_ajar]

# Pastikan kolom Rata-Rata bertipe numeric
filtered['Rata-Rata'] = pd.to_numeric(filtered['Rata-Rata'], errors='coerce')

# Hitung rata-rata per instruktur & urutkan
pivot = filtered.groupby('Instruktur')['Rata-Rata'].mean().reset_index()
pivot_sorted = pivot.sort_values(by='Rata-Rata', ascending=False).reset_index(drop=True)

# Tambahkan kolom Rank
pivot_sorted.insert(0, 'Rank', range(1, len(pivot_sorted) + 1))

# Tampilkan hasil
st.write(f"Pengajar dengan nilai rata-rata tertinggi untuk mata ajar: {mata_ajar}")
st.dataframe(pivot_sorted)
