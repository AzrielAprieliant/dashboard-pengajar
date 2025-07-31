import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Instruktur", layout="wide", initial_sidebar_state="collapsed")

# Tampilkan judul utama duluan
st.title("📊 Dashboard Penilaian Instruktur")

# Load data
df = pd.read_excel("Penilaian Gabung dengan Nama Unit.xlsx")

# Konversi 'Rata-Rata' jadi numerik
df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")

# Perbaiki nilai yang tidak wajar (>100 diasumsikan kesalahan format, dibagi 10000)
df.loc[df["Rata-Rata"] > 100, "Rata-Rata"] = df["Rata-Rata"] / 10000

# Bulatkan ke 2 desimal
df["Rata-Rata"] = df["Rata-Rata"].round(2)

nama_diklat = st.selectbox("📘 Pilih Nama Diklat", ["Semua"] + sorted(df["Nama Diklat"].dropna().unique().tolist()))
mata_ajar = st.selectbox("📖 Pilih Mata Ajar", ["Semua"] + sorted(df["Mata Ajar"].dropna().unique().tolist()))
unit_kerja = st.selectbox("🏢 Pilih Nama Unit", ["Semua"] + sorted(df["Nama Unit"].dropna().unique().tolist()))

# Filter data
filtered_df = df.copy()

if nama_diklat != "Semua":
    filtered_df = filtered_df[filtered_df["Nama Diklat"] == nama_diklat]

if mata_ajar != "Semua":
    filtered_df = filtered_df[filtered_df["Mata Ajar"] == mata_ajar]

if unit_kerja != "Semua":
    filtered_df = filtered_df[filtered_df["Nama Unit"] == unit_kerja]

if not filtered_df.empty:
    # Urutkan dan tambahkan kolom peringkat
    filtered_df = filtered_df.sort_values(by="Rata-Rata", ascending=False).reset_index(drop=True)
    filtered_df.index += 1  # Mulai dari peringkat 1
    filtered_df.insert(0, "Peringkat", filtered_df.index)


    # Tampilkan tabel ranking
    st.markdown("### 📋 Tabel Peringkat Instruktur")
    st.dataframe(filtered_df[[
        "Peringkat", "Instruktur", "Mata Ajar", "Nama Diklat", "Nama Unit", "Rata-Rata"
    ]])
else:
    st.warning("Tidak ada data yang cocok dengan filter.")
