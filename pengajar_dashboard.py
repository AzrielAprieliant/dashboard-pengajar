import streamlit as st
import pandas as pd
import re

# Fungsi bantu
def get_awal_diklat(nama, num_kata=3):
    words = str(nama).split()
    return ' '.join(words[:num_kata]).strip().lower()

def extract_year(sheet_name):
    match = re.search(r'20\d{2}', str(sheet_name))
    return match.group() if match else '2025'

# ================== STREAMLIT APP ==================

st.title("📊 Dashboard Instruktur Nilai Tertinggi")

# URL file dari GitHub (ubah ini!)
github_excel_url = "https://raw.githubusercontent.com/username/repo/main/Data%20Instruktur%20asli.xlsx"

# Baca file dari GitHub
try:
    xls = pd.ExcelFile(github_excel_url)
    all_data = []
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        df['Sheet Name'] = sheet
        all_data.append(df)

    combined_df = pd.concat(all_data, ignore_index=True)

    # Ambil kolom penting
    selected_cols = ['Nama Diklat', 'Mata Ajar', 'Instruktur', 'Rata-Rata', 'Sheet Name']
    df = combined_df[selected_cols].copy()
    df = df.dropna(subset=['Nama Diklat', 'Instruktur', 'Rata-Rata'])

    # Cluster berdasarkan awalan diklat
    df['Cluster Diklat'] = df['Nama Diklat'].apply(get_awal_diklat)
    df['Tahun'] = df['Sheet Name'].apply(extract_year)

    # Dropdown 1: Cluster Diklat
    cluster_options = sorted(df['Cluster Diklat'].unique())
    selected_cluster = st.selectbox("Pilih Cluster Diklat", cluster_options)

    if selected_cluster:
        df_filtered_cluster = df[df['Cluster Diklat'] == selected_cluster]

        # Dropdown 2: Mata Ajar
        mata_ajar_options = sorted(df_filtered_cluster['Mata Ajar'].dropna().unique())
        selected_mata_ajar = st.selectbox("Pilih Mata Ajar", mata_ajar_options)

        if selected_mata_ajar:
            final_df = df_filtered_cluster[df_filtered_cluster['Mata Ajar'] == selected_mata_ajar]

            # Tampilkan ranking
            st.subheader("🏆 Ranking Instruktur")
            ranking = final_df[['Instruktur', 'Rata-Rata', 'Tahun']].dropna()
            ranking = ranking.sort_values(by='Rata-Rata', ascending=False).reset_index(drop=True)
            ranking.index += 1
            st.dataframe(ranking)

except Exception as e:
    st.error(f"Gagal membaca file dari GitHub. Error: {e}")
