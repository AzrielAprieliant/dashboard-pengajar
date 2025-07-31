import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Instruktur", layout="wide", initial_sidebar_state="collapsed")

st.title("📊 Dashboard Penilaian Instruktur")

# Load data
df = pd.read_excel("Penilaian Gabung dengan Nama Unit.xlsx")

# Bersihkan nilai
df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")
df.loc[df["Rata-Rata"] > 100, "Rata-Rata"] = df["Rata-Rata"] / 10000
df["Rata-Rata"] = df["Rata-Rata"].round(2)

nama_diklat = st.selectbox("📘 Pilih Nama Diklat", ["Semua"] + sorted(df["Nama Diklat"].dropna().unique().tolist()))
df_diklat = df if nama_diklat == "Semua" else df[df["Nama Diklat"] == nama_diklat]

unit_kerja = st.selectbox("🏢 Pilih Nama Unit", ["Semua"] + sorted(df_diklat["Nama Unit"].dropna().unique().tolist()))
df_unit = df_diklat if unit_kerja == "Semua" else df_diklat[df_diklat["Nama Unit"] == unit_kerja]

mata_ajar = st.selectbox("📖 Pilih Mata Ajar", ["Semua"] + sorted(df_unit["Mata Ajar"].dropna().unique().tolist()))

# Filter akhir
filtered_df = df.copy()
if nama_diklat != "Semua":
    filtered_df = filtered_df[filtered_df["Nama Diklat"] == nama_diklat]
if unit_kerja != "Semua":
    filtered_df = filtered_df[filtered_df["Nama Unit"] == unit_kerja]
if mata_ajar != "Semua":
    filtered_df = filtered_df[filtered_df["Mata Ajar"] == mata_ajar]

# =================== OUTPUT ===================


if not filtered_df.empty:
    # Ambil hanya satu mata ajar terbaik per instruktur (nilai tertinggi)
    top_per_instruktur = (
        filtered_df.sort_values(by="Rata-Rata", ascending=False)
        .groupby("Instruktur", as_index=False)
        .first()
    )

    # Ranking
    top_per_instruktur = top_per_instruktur.sort_values(by="Rata-Rata", ascending=False).reset_index(drop=True)
    top_per_instruktur.index += 1
    top_per_instruktur.insert(0, "Peringkat", top_per_instruktur.index)

    st.markdown("### 📋 Tabel Peringkat Instruktur")
    st.dataframe(top_per_instruktur[[
        "Peringkat", "Instruktur", "Mata Ajar", "Nama Diklat", "Nama Unit", "Rata-Rata"
    ]])
else:
    st.warning("Tidak ada data yang cocok dengan filter.")
