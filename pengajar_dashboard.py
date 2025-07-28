import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
from io import BytesIO

st.set_page_config(page_title="Dashboard Nilai Instruktur", layout="wide")

def load_excel(file):
    xls = pd.ExcelFile(file)
    df_all = pd.concat([xls.parse(sheet) for sheet in xls.sheet_names])
    return df_all

def group_similar_names(names, threshold=85):
    groups = []
    visited = set()

    for name in names:
        if name in visited:
            continue
        group = [name]
        visited.add(name)
        matches = process.extract(name, names, scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
        for match_name, score, _ in matches:
            if match_name != name and match_name not in visited:
                group.append(match_name)
                visited.add(match_name)
        groups.append(group)
    return groups

def get_grouped_label(name, name_groups):
    for group in name_groups:
        if name in group:
            return group[0]  # gunakan nama pertama sebagai label grup
    return name

st.title("📊 Dashboard Nilai Instruktur")

uploaded_file = st.file_uploader("Unggah file Excel", type=["xls", "xlsx"])

if uploaded_file:
    df = load_excel(uploaded_file)

    # Normalisasi kolom
    df.columns = df.columns.str.strip().str.lower()

    if 'nama diklat' in df.columns and 'mata ajar' in df.columns and 'rata-rata' in df.columns:
        diklat_names = df['nama diklat'].dropna().unique().tolist()
        name_groups = group_similar_names(diklat_names)
        df['grup diklat'] = df['nama diklat'].apply(lambda x: get_grouped_label(x, name_groups))

        selected_diklat = st.selectbox("Pilih Grup Diklat", sorted(df['grup diklat'].unique()))

        filtered = df[df['grup diklat'] == selected_diklat]

        st.subheader(f"📚 Data Nilai untuk Diklat: {selected_diklat}")

        mata_ajar_opsi = filtered['mata ajar'].unique()
        selected_mata_ajar = st.selectbox("Pilih Mata Ajar", mata_ajar_opsi)

        nilai_df = filtered[filtered['mata ajar'] == selected_mata_ajar]
        nilai_df = nilai_df[['nama', 'rata-rata']].dropna()
        nilai_df = nilai_df.sort_values(by='rata-rata', ascending=False).reset_index(drop=True)
        nilai_df.index += 1  # untuk ranking mulai dari 1

        st.write("📈 Tabel Nilai Rata-Rata")
        st.dataframe(nilai_df.rename(columns={"nama": "Nama", "rata-rata": "Nilai"}), use_container_width=True)

        # Unduh sebagai Excel
        def to_excel_download(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Ranking')
            return output.getvalue()

        st.download_button(
            label="⬇️ Unduh Data sebagai Excel",
            data=to_excel_download(nilai_df),
            file_name=f"nilai_{selected_diklat}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Kolom 'nama diklat', 'mata ajar', atau 'rata-rata' tidak ditemukan di file.")
