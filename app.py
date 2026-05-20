import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import time

# ──────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────
st.set_page_config(
    page_title="EcoAnalytics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────
# SESSION STATE — navigasi aktif
# ──────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# ──────────────────────────────────────────
# DESIGN SYSTEM
# ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');

/* ── Reset ── */
*, html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
    box-sizing: border-box;
}

:root {
    --bg:       #F0F4F0;
    --surface:  #FFFFFF;
    --border:   #D8E4D8;
    --ink-1:    #0D1F14;
    --ink-2:    #3A5242;
    --ink-3:    #7A9882;
    --green-1:  #0D3D22;
    --green-2:  #166637;
    --green-3:  #28A05A;
    --green-4:  #6ED4A0;
    --green-5:  #C4EDD8;
    --red:      #C0453A;
}

/* ── Base ── */
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1280px !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--ink-1) !important;
    border-right: 1px solid #162816 !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.75rem 1.25rem !important;
}
[data-testid="stSidebar"] * { color: #B8D4BE !important; }

/* ── NAV BUTTONS (sidebar) ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: #90B898 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    padding: 0.6rem 0.9rem !important;
    width: 100% !important;
    text-align: left !important;
    transition: background 0.15s, color 0.15s !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    box-shadow: none !important;
    transform: none !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.07) !important;
    color: #E8F4E8 !important;
    box-shadow: none !important;
    transform: none !important;
}
/* Active state ditangani via CSS class */
[data-testid="stSidebar"] .nav-active .stButton > button {
    background: var(--green-2) !important;
    color: #FFFFFF !important;
}

/* ── TIPOGRAFI ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Sora', sans-serif !important;
    color: var(--ink-1) !important;
    letter-spacing: -0.02em !important;
}
p, span, div, li, label { color: var(--ink-2) !important; }

/* ── METRIC CARD ── */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.1rem 1.4rem 1.25rem !important;
    box-shadow: 0 1px 4px rgba(13,31,20,0.05) !important;
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span,
[data-testid="stMetricLabel"] div {
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--ink-3) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--ink-1) !important;
    letter-spacing: -0.03em !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricValue"] * { color: var(--ink-1) !important; }
[data-testid="stMetricDelta"] * { font-size: 0.75rem !important; }

/* ── CARD ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 6px rgba(13,31,20,0.04);
}
.card-dark {
    background: linear-gradient(135deg, #0D1F14 0%, #166637 100%);
    border-radius: 14px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 32px rgba(13,31,20,0.22);
}

/* ── LABEL ── */
.sec-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ink-3) !important;
    display: block;
    margin-bottom: 0.25rem;
}
.page-title {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--ink-1) !important;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin: 0 0 0.3rem;
}
.page-sub {
    font-size: 0.85rem;
    color: var(--ink-3) !important;
    margin: 0 0 1.75rem;
    line-height: 1.6;
}
.card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--ink-1) !important;
    letter-spacing: -0.01em;
    margin: 0 0 0.15rem;
}
.card-sub {
    font-size: 0.75rem;
    color: var(--ink-3) !important;
    margin: 0 0 1rem;
}

/* ── RESULT HERO ── */
.result-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--green-4) !important;
    display: block;
    margin-bottom: 0.6rem;
}
.result-num {
    font-size: 2.8rem;
    font-weight: 700;
    color: #FFFFFF !important;
    letter-spacing: -0.04em;
    line-height: 1;
}
.result-unit {
    font-size: 1rem;
    font-weight: 300;
    color: rgba(255,255,255,0.5) !important;
}
.result-meta {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.45) !important;
    margin-top: 0.75rem;
}
.result-meta strong { color: var(--green-4) !important; }

/* ── POLICY STRIP ── */
.policy-strip {
    background: var(--bg);
    border-radius: 10px;
    border-left: 3px solid var(--green-2);
    padding: 1rem 1.25rem;
    margin-top: 1rem;
}
.ps-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-3) !important;
    display: block;
    margin-bottom: 0.2rem;
}
.ps-val {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--ink-1) !important;
    letter-spacing: -0.03em;
}

/* ── FORM / FILTER BAR ── */
.filter-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
}
.stSelectbox label, .stSlider > label,
.stNumberInput label, .stMultiSelect label {
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--ink-3) !important;
}
[data-baseweb="select"] > div {
    border-radius: 8px !important;
    border-color: var(--border) !important;
    background: var(--bg) !important;
    color: var(--ink-1) !important;
}
[data-baseweb="select"] * { color: var(--ink-1) !important; }

/* ── BUTTONS (main area) ── */
.main-area .stButton > button,
.block-container .stButton > button {
    background: var(--ink-1) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.4rem !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    transition: background 0.2s !important;
}
.block-container .stButton > button:hover {
    background: var(--green-2) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── EXPANDER ── */
.stExpander {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--bg) !important;
}
details summary p {
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--ink-3) !important;
}

/* ── ALERTS ── */
.stSuccess > div, .stError > div, .stInfo > div, .stWarning > div {
    border-radius: 10px !important;
    font-size: 0.85rem !important;
}

/* ── TABLE ── */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
thead tr th {
    background: var(--bg) !important;
    color: var(--ink-3) !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
}

/* ── TOGGLE ── */
.stToggle label { font-size: 0.85rem !important; color: var(--ink-2) !important; }

hr { border-color: #1D3226 !important; margin: 1rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────
# DATA
# ──────────────────────────────────────────
@st.cache_data
def load_data():
    paths = [
        "/content/drive/MyDrive/Tugas Week 12/global_deforestation_2000_2025.csv",
        "global_deforestation_2000_2025.csv"
    ]

    def assign_region(c):
        c_lower = str(c).lower()
        if c_lower in ['brazil', 'colombia', 'peru', 'argentina', 'chile', 'bolivia']:
            return 'Amerika Selatan'
        elif c_lower in ['indonesia', 'malaysia', 'thailand', 'vietnam', 'philippines']:
            return 'Asia Tenggara'
        elif c_lower in ['india', 'china', 'japan', 'korea']:
            return 'Asia'
        elif c_lower in ['canada', 'usa', 'mexico', 'united states']:
            return 'Amerika Utara'
        elif c_lower in ['congo', 'nigeria', 'south africa', 'algeria']:
            return 'Afrika'
        elif c_lower in ['russia', 'kazakhstan', 'ukraine', 'france', 'germany']:
            return 'Eropa & Asia'
        elif c_lower in ['australia', 'new zealand']:
            return 'Oseania'
        else:
            return 'Lainnya'

    for p in paths:
        if os.path.exists(p):
            df_real = pd.read_csv(p)
            if 'Region' not in df_real.columns:
                df_real['Region'] = df_real['Country'].apply(assign_region)
            return df_real

    # Dummy data
    np.random.seed(42)
    countries = ['Brazil', 'Indonesia', 'Canada', 'Russia', 'USA',
                 'Congo', 'Australia', 'India', 'China', 'Malaysia']
    rows = []
    for country in countries:
        base_forest = np.random.uniform(100000, 600000)
        base_carbon = np.random.uniform(8e9, 4.5e10)
        for year in range(2000, 2026):
            defor = np.random.uniform(0.3, 3.0)
            affor = np.random.uniform(0.1, 2.0)
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
                'Primary_Driver_of_Change': np.random.choice(
                    ['Pertanian', 'Kebakaran', 'Pertambangan', 'Penebangan'],
                    p=[0.45, 0.25, 0.15, 0.15]
                ),
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
COUNTRIES = sorted([str(x) for x in df['Country'].dropna().unique()])
DRIVERS   = sorted([str(x) for x in df['Primary_Driver_of_Change'].dropna().unique()])
REGIONS   = sorted([str(x) for x in df['Region'].dropna().unique()])
YEAR_MIN  = int(df['Year'].min()) if not df['Year'].isnull().all() else 2000
YEAR_MAX  = int(df['Year'].max()) if not df['Year'].isnull().all() else 2025

# Plotly color palette — tight green scale
C = ['#0D1F14', '#166637', '#28A05A', '#6ED4A0', '#B0E8CB', '#D8F4E4']


# ──────────────────────────────────────────
# CHART HELPERS
# ──────────────────────────────────────────
CHART_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, t=4, b=0),
    font=dict(family='Sora', color='#7A9882'),
)
AXIS_X = dict(showgrid=False, tickfont=dict(family='Sora', size=10, color='#7A9882'))
AXIS_Y = dict(showgrid=True, gridcolor='#E4EDE4', tickfont=dict(family='Sora', size=10, color='#7A9882'))
LEGEND = dict(font=dict(family='Sora', size=10, color='#3A5242'), bgcolor='rgba(0,0,0,0)')


# ──────────────────────────────────────────
# SIDEBAR — button navigation
# ──────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="margin-bottom:2rem;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">
        <div style="width:8px;height:8px;border-radius:50%;
                    background:#28A05A;flex-shrink:0;"></div>
        <span style="font-size:1.05rem;font-weight:700;
                     color:#E4F2E8;letter-spacing:-0.02em;">EcoAnalytics</span>
      </div>
      <p style="font-size:0.62rem;color:#3A5242;letter-spacing:0.1em;
                text-transform:uppercase;margin:0;padding-left:16px;">
        Global Carbon Stock
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style="font-size:0.6rem;font-weight:700;letter-spacing:0.14em;
              text-transform:uppercase;color:#2E4A36;margin-bottom:0.5rem;">
      Navigasi
    </p>
    """, unsafe_allow_html=True)

    # Nav items
    nav_items = [
        ("dashboard",  "🌍  Dashboard"),
        ("simulator",  "📈  Simulator"),
        ("kebijakan",  "⚖️  Kebijakan"),
    ]

    for key, label in nav_items:
        is_active = st.session_state.page == key
        # Inject active class via container hack
        if is_active:
            st.markdown("<div class='nav-active'>", unsafe_allow_html=True)
        if st.button(label, key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()
        if is_active:
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.7rem;color:#2E4A36;line-height:1.9;">
      <span style="color:#6ED4A0;font-weight:600;">Kelompok 6</span><br>
      Python System Analytics<br>
      Fakultas Teknologi Informasi
    </div>
    """, unsafe_allow_html=True)


page = st.session_state.page


# ══════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════
if page == "dashboard":

    st.markdown("""
    <span class='sec-label'>Pemantauan</span>
    <p class='page-title'>Dashboard Stok Karbon Global</p>
    <p class='page-sub'>Distribusi biomassa, tren deforestasi, dan tutupan hutan dunia.</p>
    """, unsafe_allow_html=True)

    # ── Filter Bar ──
    st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 1])
    with fc1:
        filter_region = st.multiselect("Kawasan", REGIONS, default=REGIONS)
    with fc2:
        filter_country = st.multiselect("Negara", COUNTRIES, default=COUNTRIES)
    with fc3:
        filter_driver = st.multiselect("Pemicu", DRIVERS, default=DRIVERS)
    with fc4:
        filter_year = st.selectbox("Tahun", list(range(YEAR_MIN, YEAR_MAX + 1)),
                                   index=YEAR_MAX - YEAR_MIN)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Apply filters ──
    df_f = df[
        df['Region'].astype(str).isin(filter_region or REGIONS) &
        df['Country'].astype(str).isin(filter_country or COUNTRIES) &
        df['Primary_Driver_of_Change'].astype(str).isin(filter_driver or DRIVERS)
    ]
    df_yr = df_f[df_f['Year'] == filter_year]

    # ── KPI Row ──
    k1, k2, k3, k4 = st.columns(4)
    total_carbon = df_yr['Total_Carbon_Stock_Tonnes'].sum()
    total_forest = df_yr['Forest_Area_km2'].sum()
    avg_defor    = df_yr['Annual_Deforestation_Rate'].mean()
    avg_affor    = df_yr['Annual_Afforestation_Rate'].mean()
    base_defor   = df[df['Year'] == YEAR_MIN]['Annual_Deforestation_Rate'].mean()
    if np.isnan(base_defor): base_defor = 0

    k1.metric("Stok Karbon Total", f"{total_carbon/1e12:.2f} Tt")
    k2.metric("Luas Hutan",        f"{total_forest/1e6:.2f} jt km²")
    k3.metric("Deforestasi",       f"{avg_defor:.2f}%/thn",
              delta=f"{avg_defor - base_defor:.2f}% vs 2000",
              delta_color="inverse")
    k4.metric("Aforestasi",        f"{avg_affor:.2f}%/thn")

    st.write("")

    # ── Row 1: Peta + Donut ──
    col_map, col_pie = st.columns([3, 2], gap="large")

    with col_map:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Distribusi Stok Karbon</span>
          <p class='card-sub'>Kepadatan stok karbon per negara, tahun terpilih.</p>
        """, unsafe_allow_html=True)

        fig_map = px.choropleth(
            df_yr,
            locations="Country",
            locationmode="country names",
            color="Total_Carbon_Stock_Tonnes",
            color_continuous_scale=[
                [0.0, "#D8F4E4"], [0.35, "#6ED4A0"],
                [0.7,  "#166637"], [1.0,  "#0D1F14"]
            ],
            labels={"Total_Carbon_Stock_Tonnes": "Stok Karbon (T)"}
        )
        fig_map.update_layout(
            **CHART_BASE,
            geo=dict(
                showframe=False, showcoastlines=True, coastlinecolor="#C8D8C8",
                projection_type='natural earth', bgcolor='rgba(0,0,0,0)',
                showland=True, landcolor="#EBF2EB",
                showocean=True, oceancolor="#E2EAF0"
            ),
            coloraxis_colorbar=dict(
                title="", tickfont=dict(family="Sora", size=9, color="#7A9882"),
                thickness=6, len=0.5, x=1.01
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_pie:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Pemicu Deforestasi</span>
          <p class='card-sub'>Distribusi faktor penyebab kehilangan tutupan hutan.</p>
        """, unsafe_allow_html=True)

        driver_data = df_f.groupby('Primary_Driver_of_Change').size().reset_index(name='Jumlah')
        fig_donut = go.Figure(go.Pie(
            labels=driver_data['Primary_Driver_of_Change'],
            values=driver_data['Jumlah'],
            hole=0.65,
            marker_colors=['#0D1F14', '#166637', '#28A05A', '#6ED4A0'],
            textfont=dict(family="Sora", size=11),
            hovertemplate="<b>%{label}</b><br>%{value} kasus<extra></extra>"
        ))
        fig_donut.update_layout(
            **CHART_BASE,
            showlegend=True,
            legend=dict(**LEGEND, orientation="v", x=0.65),
            annotations=[dict(
                text=f"<b>{driver_data['Jumlah'].sum()}</b><br><span style='font-size:9px'>Total</span>",
                x=0.5, y=0.5, font=dict(family="Sora", size=17, color="#0D1F14"),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 2: Tren + Bar ──
    col_trend, col_bar = st.columns([3, 2], gap="large")

    with col_trend:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Tren Stok Karbon 2000–2025</span>
          <p class='card-sub'>Cadangan karbon tahunan per negara.</p>
        """, unsafe_allow_html=True)

        trend = df_f.groupby(['Year', 'Country'])['Total_Carbon_Stock_Tonnes'].mean().reset_index()
        fig_trend = px.line(
            trend, x='Year', y='Total_Carbon_Stock_Tonnes', color='Country',
            color_discrete_sequence=C,
            labels={'Total_Carbon_Stock_Tonnes': 'Stok Karbon (T)', 'Year': 'Tahun'}
        )
        fig_trend.update_layout(**CHART_BASE, xaxis=AXIS_X, yaxis=AXIS_Y,
                                legend=dict(**LEGEND), hovermode="x unified")
        fig_trend.update_traces(line=dict(width=1.8))
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_bar:
        st.markdown("""
        <div class='card'>
          <span class='card-title'>Top Negara — Stok Karbon</span>
          <p class='card-sub'>Cadangan tertinggi pada tahun terpilih.</p>
        """, unsafe_allow_html=True)

        top_n = df_yr.nlargest(8, 'Total_Carbon_Stock_Tonnes')
        fig_bar = go.Figure(go.Bar(
            x=top_n['Total_Carbon_Stock_Tonnes'] / 1e9,
            y=top_n['Country'],
            orientation='h',
            marker=dict(
                color=top_n['Total_Carbon_Stock_Tonnes'],
                colorscale=[[0, '#B0E8CB'], [1, '#0D1F14']],
                showscale=False
            ),
            text=[f"{v:.1f} Gt" for v in top_n['Total_Carbon_Stock_Tonnes'] / 1e9],
            textposition='outside',
            textfont=dict(family="Sora", size=10, color="#7A9882"),
            hovertemplate="<b>%{y}</b>: %{x:.2f} Gt<extra></extra>"
        ))
        fig_bar.update_layout(
            **CHART_BASE,
            xaxis=dict(**AXIS_X,
                       title=dict(text="Giga Ton", font=dict(family="Sora", size=10, color="#7A9882"))),
            yaxis=dict(**AXIS_Y, showgrid=False,
                       tickfont=dict(family="Sora", size=11, color="#3A5242")),
            margin=dict(l=0, r=55, t=4, b=0),
            height=290
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Data Table ──
    st.markdown("""
    <div class='card'>
      <span class='card-title'>Ringkasan Data</span>
      <p class='card-sub'>Data terfilter untuk tahun yang dipilih.</p>
    """, unsafe_allow_html=True)

    tbl = df_yr[['Country', 'Region', 'Forest_Area_km2', 'Annual_Deforestation_Rate',
                 'Annual_Afforestation_Rate', 'Total_Carbon_Stock_Tonnes',
                 'Primary_Driver_of_Change']].copy()
    tbl.columns = ['Negara', 'Kawasan', 'Luas Hutan (km²)', 'Deforestasi (%)',
                   'Aforestasi (%)', 'Stok Karbon (Ton)', 'Pemicu Utama']
    tbl['Luas Hutan (km²)']   = tbl['Luas Hutan (km²)'].map('{:,.0f}'.format)
    tbl['Stok Karbon (Ton)']  = tbl['Stok Karbon (Ton)'].map('{:,.0f}'.format)
    tbl['Deforestasi (%)']    = tbl['Deforestasi (%)'].map('{:.2f}'.format)
    tbl['Aforestasi (%)']     = tbl['Aforestasi (%)'].map('{:.2f}'.format)
    st.dataframe(tbl, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# PAGE 2 — SIMULATOR
# ══════════════════════════════════════════
elif page == "simulator":

    st.markdown("""
    <span class='sec-label'>Pemodelan Prediktif</span>
    <p class='page-title'>Simulator Proyeksi Ekologi</p>
    <p class='page-sub'>Atur variabel ekologi dan lihat proyeksi cadangan karbon berdasarkan model estimasi historis.</p>
    """, unsafe_allow_html=True)

    with st.form("form_simulator", clear_on_submit=False):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<p class='sec-label'>Konfigurasi Skenario</p>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 1, 2])
        negara     = c1.selectbox("Negara Fokus", COUNTRIES)
        pemicu     = c2.selectbox("Pemicu Utama", DRIVERS)
        thn_target = c3.slider("Target Tahun Proyeksi", 2026, 2060, 2035)

        st.markdown("<hr style='border-color:#E4EDE4 !important;'>", unsafe_allow_html=True)
        st.markdown("<p class='sec-label'>Skenario Intervensi</p>", unsafe_allow_html=True)

        s1, s2 = st.columns(2, gap="large")
        laju_defor = s1.slider("Laju Deforestasi (% / tahun)", 0.0, 5.0, 1.2, 0.1)
        laju_affor = s2.slider("Laju Aforestasi (% / tahun)",  0.0, 5.0, 0.5, 0.1)

        with st.expander("Parameter Lanjutan"):
            ap1, ap2 = st.columns(2)
            luas_hutan = ap1.number_input("Luas Hutan Awal (km²)",   value=250000, step=5000)
            luas_lahan = ap2.number_input("Luas Total Daratan (km²)", value=400000, step=5000)
            skenario_label = st.selectbox(
                "Skenario Iklim",
                ["Optimis (RCP 2.6)", "Moderat (RCP 4.5)", "Pesimis (RCP 8.5)"]
            )

        st.write("")
        jalankan = st.form_submit_button("Jalankan Simulasi")
        st.markdown("</div>", unsafe_allow_html=True)

    if jalankan:
        with st.spinner("Menghitung trayektori..."):
            time.sleep(0.8)
            f_iklim = {"Optimis (RCP 2.6)": 1.02, "Moderat (RCP 4.5)": 1.0,
                       "Pesimis (RCP 8.5)": 0.97}.get(skenario_label, 1.0)

            hasil_list, thn_list = [], []
            for y in range(YEAR_MAX, thn_target + 1):
                forest_sim = luas_hutan * (1 + (laju_affor - laju_defor) / 100) ** (y - YEAR_MAX)
                params = {
                    'Year': y,
                    'Forest_Area_km2': max(forest_sim * f_iklim, 1000),
                    'Land_Area_km2': luas_lahan,
                    'Annual_Deforestation_Rate': laju_defor,
                    'Annual_Afforestation_Rate': laju_affor,
                }
                hasil_list.append(prediksi_stok(params))
                thn_list.append(y)

            hasil_akhir = hasil_list[-1]
            hasil_awal  = hasil_list[0]
            pct_change  = ((hasil_akhir - hasil_awal) / hasil_awal) * 100
            net         = laju_affor - laju_defor
            skenario_str = "Pemulihan" if net >= 0 else "Penurunan"

        # Hero result
        st.markdown(f"""
        <div class='card-dark'>
          <span class='result-label'>Proyeksi Cadangan Karbon &mdash; {thn_target}</span>
          <div class='result-num'>{hasil_akhir:,.0f}
            <span class='result-unit'> Ton</span>
          </div>
          <p class='result-meta'>
            Negara: <strong>{negara}</strong> &nbsp;·&nbsp;
            Pemicu: <strong>{pemicu}</strong> &nbsp;·&nbsp;
            Skenario: <strong>{skenario_str}</strong> &nbsp;·&nbsp;
            Perubahan: <strong>{pct_change:+.1f}%</strong>
          </p>
        </div>
        """, unsafe_allow_html=True)

        col_chart, col_summary = st.columns([3, 1], gap="large")

        with col_chart:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<span class='card-title'>Trayektori Proyeksi</span>", unsafe_allow_html=True)
            st.markdown("<p class='card-sub'>Estimasi cadangan karbon dari sekarang hingga tahun target.</p>", unsafe_allow_html=True)

            df_proj = pd.DataFrame({'Tahun': thn_list, 'Stok Karbon (Ton)': hasil_list})
            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(
                x=df_proj['Tahun'], y=df_proj['Stok Karbon (Ton)'],
                mode='lines',
                line=dict(color='#166637', width=2.5),
                fill='tozeroy', fillcolor='rgba(22,102,55,0.08)',
                hovertemplate="Tahun %{x}<br>%{y:,.0f} Ton<extra></extra>"
            ))
            fig_proj.update_layout(**CHART_BASE, xaxis=AXIS_X, yaxis=AXIS_Y, height=240)
            st.plotly_chart(fig_proj, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_summary:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<span class='card-title'>Ringkasan</span>", unsafe_allow_html=True)
            st.write("")
            st.metric("Stok Awal (2025)",  f"{hasil_awal:,.0f} T")
            st.metric("Stok Akhir Target", f"{hasil_akhir:,.0f} T",
                      delta=f"{pct_change:+.1f}%",
                      delta_color="normal" if pct_change > 0 else "inverse")
            st.metric("Laju Bersih",       f"{net:+.1f}%/thn",
                      delta_color="normal" if net > 0 else "inverse")
            st.markdown("</div>", unsafe_allow_html=True)

        if net >= 0:
            st.success(
                f"Skenario Positif — Aforestasi melampaui deforestasi sebesar "
                f"{net:.1f}%/tahun. Ekosistem diproyeksikan pulih bertahap hingga {thn_target}."
            )
        else:
            st.error(
                f"Peringatan — Deforestasi mendominasi sebesar {abs(net):.1f}%/tahun. "
                f"Cadangan karbon diproyeksikan menyusut kritis hingga {thn_target}."
            )


# ══════════════════════════════════════════
# PAGE 3 — KEBIJAKAN
# ══════════════════════════════════════════
else:

    st.markdown("""
    <span class='sec-label'>Laboratorium Regulasi</span>
    <p class='page-title'>Simulator Dampak Kebijakan</p>
    <p class='page-sub'>Aktifkan intervensi regulasi dan amati dampaknya terhadap ekosistem hutan global pada 2030.</p>
    """, unsafe_allow_html=True)

    col_panel, col_result = st.columns([4, 6], gap="large")

    with col_panel:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<p class='sec-label'>Panel Intervensi</p>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin:0 0 1.25rem;font-size:1rem;'>Kontrol Regulasi</h4>",
                    unsafe_allow_html=True)

        pol_log = st.toggle("Moratorium Penebangan Komersial",
                            help="Mengurangi deforestasi industri kayu hingga 70%.")
        pol_fun = st.toggle("Dana Reboisasi Masif",
                            help="Mendongkrak laju aforestasi hingga 3× melalui investasi publik.")
        pol_fir = st.toggle("Sanksi Tegas Pembakaran Lahan",
                            help="Menghapus faktor kebakaran sebagai pemicu kerusakan hutan.")
        pol_int = st.toggle("Program Insentif Petani Hutan",
                            help="Mengubah motivasi petani dari membuka lahan menjadi menjaga hutan.")

        st.markdown("<hr style='border-color:#E4EDE4 !important;'>", unsafe_allow_html=True)

        aktif = {"Moratorium Penebangan": pol_log, "Dana Reboisasi": pol_fun,
                 "Sanksi Pembakaran": pol_fir, "Insentif Petani": pol_int}
        n_aktif = sum(aktif.values())

        if n_aktif > 0:
            st.markdown(
                f"<span style='display:inline-block;background:#E4F2E8;color:#166637;font-size:0.65rem;"
                f"font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:0.2rem 0.65rem;"
                f"border-radius:100px;border:1px solid #B0E8CB;'>"
                f"{n_aktif} Kebijakan Aktif</span>",
                unsafe_allow_html=True
            )
            st.write("")
            for nm, val in aktif.items():
                if val:
                    st.markdown(
                        f"<p style='font-size:0.8rem;color:#166637;margin:3px 0;font-weight:500;'>"
                        f"✓ {nm}</p>",
                        unsafe_allow_html=True
                    )
        else:
            st.markdown(
                "<p style='font-size:0.8rem;color:#7A9882;font-style:italic;margin:0;'>"
                "Belum ada intervensi aktif.</p>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_result:
        base_def = 2.0
        base_aff = 0.5
        if pol_log: base_def *= 0.3
        if pol_fun: base_aff *= 3.0
        if pol_fir: base_def *= 0.8
        if pol_int: base_aff *= 1.4; base_def *= 0.9

        p_params = {
            'Year': 2030, 'Forest_Area_km2': 400000, 'Land_Area_km2': 600000,
            'Annual_Deforestation_Rate': base_def, 'Annual_Afforestation_Rate': base_aff
        }
        hasil_pol  = prediksi_stok(p_params)
        hasil_base = prediksi_stok({**p_params, 'Annual_Deforestation_Rate': 2.0,
                                    'Annual_Afforestation_Rate': 0.5})
        selisih_pct = ((hasil_pol - hasil_base) / hasil_base) * 100

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<p class='sec-label'>Dampak Proyeksi 2030</p>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin:0 0 1.25rem;font-size:1rem;'>Hasil Simulasi</h4>",
                    unsafe_allow_html=True)

        km1, km2, km3 = st.columns(3)
        km1.metric("Deforestasi", f"{base_def:.2f}%",
                   delta=f"{base_def - 2.0:+.2f}%" if base_def != 2.0 else None,
                   delta_color="inverse")
        km2.metric("Aforestasi", f"{base_aff:.2f}%",
                   delta=f"{base_aff - 0.5:+.2f}%" if base_aff != 0.5 else None)
        km3.metric("Δ Stok Karbon", f"{selisih_pct:+.1f}%",
                   delta="vs. tanpa kebijakan",
                   delta_color="normal" if selisih_pct >= 0 else "inverse")

        st.markdown(f"""
        <div class='policy-strip'>
          <span class='ps-label'>Estimasi Stok Karbon 2030</span>
          <div class='ps-val'>{hasil_pol:,.0f}
            <span style='font-size:0.95rem;font-weight:400;color:#7A9882;'> Ton</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Long-term trajectory ──
    st.write("")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='card-title'>Proyeksi Jangka Panjang 2025–2040</span>", unsafe_allow_html=True)
    st.markdown("<p class='card-sub'>Trayektori stok karbon: baseline vs. skenario kebijakan aktif.</p>", unsafe_allow_html=True)

    yrs_long = list(range(2025, 2041))
    base_traj, pol_traj = [], []
    for y in yrs_long:
        t = y - 2025
        bp = {'Year': y, 'Forest_Area_km2': 400000 * (1 - 0.015) ** t,
              'Land_Area_km2': 600000, 'Annual_Deforestation_Rate': 2.0,
              'Annual_Afforestation_Rate': 0.5}
        pp = {'Year': y,
              'Forest_Area_km2': 400000 * (1 + (base_aff - base_def) / 100) ** t,
              'Land_Area_km2': 600000, 'Annual_Deforestation_Rate': base_def,
              'Annual_Afforestation_Rate': base_aff}
        base_traj.append(prediksi_stok(bp))
        pol_traj.append(prediksi_stok(pp))

    fig_long = go.Figure()
    fig_long.add_trace(go.Scatter(
        x=yrs_long, y=base_traj, mode='lines', name='Tanpa Kebijakan',
        line=dict(color='#C0453A', width=2, dash='dot'),
        fill='tozeroy', fillcolor='rgba(192,69,58,0.04)'
    ))
    fig_long.add_trace(go.Scatter(
        x=yrs_long, y=pol_traj, mode='lines', name='Dengan Kebijakan',
        line=dict(color='#166637', width=2.5),
        fill='tozeroy', fillcolor='rgba(22,102,55,0.08)'
    ))
    fig_long.update_layout(
        **CHART_BASE,
        xaxis=AXIS_X, yaxis=AXIS_Y,
        legend=dict(**LEGEND),
        hovermode="x unified", height=260
    )
    st.plotly_chart(fig_long, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
