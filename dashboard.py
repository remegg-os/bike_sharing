import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Load data dengan caching
@st.cache_data
def load_data():
    day_df = pd.read_csv('cleaned_day.csv')
    hour_df = pd.read_csv('cleaned_hour.csv')

    # Preprocessing
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

    season_mapping = {1: 'Springer', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_mapping = {1: 'Clear/Partly Cloudy', 2: 'Mist/Cloudy', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Ice'}

    day_df['season_label'] = day_df['season'].map(season_mapping)
    day_df['weathersit_label'] = day_df['weathersit'].map(weather_mapping)

    hour_df['season_label'] = hour_df['season'].map(season_mapping)
    hour_df['weathersit_label'] = hour_df['weathersit'].map(weather_mapping)

    return day_df, hour_df

try:
    day_df, hour_df = load_data()
except Exception as e:
    st.error(f"Gagal memuat dataset. Pastikan file 'cleaned_day.csv' dan 'cleaned_hour.csv' berada di direktori yang sama. Error: {e}")
    st.stop()

# Sidebar / Filter Interaktif
st.sidebar.title("🚲 Filter Dashboard")
st.sidebar.markdown("---")

# Filter Rentang Tanggal
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

date_range = st.sidebar.date_input(
    "Rentang Waktu",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Filter Musim
season_list = ['All'] + list(day_df['season_label'].dropna().unique())
selected_season = st.sidebar.selectbox("Pilih Musim", season_list)

# Filtering dataframe
filtered_day = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & (day_df['dteday'] <= pd.to_datetime(end_date))]
filtered_hour = hour_df[(hour_df['dteday'] >= pd.to_datetime(start_date)) & (hour_df['dteday'] <= pd.to_datetime(end_date))]

if selected_season != 'All':
    filtered_day = filtered_day[filtered_day['season_label'] == selected_season]
    filtered_hour = filtered_hour[filtered_hour['season_label'] == selected_season]

# Main Content
st.title("🚲 Dashboard Analisis Penyewaan Sepeda (Bike Sharing)")
st.markdown("Dashboard interaktif ini menyajikan eksplorasi data penyewaan sepeda berdasarkan waktu, musim, kondisi cuaca, serta segmen pengguna.")

# Metrics Row
col1, col2, col3 = st.columns(3)
total_rentals = int(filtered_day['cnt'].sum()) if not filtered_day.empty else 0
total_casual = int(filtered_day['casual'].sum()) if not filtered_day.empty else 0
total_registered = int(filtered_day['registered'].sum()) if not filtered_day.empty else 0

with col1:
    st.metric("Total Penyewaan", value=f"{total_rentals:,}")
with col2:
    st.metric("Pengguna Kasual", value=f"{total_casual:,}")
with col3:
    st.metric("Pengguna Terdaftar", value=f"{total_registered:,}")

st.markdown("---")

if filtered_day.empty or filtered_hour.empty:
    st.warning("Tidak ada data yang tersedia untuk filter yang dipilih.")
else:
    # Visualisasi 1: Pola Penyewaan per Jam (Workingday vs Non-Workingday)
    st.subheader("Hourly Rental Patterns: Hari Kerja vs Hari Libur")
    fig, ax = plt.subplots(figsize=(12, 5))
    hourly_workingday = filtered_hour.groupby(['hr', 'workingday'])['cnt'].mean().reset_index()
    sns.lineplot(
        data=hourly_workingday,
        x='hr',
        y='cnt',
        hue='workingday',
        palette=['tab:orange', 'tab:blue'],
        marker='o',
        ax=ax
    )
    ax.set_title("Rata-rata Penyewaan Sepeda per Jam berdasarkan Tipe Hari", fontsize=14, fontweight='bold')
    ax.set_xlabel("Jam (Hour)", fontsize=12)
    ax.set_ylabel("Rata-rata Penyewaan", fontsize=12)
    ax.legend(title="Tipe Hari", labels=['Libur / Weekend', 'Hari Kerja (Workingday)'])
    st.pyplot(fig)

    # Layout 2 Kolom untuk Visualisasi Musim & Cuaca
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Distribusi Penyewaan Berdasarkan Musim")
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        seasonal_data = filtered_day.groupby('season_label')['cnt'].mean().reset_index()
        sns.barplot(
            data=seasonal_data,
            x='season_label',
            y='cnt',
            order=['Springer', 'Summer', 'Fall', 'Winter'],
            palette='viridis',
            ax=ax2
        )
        ax2.set_title("Rata-rata Penyewaan per Musim", fontsize=12, fontweight='bold')
        ax2.set_xlabel("Musim", fontsize=10)
        ax2.set_ylabel("Rata-rata Penyewaan Harian", fontsize=10)
        st.pyplot(fig2)

    with col_b:
        st.subheader("Pengaruh Kondisi Cuaca terhadap Penyewaan")
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        weather_data = filtered_day.groupby('weathersit_label')['cnt'].mean().reset_index()
        sns.barplot(
            data=weather_data,
            x='weathersit_label',
            y='cnt',
            palette='magma',
            ax=ax3
        )
        ax3.set_title("Rata-rata Penyewaan Berdasarkan Cuaca", fontsize=12, fontweight='bold')
        ax3.set_xlabel("Kondisi Cuaca", fontsize=10)
        ax3.set_ylabel("Rata-rata Penyewaan Harian", fontsize=10)
        plt.xticks(rotation=15)
        st.pyplot(fig3)

    st.markdown("---")

    # Visualisasi Tren Bulanan Pengguna Casual vs Registered
    st.subheader("Tren Bulanan: Pengguna Casual vs Registered")
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    monthly_user = filtered_day.groupby('mnth')[['casual', 'registered']].mean().reset_index()
    monthly_melted = monthly_user.melt(id_vars='mnth', value_vars=['casual', 'registered'], var_name='User Type', value_name='Count')
    sns.lineplot(
        data=monthly_melted,
        x='mnth',
        y='Count',
        hue='User Type',
        marker='o',
        ax=ax4
    )
    ax4.set_title("Perbandingan Rata-rata Pengguna Casual vs Registered per Bulan", fontsize=14, fontweight='bold')
    ax4.set_xlabel("Bulan (Month)", fontsize=12)
    ax4.set_ylabel("Rata-rata Jumlah Pengguna", fontsize=12)
    st.pyplot(fig4)

st.caption("Proyek Analisis Data - Bike Sharing Dataset | Copyright © 2024")
