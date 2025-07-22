import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="Pengelompokan Nama Diklat", page_icon="📚", layout="wide")

st.markdown("<h1 style='text-align: center;'>📚 Pengelompokan Nama Diklat Otomatis</h1>", unsafe_allow_html=True)

# Upload file Excel
file = st.file_uploader("📂 Upload file Excel berisi nama diklat", type=["xlsx"])

if file:
    try:
        # Baca sheet tertentu (ubah sesuai kebutuhan)
        df = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")

        # Pastikan kolom 'Nama Diklat' ada
        if 'Nama Diklat' not in df.columns:
            st.error("❌ Kolom 'Nama Diklat' tidak ditemukan di Excel.")
        else:
            # Ambil data unik, hapus NaN
            nama_diklat = df['Nama Diklat'].dropna().unique()

            # Fungsi untuk ambil awalan 4 kata (boleh ubah ke 3 jika perlu)
            def ambil_awalan(text, max_kata=4):
                return " ".join(text.split()[:max_kata]).strip()

            # Kelompokkan berdasarkan awalan
            kelompok = defaultdict(list)
            for nama in nama_diklat:
                kunci = ambil_awalan(nama)
                kelompok[kunci].append(nama)

            # Hanya ambil kelompok yang terdiri dari lebih dari 1 item (biar gak acak)
            kelompok_terfilter = {k: v for k, v in kelompok.items() if len(v) > 1}

            if kelompok_terfilter:
                # Dropdown pilih kelompok
                st.markdown("### 📁 Pilih Kelompok Nama Diklat")
                pilihan_kelompok = list(kelompok_terfilter.keys())
                dipilih = st.selectbox("", pilihan_kelompok)

                # Tampilkan hasil
                st.markdown("### 📄 Daftar Nama Diklat dalam Kelompok:")
                for nama in kelompok_terfilter[dipilih]:
                    st.markdown(f"- {nama}")
            else:
                st.info("⚠️ Tidak ditemukan kelompok nama diklat yang memiliki awalan yang sama.")
    except Exception as e:
        st.error(f"Terjadi error saat membaca file: {e}")
else:
    st.info("⬆️ Silakan upload file Excel terlebih dahulu.")
