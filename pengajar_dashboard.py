import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Instruktur", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    /* Ubah warna latar belakang utama */
    .main {
        background-color: #f0f8ff; /* biru muda */
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #e6f2ff; /* biru pastel */
    }

    /* Judul dan teks umum */
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stText {
        color: #003366;  /* biru gelap */
    }

    /* Tombol */
    button {
        background-color: #1f77b4;
        color: white;
    }

    /* Dataframe border dan font */
    .stDataFrame {
        border: 1px solid #ccc;
        font-family: sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Dashboard Penilaian Instruktur")

df = pd.read_excel("Penilaian Gabung dengan Nama Unit.xlsx")

df["Rata-Rata"] = pd.to_numeric(df["Rata-Rata"], errors="coerce")
df.loc[df["Rata-Rata"] > 100, "Rata-Rata"] = df["Rata-Rata"] / 10000
df["Rata-Rata"] = df["Rata-Rata"].round(2)

nama_diklat = st.selectbox("📘 Pilih Nama Diklat", ["Semua"] + sorted(df["Nama Diklat"].dropna().unique().tolist()))
df_diklat = df if nama_diklat == "Semua" else df[df["Nama Diklat"] == nama_diklat]

unit_kerja = st.selectbox("🏢 Pilih Nama Unit", ["Semua"] + sorted(df_diklat["Nama Unit"].dropna().unique().tolist()))
df_unit = df_diklat if unit_kerja == "Semua" else df_diklat[df_diklat["Nama Unit"] == unit_kerja]

mata_ajar = st.selectbox("📖 Pilih Mata Ajar", sorted(df_unit["Mata Ajar"].dropna().unique().tolist()))

filtered_df = df_unit[df_unit["Mata Ajar"] == mata_ajar]


if not filtered_df.empty:
    top_instruktur = (
        filtered_df.sort_values(by="Rata-Rata", ascending=False)
        .groupby("Instruktur", as_index=False)
        .first()
    )

    top_instruktur = top_instruktur.sort_values(by="Rata-Rata", ascending=False).reset_index(drop=True)
    top_instruktur.index += 1
    top_instruktur.insert(0, "Peringkat", top_instruktur.index)

    
    st.markdown(f"### 📋 Tabel Peringkat Instruktur")
    st.dataframe(top_instruktur[[
        "Peringkat", "Instruktur", "Mata Ajar", "Nama Diklat", "Nama Unit", "Tahun", "Rata-Rata"
    ]],
    use_container_width=True,
    height=500     
     )
    import plotly.express as px

# 📊 Bar Chart - Peringkat Instruktur
st.markdown("### 📈 Grafik Peringkat Instruktur (Bar Chart)")
fig_bar = px.bar(
    top_instruktur,
    x="Instruktur",
    y="Rata-Rata",
    color="Rata-Rata",
    text="Rata-Rata",
    color_continuous_scale="Blues"
)
fig_bar.update_layout(xaxis_title=None, yaxis_title="Nilai Rata-Rata", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_bar, use_container_width=True)

# 📈 Box Plot - Distribusi Nilai
st.markdown("### 📦 Distribusi Nilai Rata-Rata (Box Plot)")
fig_box = px.box(
    filtered_df,
    y="Rata-Rata",
    points="all",  # menampilkan outlier
    title="Distribusi Nilai Rata-Rata Instruktur"
)
fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_box, use_container_width=True)

# 📉 Line Chart - Rata-Rata Per Tahun (jika ada lebih dari 1 tahun)
if df["Tahun"].nunique() > 1:
    st.markdown("### 🗓️ Tren Nilai Rata-Rata per Tahun")
    df_trend = (
        df.groupby("Tahun")["Rata-Rata"]
        .mean()
        .reset_index()
    )
    fig_line = px.line(
        df_trend,
        x="Tahun",
        y="Rata-Rata",
        markers=True,
        title="Rata-Rata Instruktur per Tahun"
    )
    fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_line, use_container_width=True)

else:
    st.warning("⚠️ Tidak ada data yang cocok dengan filter.")
