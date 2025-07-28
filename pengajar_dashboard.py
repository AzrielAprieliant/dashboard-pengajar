import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from rapidfuzz import process

# Judul aplikasi
st.set_page_config(page_title="Dashboard Pengajar", layout="wide")
st.title("📊 Dashboard Pengajar - Penilaian Instruktur")

# Fungsi untuk mengelompokkan diklat berdasarkan kemiripan nama
def group_similar_titles(titles, threshold=80):
    clustered = {}
    for title in titles:
        matched = False
        for cluster in clustered:
            if fuzz.partial_ratio(title.lower(), cluster.lower()) >= threshold:
                clustered[cluster].append(title)
                matched = True
                break
        if not matched:
            clustered[title] = [title]
    return clustered

# Baca data dari file lokal (pastikan file ini ada di folder yang sama dengan script)
data = pd.read_excel("data instruktur asli.xlsx", sheet_name=None)

# Gabungkan semua sheet
all_data = pd.concat(data.values(), ignore_index=True)

# Drop baris kosong
all_data = all_data.dropna(subset=["Nama Diklat", "Mata Ajar", "Rata-Rata"])

# Kelompokkan nama diklat
unique_diklat = all_data["Nama Diklat"].unique()
clusters = group_similar_titles(unique_diklat)

# Buat pilihan berdasarkan kelompok nama diklat
diklat_options = list(clusters.keys())
selected_diklat_group = st.selectbox("Pilih Nama Dik
