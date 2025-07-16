import pandas as pd
import streamlit as st

st.title("Dashboard Pengajar dengan Nilai Tertinggi")

file = "Data Instruktur.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Rata-Rata", "Tahun"]]
], ignore_index=True)

mata_ajar = st.selectbox("Pilih Mata Ajar", all_data['Mata Ajar'].unique())
tahun = st.selectbox("Pilih Tahun", sorted(all_data['Tahun'].unique(), reverse=True))

filtered = all_data[(all_data['Mata Ajar'] == mata_ajar) & (all_data['Tahun'] == tahun)]
filtered['Rata-Rata'] = pd.to_numeric(filtered['Rata-Rata'], errors='coerce')

pivot = filtered.groupby('Instruktur')['Rata-Rata'].mean().reset_index()
pivot_sorted = pivot.sort_values(by='Rata-Rata', ascending=False).reset_index(drop=True)
pivot_sorted.insert(0, 'Rank', range(1, len(pivot_sorted) + 1))

st.write(f"Pengajar dengan nilai rata-rata tertinggi untuk mata ajar: {mata_ajar} pada tahun: {tahun}")
st.dataframe(pivot_sorted)
