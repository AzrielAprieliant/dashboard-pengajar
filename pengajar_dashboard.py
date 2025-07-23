import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

st.set_page_config(page_title="Dashboard Instruktur", layout="wide")
st.title("📊 Dashboard Instruktur Nilai Tertinggi")

# ===== 1. Baca semua sheet Excel =====
file = "Data Instruktur asli.xlsx"  # Ganti jika pakai URL GitHub raw

@st.cache_data
def load_data(file):
    sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
    sheet_2025['Tahun'] = 2025

    sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
    sheet_2024['Tahun'] = 2024

    sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
    sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
    sheet_2023['Tahun'] = 2023

    data = pd.concat([
        sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
        sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
        sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
    ], ignore_index=True)

    data['Rata-Rata'] = pd.to_numeric(data['Rata-Rata'], errors='coerce')
    return data

all_data = load_data(file)

# ===== 2. Fuzzy Clustering Nama Diklat =====
@st.cache_data
def fuzzy_cluster_diklat(df, threshold=85):
    unique_names = sorted(df["Nama Diklat"].dropna().unique())
    clustered = []
    used = set()

    for nama in unique_names:
        if nama in used:
            continue
        group = [nama]
        used.add(nama)
        for other in unique_names:
            if other in used:
                continue
            if fuzz.token_sort_ratio(nama, other) >= threshold:
                group.append(other)
                used.add(other)
        clustered.append(group)

    cluster_map = {}
    for group in clustered:
        cluster_name = group[0]  # Bisa juga ambil awalan saja
        for nama in group:
            cluster_map[nama] = cluster_name

    return df["Nama Diklat"].map(cluster_map)

all_data["Nama Diklat Gabungan"] = fuzzy_cluster_diklat(all_data)

# ===== 3. Dropdown Pilih Diklat Gabungan =====
selected_diklat = st.selectbox("Pilih Nama Diklat", sorted(all_data["Nama Diklat Gabungan"].unique()))

filtered_diklat = all_data[all_data["Nama Diklat Gabungan"] == selected_diklat]

# ===== 4. Dropdown Pilih Mata Ajar =====
selected_mata_ajar = st.selectbox("Pilih Mata Ajar", sorted(filtered_diklat["Mata Ajar"].dropna().unique()))

filtered = filtered_diklat[filtered_diklat["Mata Ajar"] == selected_mata_ajar]

# ===== 5. Ranking Instruktur =====
pivot = filtered.groupby(['Tahun', 'Instruktur'])['Rata-Rata'].mean().reset_index()
pivot = pivot.dropna(subset=['Rata-Rata'])
pivot_sorted = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False]).reset_index(drop=True)
pivot_sorted['Rank'] = pivot_sorted.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)
pivot_sorted = pivot_sorted.rename(columns={'Rata-Rata': 'Nilai'})

# ===== 6. Tampilkan Hasil =====
st.markdown(f"### 📘 Hasil untuk Diklat: **{selected_diklat}**, Mata Ajar: **{selected_mata_ajar}**")
st.dataframe(pivot_sorted[['Tahun', 'Rank', 'Instruktur', 'Nilai']], use_container_width=True)
