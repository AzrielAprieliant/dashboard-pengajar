import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title("Dashboard Pengajar dengan Nilai Tertinggi (Pilih Tahun & Mata Ajar)")

file = "Data Instruktur.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

# Gabung semua data
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Pastikan numeric
all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# Dropdown pilih mata ajar
mata_ajar = st.selectbox("Pilih Mata Ajar", sorted(all_data['Mata Ajar'].dropna().unique()))

# Dropdown pilih tahun
tahun = st.selectbox("Pilih Tahun", sorted(all_data['Tahun'].unique(), reverse=True))

# Filter data sesuai pilihan
filtered = all_data[(all_data['Mata Ajar'] == mata_ajar) & (all_data['Tahun'] == tahun)]

# Hitung rata-rata per instruktur (meskipun datanya biasanya udah rata-rata)
pivot = filtered.groupby('Instruktur')['Rata-Rata'].mean().reset_index()

# Buang NaN
pivot = pivot.dropna(subset=['Rata-Rata'])

# Rank
pivot['Rank'] = pivot['Rata-Rata'].rank(method='first', ascending=False).astype(int)

# Urutkan Rank
pivot_sorted = pivot.sort_values('Rank')

# Tampilkan tabel
st.write(f"Nilai rata-rata pengajar untuk mata ajar: **{mata_ajar}** di tahun **{tahun}**")
st.dataframe(pivot_sorted)

# Grafik: Top 10 pengajar
top10 = pivot_sorted.head(10)

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(top10['Instruktur'], top10['Rata-Rata'], color='skyblue')
ax.set_xlabel("Rata-Rata")
ax.set_ylabel("Instruktur")
ax.set_title(f"Top 10 Nilai Rata-Rata Pengajar - {mata_ajar} ({tahun})")
ax.invert_yaxis()  # supaya ranking paling tinggi di atas

st.pyplot(fig)
