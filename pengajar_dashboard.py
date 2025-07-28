import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import os

st.set_page_config(page_title="Dashboard Pengajar", layout="wide")
st.title("📊 Dashboard Penilaian Instruktur")

# Load file Excel
file_path = "data instruktur asli.xlsx"
if not os.path.exists(file_path):
    st.error(f"File tidak ditemukan: {file_path}")
    st.stop()

# Baca semua sheet
excel_data = pd.read_excel(file_path, sheet_name=None)
df = pd.concat(excel_data.values(), ignore_index=True)

# Ganti nama kolom jika perlu
if "Rata-Rata" not in df.columns:
    st.error("Kolom 'Rata-Rata' tidak ditemukan di file Excel.")
    st.stop()

# Bersihkan data
df = df.rename(columns=lambda x: x.strip())
df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")
df = df.dropna(subset=["Rata-Rata"])
df = df.fillna("")

# Kelompokkan nama diklat berdasarkan kemiripan
def group_similar_names(names, threshold=85):
    groups = []
    for name in names:
        found_group = False
        for group in groups:
            if fuzz.token_sort_ratio(name, group[0]) >= threshold:
                group.append(name)
                found_group = True
                break
        if not found_group:
            groups.append([name])
    return groups

unique_diklat = df["Nama Diklat"].unique()
grouped_diklat = group_similar_names(unique_diklat)

# Loop seluruh grup dan tampilkan ranking
for i, group in enumerate(grouped_diklat, 1):
    group_name = group[0]
    filtered_df = df[df["Nama Diklat"].isin(group)]

    st.subheader(f"📌 Grup Diklat: {group_name}")
    mata_ajar_grouped = filtered_df.groupby(["Nama Instruktur", "Nama Mata Ajar"])["Rata-Rata"].mean().reset_index()
    instruktur_avg = mata_ajar_grouped.groupby("Nama Instruktur")["Rata-Rata"].mean().reset_index()
    instruktur_avg = instruktur_avg.sort_values(by="Rata-Rata", ascending=False).reset_index(drop=True)
    instruktur_avg.index += 1

    st.write("📚 Daftar Mata Ajar & Nilai:")
    st.dataframe(mata_ajar_grouped, use_container_width=True)

    st.write("🏆 Ranking Instruktur (berdasarkan rata-rata):")
    st.dataframe(instruktur_avg, use_container_width=True)

    st.markdown("---")
