import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard Pengajar", layout="centered")
st.title("📊 Pengajar dengan Nilai Tertinggi")

# === BACA DATA ===
file = "Data Instruktur asli.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

# === GABUNG DATA ===
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
], ignore_index=True)

# === BERSIHKAN ===
all_data["Rata-Rata"] = pd.to_numeric(all_data["Rata-Rata"], errors="coerce")
for col in ["Instruktur", "Mata Ajar", "Nama Diklat"]:
    all_data[col] = all_data[col].astype(str).str.strip().str.replace("\xa0", " ", regex=False)

# === TAMBAHKAN KATEGORI DIKLAT (Bagian depan sebelum "di", "pada", "untuk", dll) ===
import re
def ekstrak_kategori(nama):
    # Potong sebelum kata pemisah
    match = re.split(r"\s+(di|pada|untuk|dalam|bagi|kepada)\s+", nama, maxsplit=1, flags=re.IGNORECASE)
    return match[0].strip() if match else nama.strip()

all_data["Kategori Diklat"] = all_data["Nama Diklat"].apply(ekstrak_kategori)

# === DROPDOWN 1: PILIH KATEGORI DIKLAT ===
kategori_list = sorted(all_data["Kategori Diklat"].dropna().unique())
kategori = st.selectbox("🏷️ Pilih Kategori Diklat", kategori_list)

# === DROPDOWN 2: PILIH NAMA DIKLAT LENGKAP ===
filtered_by_kategori = all_data[all_data["Kategori Diklat"] == kategori]
diklat_list = sorted(filtered_by_kategori["Nama Diklat"].dropna().unique())
nama_diklat = st.selectbox("📚 Pilih Nama Diklat Lengkap", diklat_list)

# === DROPDOWN 3: PILIH MATA AJAR ===
filtered_by_diklat = filtered_by_kategori[filtered_by_kategori["Nama Diklat"] == nama_diklat]
mata_ajar_list = sorted(filtered_by_diklat["Mata Ajar"].dropna().unique())
mata_ajar = st.selectbox("🧠 Pilih Mata Ajar", mata_ajar_list)

# === FILTER AKHIR ===
filtered = filtered_by_diklat[filtered_by_diklat["Mata Ajar"] == mata_ajar]

# === HITUNG RANK ===
pivot = (
    filtered.groupby(["Tahun", "Instruktur"])["Rata-Rata"]
    .mean()
    .reset_index()
    .dropna()
)
pivot = pivot.sort_values(by=["Tahun", "Rata-Rata"], ascending=[False, False]).reset_index(drop=True)
pivot["Rank"] = pivot.groupby("Tahun")["Rata-Rata"].rank(method="first", ascending=False).astype(int)
pivot = pivot.rename(columns={"Rata-Rata": "Nilai"})

# === TAMPILKAN HASIL ===
st.markdown(f"### 📈 Hasil untuk:\n**Kategori:** _{kategori}_  \n**Nama Diklat:** _{nama_diklat}_  \n**Mata Ajar:** _{mata_ajar}_")

st.dataframe(
    pivot[["Tahun", "Rank", "Instruktur", "Nilai"]],
    use_container_width=True
)
