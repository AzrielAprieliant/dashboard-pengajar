import pandas as pd
import streamlit as st

st.title("📊 Pengajar dengan Nilai Tertinggi")

# === BACA FILE EXCEL ===
file = "Data Instruktur asli.xlsx"
# Sheet per tahun
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

# Gabung semua sheet
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Pastikan angka numerik
all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# === 2. Buat Awalan Nama Diklat (Clustering Otomatis) ===
def get_awalan_diklat(nama, n_kata=3):
    return " ".join(str(nama).split()[:n_kata]).lower().strip()

all_data["Awalan Diklat"] = all_data["Nama Diklat"].apply(get_awalan_diklat)

# === 3. Mapping Awalan → Nama Diklat yang Rapi ===
custom_nama_diklat = {
    "audit investigatif level": "Audit Investigatif",
    "bimbingan teknis reviu": "Bimtek Reviu Laporan",
    "pelatihan jabatan fungsional": "Pelatihan JF Auditor",
    # Tambahkan sesuai kebutuhan kamu di sini
}

# Kolom baru untuk ditampilkan di dropdown
all_data["Nama Diklat Display"] = all_data["Awalan Diklat"].map(custom_nama_diklat).fillna(all_data["Awalan Diklat"].str.title())

# === 4. Dropdown Nama Diklat (Cluster Otomatis, Label Rapi) ===
nama_diklat_display = st.selectbox("Pilih Nama Diklat", sorted(all_data["Nama Diklat Display"].unique()))

# Ambil awalan asli dari nama yang dipilih
selected_awalan = all_data[all_data["Nama Diklat Display"] == nama_diklat_display]["Awalan Diklat"].iloc[0]

filtered_cluster = all_data[all_data["Awalan Diklat"] == selected_awalan]

# === 5. Dropdown Mata Ajar ===
mata_ajar = st.selectbox("Pilih Mata Ajar", sorted(filtered_cluster['Mata Ajar'].dropna().unique()))
filtered = filtered_cluster[filtered_cluster['Mata Ajar'] == mata_ajar]

# === 6. Ranking Instruktur Berdasarkan Nilai ===
pivot = filtered.groupby(['Tahun', 'Instruktur'])['Rata-Rata'].mean().reset_index()
pivot = pivot.dropna(subset=['Rata-Rata'])
pivot = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False])
pivot['Rank'] = pivot.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)
pivot = pivot.rename(columns={'Rata-Rata': 'Nilai'})

# === 7. Tampilkan Tabel Hasil ===
st.markdown(f"""
#### 📘 Ranking Instruktur
**Diklat:** {nama_diklat_display}  
**Mata Ajar:** {mata_ajar}
""")

st.dataframe(pivot[['Tahun', 'Rank', 'Instruktur', 'Nilai']], use_container_width=True)

