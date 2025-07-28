import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

st.set_page_config(page_title="Dashboard Instruktur", layout="wide")
st.title("📊 Dashboard Penilaian Instruktur")

# ======== STEP 1: BACA DATA DARI SEMUA SHEET ========
file = "data instruktur asli.xlsx"

# Sheet 2025
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

# Sheet 2024
sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

# Sheet 2023
sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={
    "Instruktur /WI": "Instruktur",
    "Rata2": "Rata-Rata"
})
sheet_2023["Tahun"] = 2023

# Gabungkan semua
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Pastikan nilai numerik
all_data["Rata-Rata"] = pd.to_numeric(all_data["Rata-Rata"], errors="coerce")


# ======== STEP 2: CLUSTERING NAMA DIKLAT ========
def cluster_diklat(diklat_list, threshold=87):
    clusters = {}
    for diklat in diklat_list:
        matched = None
        for label in clusters:
            if fuzz.token_sort_ratio(diklat, label) >= threshold:
                matched = label
                break
        if matched:
            clusters[matched].append(diklat)
        else:
            clusters[diklat] = [diklat]
    return clusters

unique_diklat = all_data["Nama Diklat"].dropna().unique().tolist()
cluster_result = cluster_diklat(unique_diklat)

# Mapping diklat asli ke cluster nama gabungan
map_diklat = {}
for group_name, variants in cluster_result.items():
    for var in variants:
        map_diklat[var] = group_name

# Tambahkan kolom nama diklat gabungan
all_data["Nama Diklat Gabungan"] = all_data["Nama Diklat"].map(map_diklat)


# ======== STEP 3: DROPDOWN DIKLAT GABUNGAN & MATA AJAR ========
selected_diklat = st.selectbox("📌 Pilih Nama Diklat", sorted(all_data["Nama Diklat Gabungan"].dropna().unique()))
filtered_df = all_data[all_data["Nama Diklat Gabungan"] == selected_diklat]

selected_mata_ajar = st.selectbox("📘 Pilih Mata Ajar", sorted(filtered_df["Mata Ajar"].dropna().unique()))
filtered_df = filtered_df[filtered_df["Mata Ajar"] == selected_mata_ajar]


# ======== STEP 4: HITUNG RANKING PER INSTRUKTUR PER TAHUN ========
# Pastikan tidak ada nilai kosong
filtered_df = filtered_df.dropna(subset=["Instruktur", "Rata-Rata"])

pivot = (
    filtered_df.groupby(["Tahun", "Instruktur"])["Rata-Rata"]
    .mean()
    .reset_index()
    .sort_values(by=["Tahun", "Rata-Rata"], ascending=[False, False])
)

# Tambahkan ranking
pivot["Rank"] = pivot.groupby("Tahun")["Rata-Rata"].rank(method="first", ascending=False).astype(int)
pivot = pivot.rename(columns={"Rata-Rata": "Nilai"})

# ======== STEP 5: TAMPILKAN HASIL ========
st.markdown(f"### 📍 Grup Diklat: {selected_diklat} | Mata Ajar: {selected_mata_ajar}")
st.dataframe(pivot[["Tahun", "Rank", "Instruktur", "Nilai"]], use_container_width=True)
