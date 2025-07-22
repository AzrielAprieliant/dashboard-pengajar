import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="📚 Pengelompokan Nama Diklat Otomatis", layout="centered")

st.title("📚 Pengelompokan Nama Diklat Otomatis")

# Upload file Excel
uploaded_file = st.file_uploader("📤 Upload File Excel", type=["xlsx"])

if uploaded_file:
    # Baca sheet
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Penilaian Jan Jun 2025")
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        st.stop()

    # Drop baris kosong
    df = df.dropna(subset=["Nama Diklat", "Nama Mata Ajar", "Nilai"])

    # Ambil nama diklat unik
    diklat_list = df["Nama Diklat"].dropna().unique()

    # Fungsi grouping berdasarkan awalan
    grouped_diklat = defaultdict(list)
    for diklat in diklat_list:
        prefix = diklat.split()[0]
        grouped_diklat[prefix].append(diklat)

    # Gabungkan hanya jika prefix muncul > 1
    grouped_options = []
    grouped_dict = {}
    for prefix, diklats in grouped_diklat.items():
        if len(diklats) > 1:
            group_name = f"{prefix} - ({len(diklats)} diklat)"
            grouped_options.append(group_name)
            grouped_dict[group_name] = diklats
        else:
            grouped_options.extend(diklats)

    # Pilih dari dropdown
    st.subheader("📁 Pilih Kelompok Nama Diklat")
    selected = st.selectbox("Pilih Kelompok Diklat", grouped_options)

    # Ambil diklat terpilih
    if selected in grouped_dict:
        diklat_terpilih = grouped_dict[selected]
    else:
        diklat_terpilih = [selected]

    # Filter data
    filtered_df = df[df["Nama Diklat"].isin(diklat_terpilih)]

    # Tampilkan data
    st.markdown("### 📖 Detail Mata Ajar dan Nilai")
    st.dataframe(
        filtered_df[["Nama Diklat", "Nama Mata Ajar", "Nilai"]].sort_values(by=["Nama Diklat", "Nama Mata Ajar"])
    )

else:
    st.warning("Silakan upload file Excel terlebih dahulu.")
