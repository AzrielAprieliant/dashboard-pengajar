import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Dashboard Instruktur", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
html, body, [class*="css"]  {
    zoom: 80%;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Penilaian Instruktur")

# === BACA DATA NILAI ===
file = "Data Instruktur asli.xlsx"

sheet_2025 = pd.read_excel(file, sheet_name="Penilaian Jan Jun 2025")
sheet_2025["Tahun"] = 2025

sheet_2024 = pd.read_excel(file, sheet_name="Penilaian 2024")
sheet_2024["Tahun"] = 2024

sheet_2023 = pd.read_excel(file, sheet_name="Penilaian 2023")
sheet_2023 = sheet_2023.rename(columns={"Instruktur /WI": "Instruktur", "Rata2": "Rata-Rata"})
sheet_2023["Tahun"] = 2023

df = pd.concat([
    sheet_2025[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2024[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
    sheet_2023[["Instruktur", "Mata Ajar", "Nama Diklat", "Rata-Rata", "Tahun"]],
], ignore_index=True)

df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")

# === BACA FILE UNIT KERJA ===
df_unitkerja = pd.read_excel("Nama dan Unit Kerja.xlsx")
df_unitkerja = df_unitkerja.rename(columns={"Nama": "Nama_Unit", "nama unit": "Nama Unit"})

# === FUZZY MATCHING UNIT KERJA ===
def fuzzy_match(nama, list_nama, threshold=60):
    match, score, _ = process.extractOne(nama, list_nama, scorer=fuzz.token_sort_ratio)
    return match if score >= threshold else None

df["Nama_Cocok"] = df["Instruktur"].apply(lambda x: fuzzy_match(str(x), df_unitkerja["Nama_Unit"]))
df = pd.merge(df, df_unitkerja[["Nama_Unit", "Nama Unit"]], left_on="Nama_Cocok", right_on="Nama_Unit", how="left")
df = df.rename(columns={"Nama Unit": "Unit Kerja"})

# === CLUSTERING NAMA DIKLAT ===
diklat_list = df["Nama Diklat"].dropna().unique().tolist()
vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 2))
X = vectorizer.fit_transform(diklat_list)

n_clusters = min(len(diklat_list), 15)
model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
model.fit(X)

labels = model.labels_
closest, _ = pairwise_distances_argmin_min(model.cluster_centers_, X)

cluster_map = {}
for idx, label in enumerate(labels):
    cluster_name = diklat_list[closest[label]]
    cluster_map[diklat_list[idx]] = cluster_name

df["Grup Diklat"] = df["Nama Diklat"].map(cluster_map)

# === DROPDOWN: GRUP DIKLAT ===
selected_diklat_group = st.selectbox("📌 Nama Diklat", sorted(df["Grup Diklat"].dropna().unique()))
filtered_df = df[df["Grup Diklat"] == selected_diklat_group]

# === DROPDOWN: MATA AJAR ===
available_mata_ajar = filtered_df["Mata Ajar"].dropna().unique()
selected_mata_ajar = st.selectbox("📘 Mata Ajar", sorted(available_mata_ajar))
filtered_df = filtered_df[filtered_df["Mata Ajar"] == selected_mata_ajar]

# === DROPDOWN: UNIT KERJA ===
available_unit_kerja = filtered_df["Unit Kerja"].dropna().unique()
if len(available_unit_kerja) > 0:
    unit_options = ["(Tampilkan Semua)"] + sorted(available_unit_kerja)
    selected_unit_kerja = st.selectbox("🏢 Unit Kerja", unit_options)
    if selected_unit_kerja != "(Tampilkan Semua)":
        filtered_df = filtered_df[filtered_df["Unit Kerja"] == selected_unit_kerja]

# === HASIL & RANKING ===
if not filtered_df.empty:
    st.markdown("### 🔍 Hasil Data:")
    st.dataframe(
        filtered_df[["Instruktur", "Mata Ajar", "Nama Diklat", "Tahun", "Unit Kerja", "Rata-Rata"]],
        use_container_width=True
    )

    if filtered_df["Rata-Rata"].notna().sum() > 0:
        grouped = (
            filtered_df.groupby("Instruktur")["Rata-Rata"]
            .mean()
            .reset_index()
            .rename(columns={"Rata-Rata": "Nilai"})
        )

        tahun_instruktur = (
            filtered_df.groupby("Instruktur")["Tahun"]
            .apply(lambda x: ", ".join(str(t) for t in sorted(x.unique())))
            .reset_index()
        )

        grouped = pd.merge(grouped, tahun_instruktur, on="Instruktur")
        grouped = grouped.sort_values(by="Nilai", ascending=False)
        grouped["Rank"] = grouped["Nilai"].rank(method="first", ascending=False).astype(int)

        st.markdown("### 🏆 Ranking Instruktur (Berdasarkan Rata-Rata Nilai)")
        st.dataframe(grouped[["Rank", "Instruktur", "Tahun", "Nilai"]], use_container_width=True)
    else:
        st.warning("⚠️ Tidak ada nilai rata-rata yang tersedia untuk data ini.")
else:
    st.warning("⚠️ Data kosong. Coba pilih kombinasi Diklat, Mata Ajar, atau Unit Kerja yang berbeda.")
