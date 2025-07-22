import pandas as pd
import streamlit as st
import re

# === SETUP TAMPILAN ===
st.set_page_config(page_title="Dashboard Pengajar", layout="centered")
st.title("📊 Pengajar dengan Nilai Tertinggi")

# === BACA DATA EXCEL ===
file = "Data Instruktur asli.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

# Gabung semua data
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# === BERSIHKAN DATA ===
all_data["Rata-Rata"] = pd.to_numeric(all_data["Rata-Rata"], errors="coerce")
for col in ["Instruktur", "Mata Ajar", "Nama Diklat"]:
    all_data[col] = all_data[col].astype(str).str.strip().str.replace("\xa0", " ", regex=False)

# === NORMALISASI KATEGORI DIKLAT ===
def bersihkan_nama_diklat(nama):
    nama = nama.upper().strip()
    nama = re.split(r'[-(]', nama)[0]
    nama = re.sub(r'\s+', ' ', nama)
    return nama.strip()

all_data["Kategori Diklat"] = all_data["Nama Diklat"].apply(bersihkan_nama_diklat)

# === DROPDOWN: KATEGORI DIKLAT ===
unique_kategori = sorted(all_data["Kategori Diklat"].dropna().unique())
col1, col2 = st.columns([1, 1])

with col1:
    kategori_diklat = st.selectbox("📚 Pilih Kategori Diklat", options=unique_kategori)

filtered_kategori = all_data[all_data["Kategori Diklat"] == kategori_diklat]

# === DROPDOWN: MATA AJAR ===
unique_mata_ajar = sorted(filtered_kategori["Mata Ajar"].dropna().unique())
with col2:
    mata_ajar = st.selectbox("🧠 Pilih Mata Ajar", options=unique_mata_ajar)

filtered = filtered_kategori[filtered_kategori["Mata Ajar"] == mata_ajar]

# === HITUNG RATA-RATA PER INSTRUKTUR PER TAHUN ===
pivot = filtered.groupby(["Tahun", "Instruktur"])["Rata-Rata"].mean().reset_index()
pivot = pivot.dropna(subset=["Rata-Rata"])

pivot_sorted = pivot.sort_values(by=["Tahun", "Rata-Rata"], ascending=[False, False]).reset_index(drop=True)
pivot_sorted["Rank"] = pivot_sorted.groupby("Tahun")["Rata-Rata"].rank(method="first", ascending=False).fillna(0).astype(int)
pivot_sorted = pivot_sorted.rename(columns={"Rata-Rata": "Nilai"})

# === TAMPILKAN TABEL ===
st.markdown(f"### 📈 Hasil untuk:\n**Kategori Diklat:** _{kategori_diklat}_  \n**Mata Ajar:** _{mata_ajar}_")
st.dataframe(
    pivot_sorted[["Tahun", "Rank", "Instruktur", "Nilai"]],
    use_container_width=True
)
