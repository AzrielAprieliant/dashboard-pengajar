import pandas as pd
import streamlit as st

# === SETUP TAMPILAN LEBIH KECIL ===
st.set_page_config(page_title="Dashboard Pengajar", layout="centered")
st.title("📊 Pengajar dengan Nilai Tertinggi")

# === BACA DATA EXCEL ===
file = "Data Instruktur.xlsx"

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

# === DROPDOWN 1: Nama Diklat ===
unique_diklat = sorted(all_data["Nama Diklat"].dropna().unique())

col1, col2 = st.columns([1, 1])
with col1:
    nama_diklat = st.selectbox(
        "📚 Pilih Nama Diklat",
        options=unique_diklat,
        key="select_diklat"
    )

filtered_diklat = all_data[all_data["Nama Diklat"] == nama_diklat]

# === DROPDOWN 2: Mata Ajar ===
filtered_mata_ajar = sorted(filtered_diklat["Mata Ajar"].dropna().unique())
with col2:
    mata_ajar = st.selectbox(
        "🧠 Pilih Mata Ajar",
        options=filtered_mata_ajar,
        key="select_mata_ajar"
    )

# === FILTER AKHIR ===
filtered = filtered_diklat[filtered_diklat["Mata Ajar"] == mata_ajar]

# === HITUNG RATA-RATA PER INSTRUKTUR PER TAHUN ===
pivot = filtered.groupby(["Tahun", "Instruktur"])["Rata-Rata"].mean().reset_index()
pivot = pivot.dropna(subset=["Rata-Rata"])

pivot_sorted = pivot.sort_values(by=["Tahun", "Rata-Rata"], ascending=[False, False]).reset_index(drop=True)
pivot_sorted["Rank"] = pivot_sorted.groupby("Tahun")["Rata-Rata"].rank(method="first", ascending=False).fillna(0).astype(int)

# === GANTI NAMA KOLOM & TAMPILKAN ===
pivot_sorted = pivot_sorted.rename(columns={"Rata-Rata": "Nilai"})

st.markdown(f"### 📈 Hasil untuk:\n**Nama Diklat:** _{nama_diklat}_  \n**Mata Ajar:** _{mata_ajar}_")
st.dataframe(
    pivot_sorted[["Tahun", "Rank", "Instruktur", "Nilai"]],
    use_container_width=True
)
