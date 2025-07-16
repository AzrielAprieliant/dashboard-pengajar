import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Judul dashboard
st.title("Dashboard Pengajar dengan Nilai Tertinggi (Dengan Tahun)")

# Load data
df = pd.read_excel("Data Instruktur.xlsx")

# Pastikan kolom Tahun ada dan benar
df['Tahun'] = df['Tahun'].astype(str)

# Dropdown pilih mata ajar dan tahun
selected_mata_ajar = st.selectbox("Pilih Mata Ajar", df['Mata Ajar'].dropna().unique())
selected_tahun = st.selectbox("Pilih Tahun", df['Tahun'].dropna().unique())

# Filter data
filtered = df[(df['Mata Ajar'] == selected_mata_ajar) & (df['Tahun'] == selected_tahun)]

# Hitung rata-rata per instruktur
pivot = filtered.groupby(['Instruktur', 'Tahun'])['Rata-Rata'].mean().reset_index()

# Urutkan rank
pivot['Rank'] = pivot.groupby('Tahun')['Rata-Rata'].rank(method='first', ascending=False)

# Tampilkan tabel
st.subheader("Pengajar & Nilai Rata-Rata")
st.dataframe(pivot.sort_values(by='Rank'))

# Tampilkan grafik top 10
st.subheader("Grafik Top 10 Pengajar (Tahun & Mata Ajar Terpilih)")
top10 = pivot.sort_values(by='Rata-Rata', ascending=False).head(10)

fig, ax = plt.subplots()
ax.barh(top10['Instruktur'], top10['Rata-Rata'])
ax.invert_yaxis()
st.pyplot(fig)
