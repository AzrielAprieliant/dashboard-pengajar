import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title("Dashboard Pengajar dengan Nilai Tertinggi (Dengan Tahun)")

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

# Pastikan Rata-Rata numeric
all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# Filter sesuai mata ajar
filtered = all_data[all_data['Mata Ajar'] == mata_ajar]

# Hitung rata-rata per instruktur & tahun
pivot = filtered.groupby(['Tahun', 'Instruktur'])['Rata-Rata'].mean().reset_index()

# Buang baris yang Rata-Rata NaN sebelum ranking
pivot = pivot.dropna(subset=['Rata-Rata'])

# Tambahkan kolom Rank per tahun
pivot['Rank'] = pivot.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)

# Tampilkan tabel
st.write(f"Nilai rata-rata pengajar untuk mata ajar: {mata_ajar} (semua tahun)")
st.dataframe(pivot.sort_values(['Tahun', 'Rank']))

# Grafik: nilai tertinggi per tahun
pivot_max = pivot.groupby('Tahun')['Rata-Rata'].max().reset_index()

fig, ax = plt.subplots()
ax.plot(pivot_max['Tahun'], pivot_max['Rata-Rata'], marker='o', color='skyblue')
ax.set_title(f"Nilai Tertinggi per Tahun untuk {mata_ajar}")
ax.set_xlabel("Tahun")
ax.set_ylabel("Nilai Tertinggi")
ax.grid(True)

st.pyplot(fig)
