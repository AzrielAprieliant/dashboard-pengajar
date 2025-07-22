import pandas as pd
import streamlit as st

st.set_page_config(page_title="Kelompok Diklat", layout="wide")
st.title("📚 Pengelompokan Nama Diklat Otomatis")

# BACA DATA
file = "Output_Kelompok_Diklat.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

# Gabung semua sheet
data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# BERSIHKAN
for col in ["Instruktur", "Mata Ajar", "Nama Diklat"]:
    data[col] = data[col].astype(str).str.strip().str.replace("\xa0", " ", regex=False)
data["Rata-Rata"] = pd.to_numeric(data["Rata-Rata"], errors="coerce")

# BUAT KOLOM NAMA KELOMPOK DARI AWAL KATA
data["Kelompok Diklat"] = data["Nama Diklat"].str.extract(r"^([A-Za-z\s]+)", expand=False).str.strip()

# DROPDOWN PILIH KELOMPOK DIKLAT
kelompok_opsi = sorted(data["Kelompok Diklat"].dropna().unique())
pilihan_kelompok = st.selectbox("🔍 Pilih Kelompok Nama Diklat", options=kelompok_opsi)

# FILTER BERDASARKAN KELOMPOK YANG DIPILIH
filtered = data[data["Kelompok Diklat"] == pilihan_kelompok]

# TAMPILKAN DATA
st.markdown(f"### 📊 Hasil Kelompok: _{pilihan_kelompok}_")
st.dataframe(
    filtered[["Tahun", "Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata"]],
    use_container_width=True
)
