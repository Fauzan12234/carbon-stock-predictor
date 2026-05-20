import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import time

# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EcoAnalytics — Stok Karbon Global",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# DESIGN SYSTEM — CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600&display=swap');

/* ── Reset & Base ── */
*, html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
}
.stApp {
    background-color: #EFF2EE !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2.5rem 2.75rem 4rem !important;
    max-width: 1300px !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0A1A14 !important;
    border-right: 1px solid #1C3028 !important;
    min-width: 240px !important;
    max-width: 240px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 2rem 1.5rem !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
    color: #D4E6D4 !important;
}
[data-testid="stSidebar"] .stRadio > label {
    color: #5A7A66 !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 2px !important;
    display: flex !important;
    flex-direction: column !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #C8DEC8 !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    padding: 0.6rem 0.85rem !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.07) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stMarkdown hr {
    border-color: #1C3028 !important;
    margin: 1.25rem 0 !important;
}

/* ── TIPOGRAFI UTAMA ── */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #0A1A14 !important;
    font-weight: 500 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.2 !important;
}
h4, h5, h6 {
    font-family: 'Sora', sans-serif !important;
    color: #0A1A14 !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
}
p, span, div, li {
    color: #2C3E2E !important;
}
label {
    color: #2C3E2E !important;
}

/* ── METRIC CARDS ── */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #DDE8DD !important;
    border-radius: 14px !important;
    padding: 1.25rem 1.5rem 1.4rem !important;
    box-shadow: 0 2px 8px rgba(10,26,20,0.06) !important;
    transition: all 0.2s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #1A5C3A, #5AB88A);
    border-radius: 0 0 14px 14px;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(10,26,20,0.1) !important;
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span,
[data-testid="stMetricLabel"] div {
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #7A9A82 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.9rem !important;
    font-weight: 500 !important;
    color: #0A1A14 !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricValue"] * { color: #0A1A14 !important; }
[data-testid="stMetricDelta"] * { font-size: 0.8rem !important; }

/* ── CARD KOMPONEN ── */
.card {
    background: #FFFFFF;
    border: 1px solid #DDE8DD;
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(10,26,20,0.05);
}
.card-flat {
    background: #F5F8F5;
    border: 1px solid #DDE8DD;
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.5rem;
}
.card-dark {
    background: linear-gradient(140deg, #0A1A14 0%, #163326 55%, #0E5438 100%);
    border-radius: 16px;
    padding: 2.25rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(10,26,20,0.25);
}
.card-dark::after {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: rgba(90,184,138,0.07);
}

/* ── SECTION LABEL ── */
.sec-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #7A9A82;
    display: block;
    margin-bottom: 0.3rem;
}
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 500;
    color: #0A1A14;
    line-height: 1.15;
    margin: 0 0 0.4rem;
}
.page-sub {
    font-size: 0.9rem;
    color: #6B8070;
    margin: 0 0 2rem;
    line-height: 1.6;
}
.card-title {
    font-size: 1rem;
    font-weight: 600;
    color: #0A1A14;
    margin: 0 0 0.2rem;
}
.card-sub {
    font-size: 0.8rem;
    color: #7A9A82;
    margin: 0 0 1.25rem;
}

/* ── TOMBOL ── */
.stButton > button {
    background: #0A1A14 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 0.7rem 1.5rem !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background: #1A5C3A !important;
    box-shadow: 0 6px 20px rgba(10,26,20,0.22) !important;
    transform: translateY(-1px) !important;
}

/* ── FORM ELEMENTS ── */
.stSelectbox label,
.stSlider > label,
.stNumberInput label,
.stMultiSelect label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #5A7A66 !important;
}
[data-baseweb="select"] > div,
[data-baseweb="input"] > div > input {
    border-radius: 9px !important;
    border-color: #DDE8DD !important;
    background: #F5F8F5 !important;
    color: #0A1A14 !important;
}
[data-baseweb="select"] * { color: #0A1A14 !important; }
.stSlider [data-testid="stMarkdownContainer"] p { color: #5A7A66 !important; }

/* ── EXPANDER & ALERTS ── */
.stExpander {
    border: 1px solid #DDE8DD !important;
    border-radius: 10px !important;
    background: #F5F8F5 !important;
}
details summary p {
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #5A7A66 !important;
}
.stSuccess > div, .stError > div, .stInfo > div, .stWarning > div {
    border-radius: 10px !important;
    font-size: 0.875rem !important;
}
hr { border-color: #DDE8DD !important; margin: 1.5rem 0 !important; }

/* ── RESULT HERO ── */
.result-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #5AB88A !important;
    display: block;
    margin-bottom: 0.75rem;
}
.result-num {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 500;
    color: #FFFFFF !important;
    line-height: 1;
}
.result-unit {
    font-size: 1.1rem;
    font-weight: 300;
    color: rgba(255,255,255,0.55) !important;
}
.result-meta {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.5) !important;
    margin-top: 0.85rem;
}
.result-meta strong { color: #5AB88A !important; }

/* ── POLICY STRIP ── */
.policy-strip {
    background: #FFFFFF;
    border-radius: 10px;
    border-left: 3px solid #1A5C3A;
    padding: 1.25rem 1.5rem;
    margin-top: 1rem;
}
.policy-strip .ps-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7A9A82 !important;
    display: block;
    margin-bottom: 0.2rem;
}
.policy-strip .ps-val {
    font-family: 'Playfair Display', serif;
    font-size: 1.85rem;
    font-weight: 500;
    color: #0A1A14 !important;
}

/* ── TAG AKTIF ── */
.tag-active {
    display: inline-block;
    background: #E6F4EC;
    color: #1A5C3A !important;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.22rem 0.65rem;
    border-radius: 100px;
    border: 1px solid #B8DEC8;
    margin-bottom: 1.25rem;
    margin-right: 4px;
}

/* ── TABEL DATA ── */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
thead tr th {
    background: #F5F8F5 !important;
    color: #5A7A66 !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid #DDE8DD !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD & SIAPKAN DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    paths = [
        "/content/drive/MyDrive/Tugas Week 12/global_deforestation_2000_2025.csv",
        "global_deforestation_2000_2025.csv"
    ]
    
    # Fungsi pemetaan wilayah geografis
    def assign_region(c):
        c_lower = str(c).lower()
        if c_lower in ['brazil', 'colombia', 'peru', 'argentina', 'chile', 'bolivia']: return 'Amerika Selatan'
        elif c_lower in ['indonesia', 'malaysia', 'thailand', 'vietnam', 'philippines']: return 'Asia Tenggara'
        elif c_lower in ['india', 'china', 'japan', 'korea']: return 'Asia'
        elif c_lower in ['canada', 'usa', 'mexico', 'united states']: return 'Amerika Utara'
        elif c_lower in ['congo', 'nigeria', 'south africa', 'algeria']: return 'Afrika'
        elif c_lower in ['russia', 'kazakhstan', 'ukraine', 'france', 'germany']: return 'Eropa/Asia'
        elif c_lower in ['australia', 'new zealand']: return 'Oseania'
        else: return 'Lainnya'

    for p in paths:
        if os.path.exists(p):
            df_real = pd.read_csv(p)
            if 'Region' not in df_real.columns:
                df_real['Region'] = df_real['Country'].apply(assign_region)
            return df_real

    # Fallback Data Dummy jika file tidak terbaca
    np.random.seed(42)
    countries = ['Brazil', 'Indonesia', 'Canada', 'Russia', 'USA', 'Congo', 'Australia', 'India', 'China', 'Malaysia', 'Colombia', 'Peru']
    rows = []
    for country in countries:
        base_forest = np.random.uniform(80000, 600000)
        base_carbon = np.random.uniform(8e9, 4.5e10)
        for year in range(2000, 2026):
            defor = np.random.uniform(0.2, 3.2)
            affor = np.random.uniform(0.1, 2.1)
            forest_area = base_forest * (1 - 0.01 * (year - 2000) * (defor - affor * 0.4))
            carbon = base_carbon * (forest_area / base_forest) * np.random.uniform(0.97, 1.03)
            rows.append({
                'Country': country,
                'Year': year,
                'Forest_Area_km2': max(forest_area, 5000),
                'Land_Area_km2': base_forest * np.random.uniform(1.3, 2.2),
                'Annual_Deforestation_Rate': defor,
                'Annual_Afforestation_Rate': affor,
                'Total_Carbon_Stock_Tonnes': max(carbon, 1e8),
                'Primary_Driver_of_Change': np.random.choice(['Pertanian', 'Kebakaran', 'Pertambangan', 'Penebangan'], p=[0.45, 0.25, 0.15, 0.15]),
                'Region': assign_region(country)
            })
    return pd.DataFrame(rows)


def prediksi_stok(fitur: dict) -> float:
    log_forest = np.log1p(max(fitur['Forest_Area_km2'], 1.0))
    rasio = fitur['Forest_Area_km2'] / (fitur['Land_Area_km2'] + 1e-6)
    base = (
        4.2
        + 0.94 * log_forest
        + 0.08 * rasio
        - 0.04 * fitur['Annual_Deforestation_Rate']
        + 0.025 * fitur.get('Annual_Afforestation_Rate', 0)
    )
    return max(np.expm1(base), 0)


df = load_data()

# Penanganan missing values dan konversi aman ke teks agar sorted tidak error
COUNTRIES  = sorted([str(x) for x in df['Country'].dropna().unique()])
DRIVERS    = sorted([str(x) for x in df['Primary_Driver_of_Change'].dropna().unique()])
REGIONS    = sorted([str(x) for x in df['Region'].dropna().unique()])
YEAR_MIN   = int(df['Year'].min()) if not df['Year'].isnull().all() else 2000
YEAR_MAX   = int(df['Year'].max()) if not df['Year'].isnull().all() else 2025
COLOR_SEQ  = ['#0A1A14','#1A5C3A','#2E8B57','#5AB88A','#94D4B0','#C4EACF','#DDE8DD']


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:2rem;">
      <div style="display:flex;align-items:center;gap:9px;margin-bottom:5px;">
        <div style="width:9px;height:9px;border-radius:50%;background:#5AB88A;flex-shrink:0;"></div>
        <span style="font-family:'Playfair Display',serif;font-size:1.15rem;
                     color:#E8F5E8;letter-spacing:-0.02em;">EcoAnalytics</span>
      </div>
      <p style="font-size:0.68rem;color:#3D6650;letter-spacing:0.1em;
                text-transform:uppercase;margin:0;padding-left:18px;">
        Stok Karbon Global
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p class='sec-label' style='color:#3D6650 !important;'>Menu Utama</p>",
                unsafe_allow_html=True)

    nav = st.radio(
        "nav",
        ["Dashboard Analitik", "Simulator Proyeksi", "Analisis Kebijakan"],
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.72rem;color:#3D6650;line-height:1.8;">
      <span style="color:#5AB88A;font-weight:600;">Kelompok 6</span><br>
      Python System Analytics<br>
      Fakultas Teknologi Informasi
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# HALAMAN 1 — DASHBOARD ANALITIK
# ══════════════════════════════════════════════
if nav == "Dashboard Analitik":

    st.markdown("""
    <span class='sec-label'>Pemantauan Real-Time</span>
    <h2 class='page-title'>Dashboard Stok Karbon Global</h2>
    <p class='page-sub'>
      Pantau distribusi biomassa, tren deforestasi, dan perubahan tutupan hutan
      di seluruh dunia secara komprehensif.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card' style='padding:1.25rem 1.75rem; margin-bottom:1.25rem;'>", unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 1])
    with fc1:
        filter_region = st.multiselect(
            "Filter Kawasan",
            options=REGIONS,
            default=REGIONS,
            placeholder="Semua Kawasan"
        )
    with fc2:
        filter_country = st.multiselect(
            "Filter Negara",
            options=COUNTRIES,
            default=COUNTRIES,
            placeholder="Semua Negara"
        )
    with fc3:
        filter_driver = st.multiselect(
            "Pemicu Perubahan",
            options=DRIVERS,
            default=DRIVERS,
            placeholder="Semua Pemicu"
        )
    with fc4:
        filter_year = st.selectbox(
            "Tahun",
            options=list(range(YEAR_MIN, YEAR_MAX + 1)),
            index=YEAR_MAX - YEAR_MIN
        )
    st.markdown("</div>", unsafe_allow_html=True)

    df_f = df[
        (df['Region'].astype(str).isin(filter_region if filter_region else REGIONS)) &
        (df['Country'].astype(str).isin(filter_country if filter_country else COUNTRIES)) &
        (df['Primary_Driver_of_Change'].astype(str).isin(filter_driver if filter_driver else DRIVERS))
    ]
    df_yr = df_f[df_f['Year'] == filter_year]

    k1, k2, k3, k4, k5 = st.columns(5)
    total_carbon = df_yr['Total_Carbon_Stock_Tonnes'].sum()
    total_forest = df_yr['Forest_Area_km2'].sum()
    avg_defor    = df_yr['Annual_Deforestation_Rate'].mean()
    avg_affor    = df_yr['Annual_Afforestation_Rate'].mean()
    n_countries  = df_yr['Country'].nunique()

    # Hitung rata-rata dasar dengan aman menghindari error jika data tidak ada
    base_defor_mean = df[df['Year'] == YEAR_MIN]['Annual_Deforestation_Rate'].mean()
    if np.isnan(base_defor_mean):
        base_defor_mean = 0

    k1.metric("Total Stok Karbon", f"{total_carbon/1e12:.2f} Tt")
    k2.metric("Total Area Hutan", f"{total_forest/1e6:.2f} jt km²")
    k3.metric("Rata-rata Deforestasi", f"{avg_defor:.2f}%/thn",
              delta=f"{avg_defor - base_defor_mean:.2f}%",
              delta_color="inverse")
    k4.metric("Rata-rata Aforestasi", f"{avg_affor:.2f}%/thn")
    k5.metric("Jumlah Negara", f"{n_countries} Entitas")

    st.write("")

    row1_l, row1_r = st.columns([3, 2], gap="large")

    with row1_l:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Peta Distribusi Stok Karbon</span>
          <p class='card-sub'>Kepadatan stok karbon per negara pada tahun yang dipilih.</p>
        """, unsafe_allow_html=True)

        fig_map = px.choropleth(
            df_yr,
            locations="Country",
            locationmode="country names",
            color="Total_Carbon_Stock_Tonnes",
            color_continuous_scale=[
                [0.0, "#E6F4EC"], [0.25, "#94D4B0"],
                [0.6,  "#2E8B57"], [1.0,  "#0A1A14"]
            ],
            labels={"Total_Carbon_Stock_Tonnes": "Stok Karbon (T)"}
        )
        fig_map.update_layout(
            geo=dict(
                showframe=False, showcoastlines=True,
                coastlinecolor="#C8D8C8",
                projection_type='natural earth',
                bgcolor='rgba(0,0,0,0)',
                showland=True, landcolor="#F0F3EE",
                showocean=True, oceancolor="#E8EEF8"
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_colorbar=dict(
                title="",
                tickfont=dict(family="Sora", size=10, color="#7A9A82"),
                thickness=8, len=0.55, x=1.01
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_r:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Komposisi Pemicu Deforestasi</span>
          <p class='card-sub'>Distribusi faktor penyebab kehilangan tutupan hutan.</p>
        """, unsafe_allow_html=True)

        driver_data = df_f.groupby('Primary_Driver_of_Change').size().reset_index(name='Jumlah')
        fig_donut = go.Figure(go.Pie(
            labels=driver_data['Primary_Driver_of_Change'],
            values=driver_data['Jumlah'],
            hole=0.62,
            marker_colors=['#0A1A14','#1A5C3A','#5AB88A','#B8DECC'],
            textfont=dict(family="Sora", size=11),
            hovertemplate="<b>%{label}</b><br>%{value} kasus<extra></extra>"
        ))
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True,
            legend=dict(
                font=dict(family="Sora", size=11, color="#2C3E2E"),
                bgcolor="rgba(0,0,0,0)",
                orientation="v",
                x=0.7
            ),
            annotations=[dict(
                text=f"<b>{driver_data['Jumlah'].sum()}</b><br><span style='font-size:10px'>Total</span>",
                x=0.5, y=0.5, font=dict(family="Playfair Display", size=18, color="#0A1A14"),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    row2_l, row2_r = st.columns([3, 2], gap="large")

    with row2_l:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Tren Stok Karbon (2000–2025)</span>
          <p class='card-sub'>Perubahan cadangan karbon tahunan per negara.</p>
        """, unsafe_allow_html=True)

        trend = df_f.groupby(['Year','Country'])['Total_Carbon_Stock_Tonnes'].mean().reset_index()
        fig_trend = px.line(
            trend, x='Year', y='Total_Carbon_Stock_Tonnes', color='Country',
            color_discrete_sequence=COLOR_SEQ,
            labels={'Total_Carbon_Stock_Tonnes': 'Stok Karbon (T)', 'Year': 'Tahun'}
        )
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=4, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(family="Sora", size=10, color="#7A9A82")),
            yaxis=dict(showgrid=True, gridcolor="#EFF2EE",
                       tickfont=dict(family="Sora", size=10, color="#7A9A82")),
            legend=dict(font=dict(family="Sora", size=10, color="#2C3E2E"),
                        bgcolor="rgba(0,0,0,0)"),
            hovermode="x unified"
        )
        fig_trend.update_traces(line=dict(width=1.8))
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row2_r:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Perbandingan Antar Negara</span>
          <p class='card-sub'>Stok karbon tertinggi pada tahun terpilih.</p>
        """, unsafe_allow_html=True)

        top_n = df_yr.nlargest(8, 'Total_Carbon_Stock_Tonnes')
        fig_bar = go.Figure(go.Bar(
            x=top_n['Total_Carbon_Stock_Tonnes'] / 1e9,
            y=top_n['Country'],
            orientation='h',
            marker=dict(
                color=top_n['Total_Carbon_Stock_Tonnes'],
                colorscale=[[0,'#B8DECC'],[1,'#0A1A14']],
                showscale=False
            ),
            text=[f"{v:.1f} Gt" for v in top_n['Total_Carbon_Stock_Tonnes']/1e9],
            textposition='outside',
            textfont=dict(family="Sora", size=10, color="#5A7A66"),
            hovertemplate="<b>%{y}</b>: %{x:.2f} Gt<extra></extra>"
        ))
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=60, t=4, b=0),
            xaxis=dict(showgrid=True, gridcolor="#EFF2EE",
                       tickfont=dict(family="Sora", size=10, color="#7A9A82"),
                       title=dict(text="Giga Ton", font=dict(family="Sora", size=10, color="#7A9A82"))),
            yaxis=dict(showgrid=False, tickfont=dict(family="Sora", size=11, color="#2C3E2E")),
            height=300
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    row3_l, row3_r = st.columns([1, 1], gap="large")

    with row3_l:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Korelasi: Luas Hutan vs Stok Karbon</span>
          <p class='card-sub'>Hubungan area hutan dengan total cadangan karbon.</p>
        """, unsafe_allow_html=True)

        fig_sct = px.scatter(
            df_f[df_f['Year'] == filter_year],
            x='Forest_Area_km2', y='Total_Carbon_Stock_Tonnes',
            color='Region', size='Annual_Afforestation_Rate',
            color_discrete_sequence=['#0A1A14','#1A5C3A','#5AB88A','#B8DECC','#2E8B57','#94D4B0'],
            labels={
                'Forest_Area_km2': 'Luas Hutan (km²)',
                'Total_Carbon_Stock_Tonnes': 'Stok Karbon (T)'
            },
            hover_name='Country',
            size_max=20
        )
        fig_sct.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=4, b=0),
            xaxis=dict(showgrid=True, gridcolor="#EFF2EE",
                       tickfont=dict(family="Sora", size=10, color="#7A9A82")),
            yaxis=dict(showgrid=True, gridcolor="#EFF2EE",
                       tickfont=dict(family="Sora", size=10, color="#7A9A82")),
            legend=dict(font=dict(family="Sora", size=10, color="#2C3E2E"),
                        bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_sct, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row3_r:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Laju Deforestasi vs Aforestasi</span>
          <p class='card-sub'>Perbandingan laju kehilangan dan pemulihan hutan per negara.</p>
        """, unsafe_allow_html=True)

        cmp = df_f[df_f['Year'] == filter_year][
            ['Country','Annual_Deforestation_Rate','Annual_Afforestation_Rate']
        ].sort_values('Annual_Deforestation_Rate', ascending=False).head(10)

        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Bar(
            name='Deforestasi', x=cmp['Country'], y=cmp['Annual_Deforestation_Rate'],
            marker_color='#C85A5A', opacity=0.85
        ))
        fig_cmp.add_trace(go.Bar(
            name='Aforestasi', x=cmp['Country'], y=cmp['Annual_Afforestation_Rate'],
            marker_color='#1A5C3A', opacity=0.85
        ))
        fig_cmp.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=4, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(family="Sora", size=10, color="#7A9A82")),
            yaxis=dict(showgrid=True, gridcolor="#EFF2EE",
                       tickfont=dict(family="Sora", size=10, color="#7A9A82"),
                       title=dict(text="% per tahun", font=dict(family="Sora", size=10, color="#7A9A82"))),
            legend=dict(font=dict(family="Sora", size=11, color="#2C3E2E"),
                        bgcolor="rgba(0,0,0,0)"),
            bargap=0.3, bargroupgap=0.05
        )
        st.plotly_chart(fig_cmp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='card'>
      <span class='card-title'>Ringkasan Data Detail</span>
      <p class='card-sub'>Data terfilter untuk tahun dan negara yang dipilih.</p>
    """, unsafe_allow_html=True)

    tbl = df_yr[[
        'Country','Region','Forest_Area_km2','Annual_Deforestation_Rate',
        'Annual_Afforestation_Rate','Total_Carbon_Stock_Tonnes','Primary_Driver_of_Change'
    ]].copy()
    tbl.columns = [
        'Negara','Kawasan','Luas Hutan (km²)','Deforestasi (%/thn)',
        'Aforestasi (%/thn)','Stok Karbon (Ton)','Pemicu Utama'
    ]
    tbl['Luas Hutan (km²)']   = tbl['Luas Hutan (km²)'].map('{:,.0f}'.format)
    tbl['Stok Karbon (Ton)']  = tbl['Stok Karbon (Ton)'].map('{:,.0f}'.format)
    tbl['Deforestasi (%/thn)']= tbl['Deforestasi (%/thn)'].map('{:.2f}'.format)
    tbl['Aforestasi (%/thn)'] = tbl['Aforestasi (%/thn)'].map('{:.2f}'.format)
    st.dataframe(tbl, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# HALAMAN 2 — SIMULATOR PROYEKSI
# ══════════════════════════════════════════════
elif nav == "Simulator Proyeksi":

    st.markdown("""
    <span class='sec-label'>Permodelan Prediktif</span>
    <h2 class='page-title'>Simulator Proyeksi Ekologi</h2>
    <p class='page-sub'>
      Atur variabel ekologi dan lihat proyeksi cadangan karbon hingga tahun mendatang
      berdasarkan model estimasi berbasis data historis.
    </p>
    """, unsafe_allow_html=True)

    with st.form("form_simulator", clear_on_submit=False):
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.markdown("<p class='sec-label'>Konfigurasi Skenario</p>", unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns([1, 1, 2])
        with cc1:
            negara     = st.selectbox("Negara Fokus", COUNTRIES)
        with cc2:
            pemicu     = st.selectbox("Pemicu Utama", DRIVERS)
        with cc3:
            thn_target = st.slider("Target Tahun Proyeksi", 2026, 2060, 2035)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<p class='sec-label'>Skenario Intervensi Ekologi</p>", unsafe_allow_html=True)

        sl1, sl2 = st.columns(2, gap="large")
        with sl1:
            laju_defor = st.slider(
                "Laju Deforestasi (% per tahun)", 0.0, 5.0, 1.2, 0.1,
                help="Estimasi persentase hutan yang hilang setiap tahunnya."
            )
        with sl2:
            laju_affor = st.slider(
                "Laju Aforestasi (% per tahun)", 0.0, 5.0, 0.5, 0.1,
                help="Target pemulihan atau penanaman hutan baru per tahun."
            )

        with st.expander("Parameter Lanjutan — Opsional"):
            st.markdown(
                "<p style='font-size:0.82rem;color:#7A9A82;margin-bottom:1rem;'>"
                "Nilai default menggunakan rata-rata regional. Ubah hanya jika tersedia data lapangan spesifik.</p>",
                unsafe_allow_html=True
            )
            ap1, ap2 = st.columns(2)
            luas_hutan = ap1.number_input("Luas Hutan Awal (km²)", value=250000, step=5000)
            luas_lahan = ap2.number_input("Luas Total Daratan (km²)", value=400000, step=5000)
            ap3, ap4 = st.columns(2)
            skenario_label = ap3.selectbox(
                "Skenario Iklim",
                ["Optimis (RCP 2.6)", "Moderat (RCP 4.5)", "Pesimis (RCP 8.5)"]
            )

        st.write("")
        jalankan = st.form_submit_button("Jalankan Simulasi Proyeksi")
        st.markdown("</div>", unsafe_allow_html=True)

    if jalankan:
        with st.spinner("Menghitung trayektori cadangan karbon..."):
            time.sleep(1.2)

            hasil_list, thn_list = [], []
            for y in range(YEAR_MAX, thn_target + 1):
                faktor_iklim = {'Optimis (RCP 2.6)': 1.02, 'Moderat (RCP 4.5)': 1.0, 'Pesimis (RCP 8.5)': 0.97}
                f_iklim      = faktor_iklim.get(skenario_label, 1.0)
                forest_sim   = luas_hutan * (1 + (laju_affor - laju_defor) / 100) ** (y - YEAR_MAX)
                params = {
                    'Year': y,
                    'Forest_Area_km2': max(forest_sim * f_iklim, 1000),
                    'Land_Area_km2': luas_lahan,
                    'Annual_Deforestation_Rate': laju_defor,
                    'Annual_Afforestation_Rate': laju_affor,
                    'Primary_Driver_of_Change': pemicu
                }
                hasil_list.append(prediksi_stok(params))
                thn_list.append(y)

            hasil_akhir  = hasil_list[-1]
            hasil_awal   = hasil_list[0]
            pct_change   = ((hasil_akhir - hasil_awal) / hasil_awal) * 100
            net          = laju_affor - laju_defor
            skenario_str = "Pemulihan" if net >= 0 else "Penurunan"

        st.markdown(f"""
        <div class='card-dark'>
          <span class='result-label'>Proyeksi Cadangan Karbon &mdash; {thn_target}</span>
          <div class='result-num'>{hasil_akhir:,.0f}
            <span class='result-unit'>Ton</span>
          </div>
          <p class='result-meta'>
            Negara: <strong>{negara}</strong> &nbsp;&middot;&nbsp;
            Pemicu: <strong>{pemicu}</strong> &nbsp;&middot;&nbsp;
            Skenario: <strong>{skenario_str}</strong> &nbsp;&middot;&nbsp;
            Perubahan: <strong>{pct_change:+.1f}%</strong>
          </p>
        </div>
        """, unsafe_allow_html=True)

        ra, rb = st.columns([2, 1], gap="large")

        with ra:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<span class='card-title'>Trayektori Proyeksi Stok Karbon</span>", unsafe_allow_html=True)
            st.markdown("<p class='card-sub'>Estimasi perubahan cadangan karbon dari sekarang hingga tahun target.</p>", unsafe_allow_html=True)

            df_proj = pd.DataFrame({'Tahun': thn_list, 'Stok Karbon (Ton)': hasil_list})
            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(
                x=df_proj['Tahun'], y=df_proj['Stok Karbon (Ton)'],
                mode='lines',
                line=dict(color='#1A5C3A', width=2.5),
                fill='tozeroy',
                fillcolor='rgba(26,92,58,0.07)',
                hovertemplate="Tahun %{x}<br>%{y:,.0f} Ton<extra></extra>"
            ))
            fig_proj.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=4, b=0),
                xaxis=dict(showgrid=False,
                           tickfont=dict(family="Sora", size=10, color="#7A9A82")),
                yaxis=dict(showgrid=True, gridcolor="#EFF2EE",
                           tickfont=dict(family="Sora", size=10, color="#7A9A82")),
                height=260
            )
            st.plotly_chart(fig_proj, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with rb:
            st.markdown("<div class='card-flat'>", unsafe_allow_html=True)
            st.markdown("<span class='card-title'>Ringkasan Skenario</span>", unsafe_allow_html=True)
            st.write("")

            st.metric("Stok Awal (2025)",   f"{hasil_awal:,.0f} T")
            st.metric("Stok Akhir Target",  f"{hasil_akhir:,.0f} T",
                      delta=f"{pct_change:+.1f}%",
                      delta_color="normal" if pct_change > 0 else "inverse")
            st.metric("Selisih Laju Bersih", f"{net:+.1f}%/thn",
                      delta_color="normal" if net > 0 else "inverse")
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        if net >= 0:
            st.success(
                f"Skenario Positif — Laju aforestasi melampaui deforestasi sebesar "
                f"{net:.1f}%/tahun. Ekosistem diproyeksikan pulih secara bertahap hingga {thn_target}."
            )
        else:
            st.error(
                f"Peringatan Ekologis — Laju deforestasi mendominasi sebesar "
                f"{abs(net):.1f}%/tahun. Cadangan karbon diproyeksikan menyusut kritis hingga {thn_target}."
            )


# ══════════════════════════════════════════════
# HALAMAN 3 — ANALISIS KEBIJAKAN
# ══════════════════════════════════════════════
else:
    st.markdown("""
    <span class='sec-label'>Laboratorium Regulasi</span>
    <h2 class='page-title'>Simulator Dampak Kebijakan</h2>
    <p class='page-sub'>
      Aktifkan intervensi regulasi di bawah ini dan amati dampaknya secara langsung
      terhadap proyeksi ekosistem hutan global pada tahun 2030.
    </p>
    """, unsafe_allow_html=True)

    colp, colr = st.columns([4, 6], gap="large")

    with colp:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<p class='sec-label'>Panel Intervensi</p>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin:0 0 1.5rem;'>Kontrol Regulasi</h4>", unsafe_allow_html=True)

        pol_log = st.toggle(
            "Moratorium Penebangan Komersial",
            help="Mengurangi deforestasi dari sektor industri kayu hingga 70%."
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        pol_fun = st.toggle(
            "Dana Reboisasi Masif",
            help="Mendongkrak laju aforestasi hingga 3 kali lipat melalui investasi publik."
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        pol_fir = st.toggle(
            "Sanksi Tegas Pembakaran Lahan",
            help="Menghapus faktor kebakaran sebagai pemicu utama kerusakan hutan."
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        pol_int = st.toggle(
            "Program Insentif Petani Hutan",
            help="Mengubah motivasi ekonomi petani dari membuka lahan menjadi menjaga hutan."
        )
        st.markdown("<hr>", unsafe_allow_html=True)

        aktif = {
            "Moratorium Penebangan": pol_log,
            "Dana Reboisasi": pol_fun,
            "Sanksi Pembakaran": pol_fir,
            "Insentif Petani": pol_int
        }
        n_aktif = sum(aktif.values())

        if n_aktif > 0:
            st.markdown(
                f"<span class='tag-active'>{n_aktif} Kebijakan Aktif</span>",
                unsafe_allow_html=True
            )
            for nm, val in aktif.items():
                if val:
                    st.markdown(
                        f"<p style='font-size:0.82rem;color:#1A5C3A;margin:3px 0;font-weight:500;'>"
                        f"— {nm}</p>",
                        unsafe_allow_html=True
                    )
        else:
            st.markdown(
                "<p style='font-size:0.82rem;color:#A8B8A8;font-style:italic;'>"
                "Belum ada intervensi aktif. Aktifkan toggle di atas untuk memulai.</p>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with colr:
        base_def = 2.0
        base_aff = 0.5
        if pol_log: base_def *= 0.3
        if pol_fun: base_aff *= 3.0
        if pol_fir: base_def *= 0.8
        if pol_int: base_aff *= 1.4; base_def *= 0.9

        p_params = {
            'Year': 2030, 'Forest_Area_km2': 400000, 'Land_Area_km2': 600000,
            'Annual_Deforestation_Rate': base_def, 'Annual_Afforestation_Rate': base_aff,
            'Primary_Driver_of_Change': 'Pertanian'
        }
        hasil_pol = prediksi_stok(p_params)

        baseline_params = {**p_params,
            'Annual_Deforestation_Rate': 2.0, 'Annual_Afforestation_Rate': 0.5
        }
        hasil_base = prediksi_stok(baseline_params)
        selisih_pct = ((hasil_pol - hasil_base) / hasil_base) * 100

        st.markdown("<div class='card-flat'>", unsafe_allow_html=True)
        st.markdown("<p class='sec-label'>Dampak Proyeksi 2030</p>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin:0 0 1.25rem;'>Hasil Simulasi Ekologis</h4>", unsafe_allow_html=True)

        km1, km2, km3 = st.columns(3)
        km1.metric(
            "Laju Deforestasi",
            f"{base_def:.2f}%",
            delta=f"{base_def - 2.0:+.2f}%" if base_def != 2.0 else None,
            delta_color="inverse"
        )
        km2.metric(
            "Laju Aforestasi",
            f"{base_aff:.2f}%",
            delta=f"{base_aff - 0.5:+.2f}%" if base_aff != 0.5 else None
        )
        km3.metric(
            "Perubahan Stok",
            f"{selisih_pct:+.1f}%",
            delta="vs. tanpa kebijakan",
            delta_color="normal" if selisih_pct >= 0 else "inverse"
        )

        st.markdown(f"""
        <div class='policy-strip'>
          <span class='ps-label'>Estimasi Stok Karbon 2030</span>
          <div class='ps-val'>{hasil_pol:,.0f}
            <span style='font-size:1rem;font-weight:300;color:#7A9A82 !important;'> Ton</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)
        st.markdown("<span class='card-title'>Profil Dampak Multidimensi</span>", unsafe_allow_html=True)
        st.markdown("<p class='card-sub'>Perbandingan kondisi baseline vs. dengan kebijakan aktif.</p>", unsafe_allow_html=True)

        cats = [
            'Cadangan<br>Karbon', 'Tutupan<br>Hutan', 'Laju<br>Pemulihan',
            'Kontrol<br>Deforestasi', 'Skor<br>Kebijakan'
        ]
        base_vals = [0.40, 0.38, 0.18, 0.32, 0.08]
        pol_vals  = [
            min(hasil_pol / 5e10, 1.0),
            min((base_aff / 5.0) * 0.85 + 0.22, 1.0),
            min(base_aff / 5.0, 1.0),
            min(1.0 - base_def / 5.0, 1.0),
            min(n_aktif / 4.0, 1.0)
        ]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=base_vals + [base_vals[0]], theta=cats + [cats[0]],
            fill='toself', name='Baseline (Tanpa Kebijakan)',
            line=dict(color='#C8D8C8', width=1.5),
            fillcolor='rgba(200,216,200,0.15)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=pol_vals + [pol_vals[0]], theta=cats + [cats[0]],
            fill='toself', name='Dengan Kebijakan',
            line=dict(color='#1A5C3A', width=2),
            fillcolor='rgba(26,92,58,0.18)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, range=[0, 1],
                    showticklabels=False, gridcolor="#E8EEE8"
                ),
                angularaxis=dict(
                    tickfont=dict(family="Sora", size=10, color="#5A7A66")
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=True,
            legend=dict(
                font=dict(family="Sora", size=10, color="#2C3E2E"),
                bgcolor="rgba(0,0,0,0)",
                orientation="h",
                y=-0.08
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=10, b=30),
            height=280
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='card-title'>Proyeksi Dampak Kebijakan Jangka Panjang (2025–2040)</span>", unsafe_allow_html=True)
    st.markdown("<p class='card-sub'>Perbandingan trayektori stok karbon antara baseline dan skenario kebijakan aktif.</p>", unsafe_allow_html=True)

    yrs_long = list(range(2025, 2041))
    base_traj, pol_traj = [], []
    for y in yrs_long:
        t_off = y - 2025
        bp = {
            'Year': y,
            'Forest_Area_km2': 400000 * (1 - 0.015) ** t_off,
            'Land_Area_km2': 600000,
            'Annual_Deforestation_Rate': 2.0,
            'Annual_Afforestation_Rate': 0.5,
            'Primary_Driver_of_Change': 'Pertanian'
        }
        pp = {
            'Year': y,
            'Forest_Area_km2': 400000 * (1 + (base_aff - base_def) / 100) ** t_off,
            'Land_Area_km2': 600000,
            'Annual_Deforestation_Rate': base_def,
            'Annual_Afforestation_Rate': base_aff,
            'Primary_Driver_of_Change': 'Pertanian'
        }
        base_traj.append(prediksi_stok(bp))
        pol_traj.append(prediksi_stok(pp))

    fig_long = go.Figure()
    fig_long.add_trace(go.Scatter(
        x=yrs_long, y=base_traj, mode='lines', name='Tanpa Kebijakan',
        line=dict(color='#C85A5A', width=2, dash='dot'),
        fill='tozeroy', fillcolor='rgba(200,90,90,0.04)'
    ))
    fig_long.add_trace(go.Scatter(
        x=yrs_long, y=pol_traj, mode='lines', name='Dengan Kebijakan',
        line=dict(color='#1A5C3A', width=2.5),
        fill='tozeroy', fillcolor='rgba(26,92,58,0.07)'
    ))
    fig_long.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=4, b=0),
        xaxis=dict(showgrid=False, tickfont=dict(family="Sora", size=10, color="#7A9A82")),
        yaxis=dict(showgrid=True, gridcolor="#EFF2EE",
                   tickfont=dict(family="Sora", size=10, color="#7A9A82")),
        legend=dict(font=dict(family="Sora", size=11, color="#2C3E2E"), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
        height=260
    )
    st.plotly_chart(fig_long, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
