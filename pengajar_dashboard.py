import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Instruktur", layout="wide", initial_sidebar_state="collapsed")

# Judul halaman
st.title("📊 Dashboard Penilaian Instruktur")

# Load data
df = pd.read_excel("Penilaian Gabung dengan Nama Unit.xlsx")

# Bersihkan kolom 'Rata-Rata'
df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")
df.loc[df["Rata-Rata"] > 100, "Rata-Rata"] = df["Rata-Rata"] / 10000
df["Rata-Rata"] = df["Rata-Rata"].round(2)

# ================== DROPDOWN FILTER ==================

# Filter bertingkat: diklat > unit kerja > mata ajar
nama_diklat = st.selectbox("📘 Pilih Nama Diklat", ["Semua"] + sorted(df["Nama Diklat"].dropna().unique().tolist()))
df_diklat = df if nama_diklat == "Semua" else df[df["Nama Diklat"] == nama_diklat]

unit_kerja = st.selectbox("🏢 Pilih Nama Unit", ["Semua"] + sorted(df_diklat["Nama Unit"].dropna().unique().tolist()))
df_unit = df_diklat if unit_kerja == "Semua" else df_diklat[df_diklat["Nama Unit"] == unit_kerja]

mata_ajar = st.selectbox("📖 Pilih Mata Ajar", ["Semua"] + sorted(df_unit["Mata Ajar"].dropna().unique().tolist()))

# ================== FINAL FILTER ==================

filtered_df = df.copy()
if nama_diklat != "Semua":
    filtered_df = filtered_df[filtered_df["Nama Diklat"] == nama_diklat]
if unit_kerja != "Semua":
    filtered_df = filtered_df[filtered_df["Nama Unit"] == unit_kerja]
if mata_ajar != "Semua":
    filtered_df = filtered_df[filtered_df["Mata Ajar"] == mata_ajar]

# ================== OUTPUT ==================

if not filtered_df.empty:
    # Ambil satu baris terbaik per Instruktur + Mata Ajar
    top_per_instruktur_mata_ajar = (
        filtered_df.sort_values(by="Rata-Rata", ascending=False)
        .groupby(["Instruktur", "Mata Ajar"], as_index=False)
        .first()
    )

    # Ranking
    top_per_instruktur_mata_ajar = top_per_instruktur_mata_ajar.sort_values(by="Rata-Rata", ascending=False).reset_index(drop=True)
    top_per_instruktur_mata_ajar.index += 1
    top_per_instruktur_mata_ajar.insert(0, "Peringkat", top_per_instruktur_mata_ajar.index)

    # Tampilkan hasil
    st.markdown("### 📋 Tabel Peringkat Instruktur per Mata Ajar")
    st.dataframe(top_per_instruktur_mata_ajar[[
        "Peringkat", "Instruktur", "Mata Ajar", "Nama Diklat", "Nama Unit", "Rata-Rata"
    ]])
else:
    st.warning("⚠️ Tidak ada data yang cocok dengan filter.")
