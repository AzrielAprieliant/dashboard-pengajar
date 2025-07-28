import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

# === CONFIGURASI LAYOUT STREAMLIT ===
st.set_page_config(
    page_title="Dashboard Instruktur",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        zoom: 70%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Dashboard Penilaian Instruktur")

# === BACA DATA ===
file = "data instruktur asli.xlsx"

# Baca sheet dan beri kolom tahun
sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

# Gabungkan semua data
df = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
], ignore_index=True)

df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")

# === CLUSTER NAMA DIKLAT MENGGUNAKAN TF-IDF + KMeans ===
diklat_list = df["Nama Diklat"].dropna().unique().tolist()

vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 2))
X = vectorizer.fit_transform(diklat_list)

# Tentukan jumlah cluster berdasarkan panjang data
n_clusters = min(len(diklat_list), 15)
model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
model.fit(X)

# Ambil label cluster dan nama wakil dari tiap cluster
labels = model.labels_
closest, _ = pairwise_distances_argmin_min(model.cluster_centers_, X)

# Mapping diklat ke label nama grup
cluster_map = {}
for idx, label in enumerate(labels):
    cluster_name = diklat_list[closest[label]]
    cluster_map[diklat_list[idx]] = cluster_name

df["Grup Diklat"] = df["Nama Diklat"].map(cluster_map)

# === DROPDOWN: PILIH DIKLAT (GRUP) ===
selected_diklat_group = st.selectbox("📌 Grup Diklat", sorted(df["Grup Diklat"].dropna().unique()))

filtered_df = df[df["Grup Diklat"] == selected_diklat_group]

# === DROPDOWN: PILIH MATA AJAR ===
available_mata_ajar = filtered_df["Mata Ajar"].dropna().unique()
selected_mata_ajar = st.selectbox("📚 Mata Ajar", sorted(available_mata_ajar))

filtered_df = filtered_df[filtered_df["Mata Ajar"] == selected_mata_ajar]

# === HITUNG RANKING NILAI PER INSTRUKTUR PER TAHUN ===
if not filtered_df.empty:
    grouped = (
        filtered_df.groupby(["Instruktur", "Tahun"])["Rata-Rata"]
        .mean()
        .reset_index()
        .rename(columns={"Rata-Rata": "Nilai"})
    )

    # Ranking berdasarkan nilai tertinggi
    grouped = grouped.sort_values(by=["Tahun", "Nilai"], ascending=[False, False])
    grouped["Rank"] = grouped.groupby("Tahun")["Nilai"].rank(method="first", ascending=False).astype(int)

    # Tampilkan hasil
    st.markdown(f"### 📈 Ranking Instruktur")
    st.dataframe(grouped[["Tahun", "Rank", "Instruktur", "Nilai"]], use_container_width=True)
else:
    st.warning("Data tidak ditemukan untuk kombinasi Diklat dan Mata Ajar ini.")
