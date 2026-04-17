import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Jakarta Flood Dashboard 2024", layout="wide")

# 1. JUDUL DASHBOARD BERUPA INSIGHT (Syarat Wajib)
st.title("Jakarta Timur & Selatan Memerlukan Prioritas Logistik Akibat Lonjakan Pengungsi")

# 2. FUNGSI LOAD DATA
@st.cache_data
def load_data():
    # Membaca data banjir (Excel)
    # Pastikan file_excel sesuai dengan nama file Anda
    file_excel = "Data_Kejadian Bencana Banjir Tahun 2024.xlsx" 
    df = pd.read_excel(file_excel, engine='openpyxl')
    
    # Standarisasi data agar bisa di-join
    df['kecamatan'] = df['kecamatan'].str.upper().str.strip()
    
    # Membaca data spasial (GeoJSON) - Menggunakan pyogrio untuk menghindari error fiona
    gdf = gpd.read_file("kecamatan.geojson", engine='pyogrio')
    gdf['name'] = gdf['name'].str.upper().str.strip()
    
    return df, gdf

# Eksekusi Load Data
try:
    df, gdf = load_data()

    # 3. FILTER INTERAKTIF (Syarat Wajib)
    st.sidebar.header("Filter Analisis")
    wilayah_pilihan = st.sidebar.multiselect(
        "Pilih Wilayah Administrasi:", 
        options=df['wilayah'].unique(), 
        default=df['wilayah'].unique()
    )
    df_filtered = df[df['wilayah'].isin(wilayah_pilihan)]

    # 4. PENYIAPAN DATA GEOSPATIAL
    # Menghitung total kejadian per kecamatan untuk peta
    stats_kec = df_filtered.groupby('kecamatan')['jumlah_kejadian'].sum().reset_index()
    map_data = gdf.merge(stats_kec, left_on='name', right_on='kecamatan', how='left').fillna(0)

    # 5. VISUALISASI PETA (Syarat Wajib)
    st.subheader("Sebaran Frekuensi Banjir per Kecamatan (Geospatial)")
    fig_map = px.choropleth_mapbox(
        map_data,
        geojson=map_data.__geo_interface__,
        locations=map_data.index,
        color='jumlah_kejadian',
        color_continuous_scale="Reds",
        mapbox_style="carto-positron",
        center={"lat": -6.2088, "lon": 106.8456},
        zoom=10,
        hover_name='name',
        opacity=0.7,
        labels={'jumlah_kejadian': 'Total Kejadian'}
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # 6. DUA CHART TAMBAHAN (Syarat Wajib)
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Perbandingan Pengungsi per Wilayah")
        bar_data = df_filtered.groupby('wilayah')['jumlah_pengungsi'].sum().sort_values(ascending=False)
        st.bar_chart(bar_data)

    with col2:
        st.write("### Tren Kejadian Banjir Bulanan")
        # Mengurutkan berdasarkan bulan (asumsi kolom 'bulan' berisi angka 1-12)
        line_data = df_filtered.groupby('bulan')['jumlah_kejadian'].sum()
        st.line_chart(line_data)

    # 7. SECTION STORYTELLING (Syarat Wajib PDF Tugas)
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.header("🔍 Key Insight")
        st.write("**WHAT:** Berdasarkan data tahun 2024, Jakarta Timur dan Jakarta Selatan mencatat akumulasi jumlah pengungsi tertinggi.")
        st.write("**SO WHAT:** Hal ini krusial karena wilayah tersebut memiliki kepadatan penduduk yang tinggi, sehingga setiap kejadian banjir berdampak langsung pada ribuan jiwa yang membutuhkan evakuasi.")

    with c2:
        st.header("💡 Recommendation")
        st.success("""
        **NOW WHAT:** 1. Segera alokasikan tambahan perahu karet dan tenda darurat di wilayah Jatinegara (Timur) dan Tebet (Selatan).
        2. Lakukan audit sistem drainase pada kecamatan dengan warna merah gelap di peta untuk prioritas normalisasi.
        """)

except Exception as e:
    st.error(f"Gagal memuat dashboard: {e}")
    st.info("Saran: Tutup file Excel jika sedang dibuka di aplikasi lain, lalu jalankan kembali.")