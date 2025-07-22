import pandas as pd
import streamlit as st
import re
from difflib import get_close_matches

st.set_page_config(page_title="📚 Pengelompokan Nama Diklat", layout="wide")
st.title("📚 Pengelompokan Nama Diklat Otomatis")

file = "Data Instruktur asli.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

df = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
], ignore_index=True)

df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")

for col in ["Instruktur", "Mata Ajar", "Nama Diklat"]:
    df[col] = df[col].astype(str).str.strip().str.replace("\xa0", " ", regex=False)

# === Ambil 'base title' dari diklat ===
def ambil_awalan_kalimat(nama, n_kata=4):
    # Ambil n kata pertama dari judul
    return ' '.join(nama.split()[:n_kata]).strip()

df["Kelompok_Diklat"] = df["Nama Diklat"].apply(lambda x: ambil_awalan_kalimat(x, n_kata=3))

# Gunakan kemiripan teks untuk gabung kelompok serupa
kelompok_unik = df["Kelompok_Diklat"].unique()
kelompok_map = {}

for nama in kelompok_unik:
    match = get_close_matches(nama, kelompok_map.keys(), n=1, cutoff=0.85)
    if match:
        kelompok_map[nama] = match[0]
    else:
        kelompok_map[nama] = nama

df["Kelompok_Diklat"] = df["Kelompok_Diklat"].map(kelompok_map)

# === Dropdown filter ===
list_kelompok = sorted(df["Kelompok_Diklat"].dropna().unique())
kelompok_terpilih = st.selectbox("🗂️ Pilih Kelompok Diklat", list_kelompok)

filtered = df[df["Kelompok_Diklat"] == kelompok_terpilih]

st.markdown(f"### 📋 Daftar Diklat dalam Kelompok: _{kelompok_terpilih}_")
st.dataframe(
    filtered[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
    .sort_values(by=["Tahun", "Rata-Rata"], ascending=[False, False]),
    use_container_width=True
)
