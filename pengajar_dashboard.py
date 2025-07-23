import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.title("📊 Dashboard Instruktur - Nilai Rata-Rata Tertinggi")

# === 1. Baca data dari file lokal/GitHub ===
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/AzrielAprieliant/dashboard-pengajar/main/Data%20Instruktur%20asli.xlsx"
    sheet_2025 = pd.read_excel(url, sheet_name="Penilaian Jan Jun 2025")
    sheet_2024 = pd.read_excel(url, sheet_name="Penilaian 2024")
    sheet_2023 = pd.read_excel(url, sheet_name="Penilaian 2023")

    sheet_2025["Tahun"] = 2025
    sheet_2024["Tahun"] = 2024
    sheet_2023["Tahun"] = 2023

    # Samakan nama kolom
    sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})

    df = pd.concat([sheet_2025, sheet_2024, sheet_2023], ignore_index=True)
    df = df.rename(columns={"Rata-Rata": "Nilai"})  # ⬅️ Ubah jadi 'Nilai'
    df["Nilai"] = pd.to_numeric(df["Nilai"], errors="coerce")
    return df

df = load_data()

# --- 2. Clustering Nama Diklat (berdasarkan awalan mirip) ---
def cluster_diklat(nama_diklat_list, threshold=85):
    clustered = {}
    for nama in nama_diklat_list:
        found = False
        for key in clustered:
            score = fuzz.token_sort_ratio(nama.lower(), key.lower())
            if score >= threshold:
                clustered[key].append(nama)
                found = True
                break
        if not found:
            clustered[nama] = [nama]
    # Balik ke mapping nama → cluster
    mapping = {}
    for key, values in clustered.items():
        for v in values:
            mapping[v] = key
    return mapping

# Apply clustering
unique_diklat = df["Nama Diklat"].dropna().unique().tolist()
mapping_diklat = cluster_diklat(unique_diklat)
df["Nama Diklat Gabungan"] = df["Nama Diklat"].map(mapping_diklat)

# === 3. Dropdown Diklat ===
selected_diklat = st.selectbox("Pilih Nama Diklat", sor_
