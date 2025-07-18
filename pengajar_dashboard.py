import pandas as pd
import streamlit as st
import altair as alt

# === Gaya tampilan (CSS) ===
st.markdown("""
    <style>
        .main-title {
            font-size:36px;
            font-weight:bold;
            color:#4fc3f7;
            text-align:center;
        }
        .sub-title {
            font-size:18px;
            font-style:italic;
            color:#bbbbbb;
            text-align:center;
            margin-bottom:20px;
        }
        .stDataFrame th {
            background-color:#263238;
            color:white;
        }
    </style>
""", unsafe_allow_html=True)

# === Judul Halaman ===
st.markdown('<div class="main-title">📊 Dashboard Pengajar Terbaik</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Data penilaian instruktur berdasarkan Diklat & Mata Ajar (2023–2025)</div>', unsafe_allow_html=True)

# === 1. Baca data dari file Excel ===
file = "Data Instruktur.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

# === 2. Gabungkan semua data ===
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
], ignore_index=True)

all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# === 3. Dropdown Pilihan ===
nama_diklat = st.selectbox("📚 Pilih Nama Diklat", sorted(all_data['Nama Diklat'].dropna().unique()))
filtered_diklat = all_data[all_data['Nama Diklat'] == nama_diklat]

mata_ajar = st.selectbox("🧠 Pilih Mata Ajar", sorted(filtered_diklat['Mata Ajar'].dropna().unique()))
filtered = filtered_diklat[filtered_diklat['Mata Ajar'] == mata_ajar]

# === 4. Olah Data ===
pivot = filtered.groupby(['Tahun', 'Instruktur'])['Rata-Rata'].mean().reset_index()
pivot = pivot.dropna(subset=['Rata-Rata'])
pivot_sorted = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False]).reset_index(drop=True)
pivot_sorted['Rank'] = pivot_sorted.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)
pivot_sorted = pivot_sorted.rename(columns={'Rata-Rata': 'Nilai'})

# === 5. Tampilkan Tabel ===
st.markdown("---")
st.markdown(f"### 🏆 Pengajar terbaik untuk: **{nama_diklat}** — *{mata_ajar}*")
st.dataframe(pivot_sorted[['Tahun', 'Rank', 'Instruktur', 'Nilai']], use_container_width=True)
