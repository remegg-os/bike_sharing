import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

@st.cache_data
def load_data():
    day_df = pd.read_csv('cleaned_day.csv')
    hour_df = pd.read_csv('cleaned_hour.csv')

    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

    season_mapping = {1: 'Springer', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_mapping = {1: 'Clear/Partly Cloudy', 2: 'Mist/Cloudy', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Ice'}

    if 'season_label' not in day_df.columns:
        day_df['season_label'] = day_df['season'].map(season_mapping)
    if 'weathersit_label' not in day_df.columns:
        day_df['weathersit_label'] = day_df['weathersit'].map(weather_mapping)
    if 'season_label' not in hour_df.columns:
        hour_df['season_label'] = hour_df['season'].map(season_mapping)
    if 'weathersit_label' not in hour_df.columns:
        hour_df['weathersit_label'] = hour_df['weathersit'].map(weather_mapping)

    return day_df, hour_df

try:
    day_df, hour_df = load_data()
except Exception as e:
    st.error(f"Gagal memuat dataset. Pastikan 'cleaned_day.csv' dan 'cleaned_hour.csv' ada di direktori yang sama. Error: {e}")
    st.stop()

# Sidebar Filter Interaktif
st.sidebar.title("🚲 Filter Eksplorasi Data")
st.sidebar.markdown("---")

min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

season_options = ['All', 'Springer', 'Summer', 'Fall', 'Winter']
selected_season = st.sidebar.selectbox("Filter Berdasarkan Musim", season_options)

# Terapkan Filter
filtered_day = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & (day_df['dteday'] <= pd.to_datetime(end_date))]
filtered_hour = hour_df[(hour_df['dteday'] >= pd.to_datetime(start_date)) & (hour_df['dteday'] <= pd.to_datetime(end_date))]

if selected_season != 'All':
    filtered_day = filtered_day[filtered_day['season_label'] == selected_season]
    filtered_hour = filtered_hour[filtered_hour['season_label'] == selected_season]

# Header Dashboard
st.title("🚲 Bike Sharing Analytics Dashboard (2011-2012)")
st.markdown("Eksplorasi pola penyewaan sepeda berdasarkan waktu operasional (*working day* vs *weekend*) serta dampak kondisi cuaca dan musim.")

# Ringkasan Metrik
col1, col2, col3 = st.columns(3)
total_rentals = int(filtered_day['cnt'].sum()) if not filtered_day.empty else 0
avg_daily = round(filtered_day['cnt'].mean(), 1) if not filtered_day.empty else 0
registered_pct = round((filtered_day['registered'].sum() / total_rentals * 100), 1) if total_rentals > 0 else 0

with col1:
    st.metric("Total Penyewaan Sepeda", f"{total_rentals:,}")
with col2:
    st.metric("Rata-rata Penyewaan / Hari", f"{avg_daily:,}")
with col3:
    st.metric("Proporsi Pengguna Terdaftar", f"{registered_pct}%")

st.markdown("---")

if filtered_day.empty or filtered_hour.empty:
    st.warning("Tidak ada data untuk kombinasi filter tanggal dan musim yang dipilih.")
else:
    # Visualisasi Pertanyaan Bisnis 1
    st.subheader("1. Pola Penyewaan Per Jam: Hari Kerja vs Hari Libur/Akhir Pekan")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    sns.lineplot(
        data=filtered_hour,
        x='hr',
        y='cnt',
        hue='workingday',
        palette=['#ff7f0e', '#1f77b4'],
        marker='o',
        errorbar=None,
        ax=ax1
    )
    ax1.set_title("Rata-rata Penyewaan Sepeda per Jam (0 - 23)", fontsize=13, fontweight='bold')
    ax1.set_xlabel("Jam (Hour)", fontsize=11)
    ax1.set_ylabel("Rata-rata Jumlah Penyewaan", fontsize=11)
    ax1.set_xticks(range(0, 24))
    handles, _ = ax1.get_legend_handles_labels()
    if len(handles) == 2:
        ax1.legend(handles=handles, labels=['Hari Libur / Akhir Pekan (0)', 'Hari Kerja (1)'], title='Kategori Hari')
    st.pyplot(fig1)

    st.markdown("---")

    # Visualisasi Pertanyaan Bisnis 2
    st.subheader("2. Dampak Kondisi Cuaca & Perbandingan Antar Musim")
    col_left, col_right = st.columns(2)

    with col_left:
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        weather_order = [w for w in ['Clear/Partly Cloudy', 'Mist/Cloudy', 'Light Snow/Rain'] if w in filtered_day['weathersit_label'].unique()]
        sns.barplot(
            data=filtered_day,
            x='weathersit_label',
            y='cnt',
            order=weather_order,
            palette=['#2b5c8f', '#6c9ac4', '#d95f02'],
            errorbar=None,
            ax=ax2
        )
        ax2.set_title("Rata-rata Penyewaan Harian per Kondisi Cuaca", fontsize=12, fontweight='bold')
        ax2.set_xlabel("Kondisi Cuaca", fontsize=10)
        ax2.set_ylabel("Rata-rata Penyewaan Harian", fontsize=10)
        for container in ax2.containers:
            ax2.bar_label(container, fmt='%.0f', padding=3)
        st.pyplot(fig2)

    with col_right:
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        season_order = [s for s in ['Springer', 'Summer', 'Fall', 'Winter'] if s in filtered_day['season_label'].unique()]
        sns.barplot(
            data=filtered_day,
            x='season_label',
            y='cnt',
            order=season_order,
            palette=['#a6bddb', '#67a9cf', '#1c9099', '#016c59'],
            errorbar=None,
            ax=ax3
        )
        ax3.set_title("Rata-rata Penyewaan Harian per Musim", fontsize=12, fontweight='bold')
        ax3.set_xlabel("Musim", fontsize=10)
        ax3.set_ylabel("Rata-rata Penyewaan Harian", fontsize=10)
        for container in ax3.containers:
            ax3.bar_label(container, fmt='%.0f', padding=3)
        st.pyplot(fig3)

st.caption("Proyek Analisis Data: Bike Sharing Dataset | Rahmadi Mustafa Ghani")