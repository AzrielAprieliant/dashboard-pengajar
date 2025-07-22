import pandas as pd
import re

# === BACA FILE ===
file = "Data Instruktur asli.xlsx"

# Baca tiap sheet dan beri label tahun
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={
    "Instruktur /WI": "Instruktur",
    "Rata2": "Rata-Rata"
})
sheet_2023["Tahun"] = 2023

# Gabungkan semua data
data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
], ignore_index=True)

# === BERSIHIN DATA ===
for col in ["Instruktur", "Mata Ajar", "Nama Diklat"]:
    data[col] = data[col].astype(str).str.strip().str.replace("\xa0", " ", regex=False)

data["Rata-Rata"] = pd.to_numeric(data["Rata-Rata"], errors="coerce")

# === BUAT KOLOM: Grup Nama Diklat ===
def ambil_awal(nama):
    # Ambil sebelum tanda "-" atau "–" atau pisahkan per batch
    if pd.isna(nama):
        return ""
    return re.split(r"\s*[-–]\s*", nama)[0].strip().lower()

data["Grup Diklat"] = data["Nama Diklat"].apply(ambil_awal)

# === HITUNG RATA-RATA PER INSTRUKTUR PER GRUP PER TAHUN ===
pivot = data.groupby(["Tahun", "Grup Diklat", "Instruktur"])["Rata-Rata"].mean().reset_index()
pivot = pivot.dropna(subset=["Rata-Rata"])

# === HITUNG RANK PER TAHUN & PER GRUP ===
pivot["Rank"] = pivot.groupby(["Tahun", "Grup Diklat"])["Rata-Rata"]\
    .rank(method="first", ascending=False).astype(int)

# === GANTI NAMA KOLOM UTAMA ===
pivot = pivot.rename(columns={"Grup Diklat": "Nama Diklat", "Rata-Rata": "Nilai"})

# === SIMPAN KE EXCEL ===
pivot.to_excel("Output_Kelompok_Diklat.xlsx", index=False)
print("✅ Berhasil disimpan ke Output_Kelompok_Diklat.xlsx")
