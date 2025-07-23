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

all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# --- 2. Buat Cluster Berdasarkan Awalan 3 Kata dari Nama Diklat ---
def ambil_awalan(nama, n=3):
    return " ".join(str(nama).split()[:n]).lower()

all_data["Cluster Diklat"] = all_data["Nama Diklat"].apply(ambil_awalan)

# --- 3. Mapping Nama Cluster → Nama Tampilan ---
# Bisa kamu sesuaikan di sini
cluster_nama_mapping = {
    "audit investigatif level": "Audit Investigatif",
    "bimbingan teknis reviu": "Bimtek Reviu",
    "pelatihan jabatan fungsional": "Pelatihan Fungsional"
}
# Default: kapitalisasi otomatis kalau tidak ada di mapping
all_data["Nama Diklat Gabung"] = all_data["Cluster Diklat"].map(cluster_nama_mapping).fillna(all_data["Cluster Diklat"].str.title())

# --- 4. Dropdown Pilih Nama Diklat Gabungan ---
nama_diklat_display = st.selectbox("Pilih Nama Diklat", sorted(all_data["Nama Diklat Gabung"].unique()))

# Ambil cluster yang sesuai
cluster_terpilih = all_data[all_data["Nama Diklat Gabung"] == nama_diklat_display]["Cluster Diklat"].iloc[0]

# Filter berdasarkan cluster diklat
filtered_cluster = all_data[all_data["Cluster Diklat"] == cluster_terpilih]

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
**Diklat Gabungan:** {nama_diklat_display}  
**Mata Ajar:** {mata_ajar}
""")

st.dataframe(pivot[['Tahun', 'Rank', 'Instruktur', 'Nilai']], use_container_width=True)
