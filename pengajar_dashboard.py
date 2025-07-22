import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="📚 Pengelompokan Nama Diklat", layout="wide")
st.title("📚 Pengelompokan Nama Diklat Otomatis")

# === BACA FILE EXCEL ===
file = "Data Instruktur asli.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

# === GABUNGKAN SEMUA ===
df = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
], ignore_index=True)

# === BERSIHKAN ===
df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")
for col in ["Instruktur", "Mata Ajar", "Nama Diklat"]:
    df[col] = df[col].astype(str).str.strip().str.replace("\xa0", " ", regex=False)

# === BUAT KOLOM 'Kelompok Diklat' OTOMATIS ===
def ambil_kelompok(nama):
    if "-" in nama:
        return nama.split("-")[0].strip()
    else:
        return nama.strip()

df["Kelompok Diklat"] = df["Nama Diklat"].apply(ambil_kelompok)

# === DROPDOWN: Pilih Kelompok Diklat ===
list_kelompok = sorted(df["Kelompok Diklat"].dropna().unique())

kelompok_terpilih = st.selectbox("🗂️ Pilih Kelompok Diklat", list_kelompok)

# === FILTER DATA ===
filtered = df[df["Kelompok Diklat"] == kelompok_terpilih]

# === TAMPILKAN ===
st.markdown(f"### 📋 Daftar Diklat dalam Kelompok: _{kelompok_terpilih}_")
st.dataframe(
    filtered.sort_values(by=["Tahun", "Rata-Rata"], ascending=[False, False]),
    use_container_width=True
)
