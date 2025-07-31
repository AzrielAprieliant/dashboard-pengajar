import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Instruktur", layout="wide", initial_sidebar_state="collapsed")
st.title("📊 Dashboard Penilaian Instruktur")

# Load data
df = pd.read_excel("Penilaian Gabung dengan Nama Unit.xlsx")

# Perbaiki nilai rata-rata
df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")
df.loc[df["Rata-Rata"] > 100, "Rata-Rata"] = df["Rata-Rata"] / 10000
df["Rata-Rata"] = df["Rata-Rata"].round(2)

# Dropdown 1: Nama Diklat
nama_diklat = st.selectbox("📘 Pilih Nama Diklat", ["Semua"] + sorted(df["Nama Diklat"].dropna().unique().tolist()))
df_diklat = df if nama_diklat == "Semua" else df[df["Nama Diklat"] == nama_diklat]

# Dropdown 2: Nama Unit
unit_kerja = st.selectbox("🏢 Pilih Nama Unit", ["Semua"] + sorted(df_diklat["Nama Unit"].dropna().unique().tolist()))
df_unit = df_diklat if unit_kerja == "Semua" else df_diklat[df_diklat["Nama Unit"] == unit_kerja]

# Dropdown 3: Mata Ajar (hanya yang tersedia di data terfilter)
mata_ajar = st.selectbox("📖 Pilih Mata Ajar", sorted(df_unit["Mata Ajar"].dropna().unique().tolist()))

# Filter akhir berdasarkan mata ajar
filtered_df = df_unit[df_unit["Mata Ajar"] == mata_ajar]

# Tampilkan hasil jika data ada
if not filtered_df.empty:
    # Ambil hanya satu baris nilai tertinggi per instruktur
    top_instruktur = (
        filtered_df.sort_values(by="Rata-Rata", ascending=False)
        .groupby("Instruktur", as_index=False)
        .first()
    )

    # Hitung peringkat
    top_instruktur = top_instruktur.sort_values(by="Rata-Rata", ascending=False).reset_index(drop=True)
    top_instruktur.index += 1
    top_instruktur.insert(0, "Peringkat", top_instruktur.index)

    # Tampilkan tabel
    st.markdown(f"### 📋 Tabel Peringkat Instruktur untuk Mata Ajar: `{mata_ajar}`")
    st.dataframe(top_instruktur[[
        "Peringkat", "Instruktur", "Mata Ajar", "Nama Diklat", "Nama Unit", "Rata-Rata"
    ]],
    use_container_width=True,
    height=500  # Atur tinggi sesuai kebutuhan (600 pixel misalnya)      
     )
else:
    st.warning("⚠️ Tidak ada data yang cocok dengan filter.")
