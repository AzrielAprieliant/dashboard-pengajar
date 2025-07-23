import pandas as pd
import streamlit as st
from rapidfuzz import process, fuzz

st.title("📊 Dashboard Instruktur Nilai Tertinggi")

# === 1. Baca data dari file lokal ===
file = "Data Instruktur asli.xlsx"

# Baca setiap sheet & tambahkan kolom Tahun
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

# Pastikan kolom Rata-Rata numeric
all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# === 2. Clustering Nama Diklat pakai RapidFuzz ===
def cluster_diklat(diklat_list, threshold=85):
    clusters = {}
    for diklat in diklat_list:
        found = None
        for label in clusters:
            if fuzz.token_sort_ratio(diklat, label) >= threshold:
                found = label
                break
        if found:
            clusters[found].append(diklat)
        else:
            clusters[diklat] = [diklat]
    return clusters

# Ambil daftar diklat unik
unique_diklat = all_data["Nama Diklat"].dropna().unique().tolist()
cluster_result = cluster_diklat(unique_diklat)

# Mapping nama diklat asli ke cluster
map_diklat = {}
for group_name, variants in cluster_result.items():
    for var in variants:
        map_diklat[var] = group_name

# Tambahkan kolom gabungan
all_data["Nama Diklat Gabungan"] = all_data["Nama Diklat"].map(map_diklat)

# === 3. Dropdown Nama Diklat ===
nama_diklat = st.selectbox("Pilih Nama Diklat", sorted(all_data["Nama Diklat Gabungan"].dropna().unique()))

# Filter berdasarkan diklat
filtered_diklat = all_data[all_data["Nama Diklat Gabungan"] == nama_diklat]

# === 4. Dropdown Mata Ajar ===
mata_ajar = st.selectbox("Pilih Mata Ajar", sorted(filtered_diklat['Mata Ajar'].dropna().unique()))

# Filter berdasarkan mata ajar
filtered = filtered_diklat[filtered_diklat['Mata Ajar'] == mata_ajar]

# === 5. Hitung rata-rata dan ranking ===
pivot = (
    filtered.groupby(['Tahun', 'Instruktur'])['Rata-Rata']
    .mean()
    .reset_index()
    .dropna()
)

pivot = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False])
pivot['Rank'] = pivot.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)
pivot = pivot.rename(columns={'Rata-Rata': 'Nilai'})

# === 6. Tampilkan hasil ===
st.write(f"Pengajar dengan nilai rata-rata tertinggi untuk Diklat: **{nama_diklat}**, Mata Ajar: **{mata_ajar}**")
st.dataframe(pivot[['Tahun', 'Rank', 'Instruktur', 'Nilai']])
