import pandas as pd
import streamlit as st

st.title("📊 Pengajar dengan Nilai Tertinggi")

# === BACA FILE EXCEL ===
file = "Data Instruktur asli.xlsx"
# Sheet per tahun
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

# Gabung semua sheet
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Bersihkan dan pastikan numeric
all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# === CLUSTER DIKLAT ===
def get_awalan_diklat(nama, n_kata=3):
    return " ".join(str(nama).split()[:n_kata]).lower().strip()

all_data["Cluster Diklat"] = all_data["Nama Diklat"].apply(get_awalan_diklat)

# === DROPDOWN 1: Cluster Diklat ===
cluster_selected = st.selectbox("Pilih Nama Diklat", sorted(all_data['Cluster Diklat'].dropna().unique()))

filtered_cluster = all_data[all_data["Nama Diklat"] == cluster_selected]

# === DROPDOWN 2: Mata Ajar ===
mata_ajar = st.selectbox("Pilih Mata Ajar", sorted(filtered_cluster['Mata Ajar'].dropna().unique()))
filtered = filtered_cluster[filtered_cluster['Mata Ajar'] == mata_ajar]

# === RANKING INSTRUKTUR ===
pivot = filtered.groupby(['Tahun', 'Instruktur'])['Rata-Rata'].mean().reset_index()
pivot = pivot.dropna(subset=['Rata-Rata'])
pivot = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False])
pivot['Rank'] = pivot.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)
pivot = pivot.rename(columns={'Rata-Rata': 'Nilai'})

# === TAMPILKAN HASIL ===
st.write(f"📘 Menampilkan instruktur untuk cluster diklat: **{cluster_selected}** dan mata ajar: **{mata_ajar}**")
st.dataframe(pivot[['Tahun', 'Rank', 'Instruktur', 'Nilai']])
