import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard Pengajar", layout="wide")
st.title("📊 Pengajar dengan Nilai Tertinggi")

# --- 1. Baca dari GitHub ---
file = "https://raw.githubusercontent.com/AzrielAprieliant/dashboard-pengajar/main/Data%20Instruktur%20asli.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

# Gabung semua data
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Pastikan numerik
all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# --- 2. Buat kolom awalan 3 kata ---
def get_awalan(diklat):
    return " ".join(str(diklat).split()[:4]).strip().lower()

all_data["Awalan Diklat"] = all_data["Nama Diklat"].apply(get_awalan)

# Hitung frekuensi awalan
awalan_counts = all_data["Awalan Diklat"].value_counts()

# --- 3. Tentukan 'Nama Diklat Gabungan' ---
def gabung_diklat(row):
    awalan = row["Awalan Diklat"]
    if awalan_counts[awalan] > 1:
        return awalan.title()  # Gunakan awalan sebagai nama gabungan
    else:
        return row["Nama Diklat"]  # Biarkan asli

all_data["Nama Diklat Gabungan"] = all_data.apply(gabung_diklat, axis=1)

# --- 4. Dropdown Pilih Nama Diklat ---
nama_diklat_display = st.selectbox("Pilih Nama Diklat", sorted(all_data["Nama Diklat Gabungan"].unique()))

# Filter berdasarkan nama diklat gabungan
filtered_cluster = all_data[all_data["Nama Diklat Gabungan"] == nama_diklat_display]

# --- 5. Dropdown Mata Ajar ---
mata_ajar = st.selectbox("Pilih Mata Ajar", sorted(filtered_cluster['Mata Ajar'].dropna().unique()))
filtered = filtered_cluster[filtered_cluster['Mata Ajar'] == mata_ajar]

# --- 6. Ranking ---
pivot = filtered.groupby(['Tahun', 'Instruktur'])['Rata-Rata'].mean().reset_index()
pivot = pivot.dropna()
pivot = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False])
pivot['Rank'] = pivot.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)
pivot = pivot.rename(columns={'Rata-Rata': 'Nilai'})

# --- 7. Tampilkan Hasil ---
st.markdown(f"""
#### 📘 Ranking Instruktur  
**Diklat:** {nama_diklat_display}  
**Mata Ajar:** {mata_ajar}
""")
st.dataframe(pivot[['Tahun', 'Rank', 'Instruktur', 'Nilai']], use_container_width=True)
