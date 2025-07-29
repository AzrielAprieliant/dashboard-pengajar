import streamlit as st
import pandas as pd
import os
import io
from rapidfuzz import process, fuzz

# === CONFIGURASI STREAMLIT ===
st.set_page_config(page_title="Dashboard Instruktur", layout="wide", initial_sidebar_state="collapsed")

st.title("📊 Dashboard Penilaian Instruktur")


# === CEK KEBERADAAN FILE ===
file = "Data Instruktur asli.xlsx"
unit_file = "Nama dan Unit Kerja.xlsx"

if not os.path.exists(file):
    st.error(f"❌ File '{file}' tidak ditemukan. Harap pastikan file diunggah ke direktori.")
    st.stop()

if not os.path.exists(unit_file):
    st.error(f"❌ File '{unit_file}' tidak ditemukan. Harap pastikan file diunggah ke direktori.")
    st.stop()

# === BACA DATA NILAI PER TAHUN ===
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

# Gabungkan semua
df = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
], ignore_index=True)

df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")
df = df.dropna(subset=["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata"])

# === BACA UNIT KERJA DAN LAKUKAN PEMADANAN (FUZZY MATCH) ===
df_unit = pd.read_excel(unit_file)
df_unit = df_unit.rename(columns={"Nama": "Nama_Unit", "nama unit": "Nama Unit"})

def fuzzy_match(nama, list_nama, threshold=60):
    match, score, _ = process.extractOne(nama, list_nama, scorer=fuzz.token_sort_ratio)
    if score >= threshold:
        return match
    return None

df["Nama_Cocok"] = df["Instruktur"].apply(lambda x: fuzzy_match(str(x), df_unit["Nama_Unit"]))
df = pd.merge(df, df_unit[["Nama_Unit", "Nama Unit"]], left_on="Nama_Cocok", right_on="Nama_Unit", how="left")
df = df.rename(columns={"Nama Unit": "Unit Kerja"})

# === DROPDOWN: PILIH NAMA DIKLAT ===
selected_diklat = st.selectbox("📌 Nama Diklat", sorted(df["Nama Diklat"].dropna().unique()))
filtered_df = df[df["Nama Diklat"] == selected_diklat]

# === DROPDOWN: MATA AJAR ===
available_mata_ajar = filtered_df["Mata Ajar"].dropna().unique()
selected_mata_ajar = st.selectbox("📘 Mata Ajar", sorted(available_mata_ajar))
filtered_df = filtered_df[filtered_df["Mata Ajar"] == selected_mata_ajar]

# === DROPDOWN: UNIT KERJA ===
available_unit_kerja = filtered_df["Unit Kerja"].dropna().unique().tolist()
available_unit_kerja.insert(0, "(Tampilkan Semua)")
selected_unit_kerja = st.selectbox("🏢 Unit Kerja", available_unit_kerja)

if selected_unit_kerja != "(Tampilkan Semua)":
    filtered_df = filtered_df[filtered_df["Unit Kerja"] == selected_unit_kerja]

# === TAMPILKAN DATA HASIL ===
if not filtered_df.empty:
    st.markdown("### 🔍 Hasil Data:")

    # Hitung tinggi tabel dinamis berdasarkan jumlah baris (maks 600px)
    row_height = 40
    max_height = 600
    dynamic_height = min(row_height * len(filtered_df), max_height)
    
    st.dataframe(
        filtered_df[["Instruktur", "Mata Ajar", "Nama Diklat", "Tahun", "Unit Kerja", "Rata-Rata"]],
        use_container_width=True,
        height=dynamic_height
    )

    # === DOWNLOAD BUTTON ===
    st.markdown("### ⬇️ Unduh Data Hasil")
    excel_buffer = io.BytesIO()
    filtered_df[["Instruktur", "Mata Ajar", "Nama Diklat", "Tahun", "Unit Kerja", "Rata-Rata"]].to_excel(
        excel_buffer, index=False, sheet_name="Hasil"
    )
    st.download_button(
        label="Unduh Hasil ke Excel",
        data=excel_buffer.getvalue(),
        file_name="hasil_penilaian_instruktur.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠️ Tidak ada data ditemukan untuk filter yang dipilih.")
