import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📚 Pengelompokan Nama Diklat Otomatis")
st.title("📚 Pengelompokan Nama Diklat Otomatis")

# Baca semua sheet dari file Excel
file_path = "Data Instruktur asli.xlsx"
if not os.path.exists(file_path):
    st.error(f"❌ File tidak ditemukan: {file_path}")
    st.stop()

# Gabungkan semua sheet
xls = pd.ExcelFile(file_path)
df_all = pd.concat([xls.parse(sheet) for sheet in xls.sheet_names], ignore_index=True)
df = df_all.copy()

# Bersihkan dan standarize nama kolom
df.columns = df.columns.str.strip()
kolom_dibutuhkan = ["Nama Diklat", "Nama Mata Ajar", "Nilai"]
if not all(kol in df.columns for kol in kolom_dibutuhkan):
    st.error("❌ Kolom yang dibutuhkan tidak lengkap dalam file Excel. Harus ada 'Nama Diklat', 'Nama Mata Ajar', dan 'Nilai'")
    st.stop()

# Hapus baris kosong dan pastikan nilai angka
df = df.dropna(subset=kolom_dibutuhkan)
df["Nilai"] = pd.to_numeric(df["Nilai"], errors="coerce")
df = df.dropna(subset=["Nilai"])

# Buat kolom Awalan Diklat (untuk pengelompokan)
df["Awalan Diklat"] = df["Nama Diklat"].str.extract(r"^(.+?)(?:\s|$)", expand=False)

# Hitung rata-rata nilai per Nama Diklat dan Mata Ajar
rata2 = df.groupby(["Nama Diklat", "Nama Mata Ajar"]).agg({"Nilai": "mean"}).reset_index()
rata2 = rata2.rename(columns={"Nilai": "Rata-Rata"})

# Gabungkan kembali dengan Awalan Diklat
rata2 = rata2.merge(df[["Nama Diklat", "Awalan Diklat"]].drop_duplicates(), on="Nama Diklat", how="left")

# Cari awalan diklat yang punya lebih dari satu nama diklat
awalan_duplikat = rata2["Awalan Diklat"].value_counts()
awalan_terpilih = awalan_duplikat[awalan_duplikat > 1].index.tolist()

# Dropdown pengelompokan berdasarkan awalan nama
dipilih = st.selectbox("🔠 Pilih Awalan Diklat", awalan_terpilih)

# Filter berdasarkan awalan yang dipilih
hasil = rata2[rata2["Awalan Diklat"] == dipilih]

# Dropdown mata ajar
mata_ajar_unik = hasil["Nama Mata Ajar"].unique().tolist()
mata_ajar_pilih = st.selectbox("📘 Pilih Mata Ajar", ["Semua"] + mata_ajar_unik)

if mata_ajar_pilih != "Semua":
    hasil = hasil[hasil["Nama Mata Ajar"] == mata_ajar_pilih]

# Urutkan berdasarkan Rata-Rata
hasil = hasil.sort_values(by="Rata-Rata", ascending=False).reset_index(drop=True)

# Tampilkan tabel akhir
st.subheader("📊 Hasil Pengelompokan dan Ranking")
st.dataframe(hasil, use_container_width=True)

# Tombol unduh CSV
csv = hasil.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download CSV", csv, file_name=f"hasil_{dipilih}.csv", mime="text/csv")
