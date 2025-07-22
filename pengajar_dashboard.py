import streamlit as st
import pandas as pd

st.set_page_config(page_title="📚 Pengelompokan Nama Diklat Otomatis", layout="wide")
st.title("📚 Pengelompokan Nama Diklat Otomatis")

# Langsung baca dari file lokal
try:
    all_sheets = pd.read_excel("Data Instruktur asli.xlsx", sheet_name=None)
except FileNotFoundError:
    st.error("❌ File 'Data Instruktur asli.xlsx' tidak ditemukan di folder ini.")
    st.stop()

# Gabung semua sheet jadi satu dataframe
df_list = []
for sheet_name, df in all_sheets.items():
    df["Sheet"] = sheet_name
    df_list.append(df)
df = pd.concat(df_list, ignore_index=True)

# Pastikan kolom penting ada
df.columns = df.columns.str.strip()
required_cols = ["Nama Diklat", "Mata Ajar", "Rata-Rata"]
if not all(col in df.columns for col in required_cols):
    st.error(f"❌ File harus memiliki kolom: {required_cols}")
    st.stop()

# Hapus baris kosong
df = df.dropna(subset=required_cols)

# Fungsi ambil 3 kata awal
def ambil_awal(nama):
    return " ".join(str(nama).strip().lower().split()[:3])

df["Awalan Diklat"] = df["Nama Diklat"].apply(ambil_awal)

# Tampilkan dropdown nama diklat (berdasarkan awalan)
grup_diklat = df["Awalan Diklat"].unique()
dipilih = st.selectbox("📌 Pilih Grup Nama Diklat", sorted(grup_diklat))

# Tampilkan data yang sesuai
hasil = df[df["Awalan Diklat"] == dipilih][["Nama Diklat", " Mata Ajar", "Rata-Rata"]].sort_values("Nama Diklat")
st.dataframe(hasil, use_container_width=True)

# Tombol download
csv = hasil.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download sebagai CSV", csv, file_name=f"{dipilih}_hasil.csv", mime="text/csv")
