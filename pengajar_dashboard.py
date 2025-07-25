import pandas as pd
import streamlit as st
from sklearn.cluster import DBSCAN
import numpy as np

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

# === 2. Clustering Nama Diklat pakai Embedding ===
unique_diklat = all_data ["Nama Diklat"].dropna().unique().tolist()

# Load Model embedding
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
embeddings = model.encode(unique_dilat)

# DBSCAN clustering
clustering = DBSCAN(eps=1.0, min_samples=2, metric='cosine').fit(embeddings)
labels = clustering.labels_

# Buat mapping nama diklat ke cluster label
cluster_map = {}
for label in set(labels):
    if label == -1:
        continue
    indexes = np.where(labels == label)[0]
    cluster_name = unique_diklat[indexes[0]]
    for i in indexes:
        cluster_map [unique_diklat[i]] = cluster_name

# Diklat yang tidak termasuk cluster tetap pakai nama asli
for i, nama in enumerate(unique_diklat):
    if nama not in cluster_map:
        cluster_map[nama] = nama

# Tambahkan ke data
all_data["Nama Diklat Gabungan"] = all_data["Nama Diklat"].map(cluster_map)

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
