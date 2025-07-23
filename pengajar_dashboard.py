import pandas as pd
import streamlit as st
import requests
from io import BytesIO
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Dashboard Instruktur", layout="wide")
st.title("📊 Dashboard Instruktur dengan Nilai Tertinggi")

# --- 1. Load data dari GitHub ---
@st.cache_data
def load_data():
    url = "https://github.com/AzrielAprieliant/dashboard-pengajar/raw/main/Data%20Instruktur%20asli.xlsx"
    response = requests.get(url)
    xls = pd.ExcelFile(BytesIO(response.content))

    all_data = []
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        df["Tahun"] = sheet[-4:] if sheet[-4:].isdigit() else None
        all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

df = load_data()

# --- 2. Normalisasi kolom ---
rename_map = {
    "Instruktur /WI": "Instruktur",
    "Rata2": "Nilai",
    "Rata-Rata": "Nilai"
}
df = df.rename(columns=rename_map)

# Hanya ambil kolom yang dibutuhkan
df = df[["Instruktur", "Mata Ajar", "Nama Diklat", "Nilai", "Tahun"]].copy()

# Pastikan numeric
df["Nilai"] = pd.to_numeric(df["Nilai"], errors="coerce")

# --- 3. Clustering Nama Diklat mirip ---
def cluster_diklat(nama_diklat_list, threshold=85):
    clustered = {}
    for nama in nama_diklat_list:
        found = False
        for key in clustered:
            score = fuzz.partial_ratio(nama.lower(), key.lower())
            if score >= threshold:
                clustered[key].append(nama)
                found = True
                break
        if not found:
            clustered[nama] = [nama]
    
    # Buat mapping: nama asli -> cluster nama
    mapping = {}
    for cluster_name, variants in clustered.items():
        for variant in variants:
            mapping[variant] = cluster_name
    return mapping

# Buat mapping nama diklat hasil clustering
nama_diklat_unik = df["Nama Diklat"].dropna().unique()
cluster_mapping = cluster_diklat(nama_diklat_unik)
df["Cluster Diklat"] = df["Nama Diklat"].map(cluster_mapping)

# --- 4. Dropdown nama diklat (clustered) ---
selected_diklat = st.selectbox("📘 Pilih Nama Diklat", sorted(df["Cluster Diklat"].unique()))

# Filter berdasarkan diklat
filtered_diklat = df[df["Cluster Diklat"] == selected_diklat]

# --- 5. Dropdown mata ajar ---
selected_mata_ajar = st.selectbox("📚 Pilih Mata Ajar", sorted(filtered_diklat["Mata Ajar"].dropna().unique()))

# Filter lagi berdasarkan mata ajar
filtered = filtered_diklat[filtered_diklat["Mata Ajar"] == selected_mata_ajar]

# --- 6. Hitung ranking per tahun ---
ranking = (
    filtered
    .groupby(["Tahun", "Instruktur"], as_index=False)
    .agg(Nilai=("Nilai", "mean"))
    .dropna(subset=["Nilai"])
)

ranking["Rank"] = ranking.groupby("Tahun")["Nilai"].rank(ascending=False, method="first").astype(int)
ranking = ranking.sort_values(["Tahun", "Rank"])

# --- 7. Tampilkan hasil ---
st.write(f"### 🏆 Pengajar terbaik untuk diklat **{selected_diklat}** dan mata ajar **{selected_mata_ajar}**")
st.dataframe(ranking, use_container_width=True)
