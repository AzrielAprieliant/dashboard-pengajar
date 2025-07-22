import streamlit as st
import pandas as pd

st.set_page_config(page_title="📚 Pengelompokan Nama Diklat", layout="wide")
st.title("📚 Pengelompokan Nama Diklat Otomatis")

# === BACA FILE ===
file = "Data Instruktur.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

# === GABUNGKAN SEMUA DATA ===
df = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# === BERSIHIN ===
df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")
for col in ["Instruktur", "Mata Ajar", "Nama Diklat"]:
    df[col] = df[col].astype(str).str.strip().str.replace("\xa0", " ", regex=False)

# === BUAT KOLOM AWALAN UNTUK PENGELOMPOKAN ===
df["Awalan"] = df["Nama Diklat"].str.extract(r'^(.{1,40})')
# Hitung jumlah per awalan
awalan_counts = df["Awalan"].value_counts()
# Filter hanya yang muncul lebih dari 1
df = df[df["Awalan"].isin(awalan_counts[awalan_counts > 1].index)]

# === DROPDOWN PERTAMA: PILIH KELOMPOK DIKLAT ===
pilihan_kelompok = sorted(df["Awalan"].unique())
kelompok = st.selectbox("📂 Pilih Kelompok Nama Diklat", pilihan_kelompok)

df_kelompok = df[df["Awalan"] == kelompok]

# === DROPDOWN KEDUA: PILIH MATA AJAR ===
pilihan_mata_ajar = sorted(df_kelompok["Mata Ajar"].unique())
mata_ajar = st.selectbox("🧠 Pilih Mata Ajar", pilihan_mata_ajar)

# === FILTER FINAL ===
filtered = df_kelompok[df_kelompok["Mata Ajar"] == mata_ajar]

# === HITUNG RANKING PER INSTRUKTUR ===
pivot = filtered.groupby(["Tahun", "Instruktur"])["Rata-Rata"].mean().reset_index()
pivot = pivot.dropna(subset=["Rata-Rata"])
pivot = pivot.sort_values(by=["Tahun", "Rata-Rata"], ascending=[False, False]).reset_index(drop=True)
pivot["Rank"] = pivot.groupby("Tahun")["Rata-Rata"].rank(method="first", ascending=False).astype(int)

# === TAMPILKAN ===
pivot = pivot.rename(columns={"Rata-Rata": "Nilai"})

st.markdown(f"### 📈 Hasil untuk:\n**Kelompok Nama Diklat:** _{kelompok}_  \n**Mata Ajar:** _{mata_ajar}_")
st.dataframe(
    pivot[["Tahun", "Rank", "Instruktur", "Nilai"]],
    use_container_width=True
)
