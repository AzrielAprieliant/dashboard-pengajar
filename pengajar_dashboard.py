import pandas as pd
import streamlit as st

# === CSS Style: kecilkan lebar ===
st.markdown("""
    <style>
    .main-title {
        font-size:30px;
        font-weight:bold;
        color:#00BFFF;
        text-align:center;
        margin-bottom: 0.5em;
    }
    .sub-title {
        font-size:14px;
        font-style:italic;
        color:#888888;
        text-align:center;
        margin-bottom:1.5em;
    }
    </style>
""", unsafe_allow_html=True)

# === Judul ===
st.markdown('<div class="main-title">📊 Dashboard Pengajar Terbaik</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Filter berdasarkan Diklat & Mata Ajar — Penilaian 2023–2025</div>', unsafe_allow_html=True)

# === Load Data ===
file = "Data Instruktur.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
], ignore_index=True)

all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# === Layout dropdown sempit agar compact ===
col1, col2 = st.columns([1, 1])  # Dua kolom sejajar

with col1:
    nama_diklat = st.selectbox(
        "📚 Pilih Nama Diklat",
        sorted(all_data["Nama Diklat"].dropna().unique()),
        key="diklat",
    )

filtered_diklat = all_data[all_data["Nama Diklat"] == nama_diklat]

with col2:
    mata_ajar = st.selectbox(
        "🧠 Pilih Mata Ajar",
        sorted(filtered_diklat["Mata Ajar"].dropna().unique()),
        key="ajar",
    )

filtered = filtered_diklat[filtered_diklat["Mata Ajar"] == mata_ajar]

# === Ranking ===
pivot = (
    filtered.groupby(["Tahun", "Instruktur"])["Rata-Rata"]
    .mean()
    .reset_index()
    .dropna(subset=["Rata-Rata"])
)

pivot_sorted = pivot.sort_values(by=["Tahun", "Rata-Rata"], ascending=[False, False]).reset_index(drop=True)
pivot_sorted["Rank"] = pivot_sorted.groupby("Tahun")["Rata-Rata"].rank(method="first", ascending=False).astype(int)
pivot_sorted = pivot_sorted.rename(columns={"Rata-Rata": "Nilai"})

# === Output ===
st.markdown("---")
st.markdown(f"### 🏆 Pengajar terbaik untuk: **{nama_diklat}** — *{mata_ajar}*")
st.dataframe(pivot_sorted[["Tahun", "Rank", "Instruktur", "Nilai"]], use_container_width=True)
