import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Judul
st.title("📊 Dashboard Penilaian Instruktur")

# === 1. Baca file Excel dari GitHub ===
file_url = "https://raw.githubusercontent.com/AzrielAprieliant/dashboard-pengajar/main/data%20instruktur%20asli.xlsx"

# Load data
sheet_2025 = pd.read_excel(file_url, sheet_name="Penilaian Jan Jun 2025")
sheet_2025['Tahun'] = 2025

sheet_2024 = pd.read_excel(file_url, sheet_name="Penilaian 2024")
sheet_2024['Tahun'] = 2024

sheet_2023 = pd.read_excel(file_url, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023['Tahun'] = 2023

# Gabungkan data
all_data = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]]
], ignore_index=True)

# Pastikan kolom nilai numerik
all_data['Rata-Rata'] = pd.to_numeric(all_data['Rata-Rata'], errors='coerce')

# === 2. Clustering Nama Diklat dengan TF-IDF + KMeans ===
unique_diklat = all_data['Nama Diklat'].dropna().unique()
vectorizer = TfidfVectorizer(stop_words='indonesian')
X = vectorizer.fit_transform(unique_diklat)

# Jumlah cluster diatur otomatis berdasarkan jumlah kata awal unik terbanyak
n_clusters = min(len(unique_diklat), 15)
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
kmeans.fit(X)
labels = kmeans.labels_

# Buat mapping nama diklat ke nama grup
diklat_cluster_map = {nama: f"Grup {label+1} - {nama.split()[0]}" for nama, label in zip(unique_diklat, labels)}
all_data['Grup Diklat'] = all_data['Nama Diklat'].map(diklat_cluster_map)

# === 3. Dropdown grup diklat ===
selected_group = st.selectbox("📌 Pilih Grup Diklat", sorted(all_data['Grup Diklat'].dropna().unique()))
filtered_df = all_data[all_data['Grup Diklat'] == selected_group]

# === 4. Dropdown mata ajar ===
selected_mata_ajar = st.selectbox("📚 Pilih Mata Ajar", sorted(filtered_df['Mata Ajar'].dropna().unique()))
filtered_df = filtered_df[filtered_df['Mata Ajar'] == selected_mata_ajar]

# === 5. Ranking nilai tertinggi ===
pivot = (
    filtered_df.groupby(['Tahun', 'Instruktur'])['Rata-Rata']
    .mean()
    .reset_index()
    .dropna()
)
pivot = pivot.sort_values(by=['Tahun', 'Rata-Rata'], ascending=[False, False])
pivot['Rank'] = pivot.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False).astype(int)
pivot = pivot.rename(columns={'Rata-Rata': 'Nilai'})

# === 6. Tampilkan hasil ===
st.write(f"📊 **Ranking Instruktur** untuk Grup: `{selected_group}`, Mata Ajar: `{selected_mata_ajar}`")
st.dataframe(pivot[['Tahun', 'Rank', 'Instruktur', 'Nilai']])
