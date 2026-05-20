import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import time

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoAnalytics — Global Carbon",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "page"            not in st.session_state: st.session_state.page            = "dashboard"
if "filters_applied" not in st.session_state: st.session_state.filters_applied = False
if "applied_region"  not in st.session_state: st.session_state.applied_region  = None
if "applied_country" not in st.session_state: st.session_state.applied_country = None
if "applied_driver"  not in st.session_state: st.session_state.applied_driver  = None
if "applied_year"    not in st.session_state: st.session_state.applied_year    = None

# ─────────────────────────────────────────────────────────────
# CSS — DESAIN MINIMALIS ELEGAN (MOBILE FRIENDLY)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* Variabel Warna Selaras */
:root {
    --sidebar-bg:       #0F1A12;
    --sidebar-border:   #1E2E23;
    --nav-idle:         #627A6B;
    --nav-hover-bg:     rgba(255,255,255,0.05);
    --nav-active-bg:    #1C5C34;
    --nav-active:       #FFFFFF;

    --page-bg:          #F7F9F6;
    --card-bg:          #FFFFFF;
    --card-border:      #DDE4DE;
    --card-shadow:      0 2px 8px rgba(15,26,18,0.05);

    --text-primary:     #0F1A12;
    --text-secondary:   #3C4D42;
    --text-muted:       #7A8C81;

    --accent-dark:      #0C2618;
    --accent-mid:       #165C34;
    --accent-base:      #1E9E54;
    --accent-light:     #6CCB9A;
    --accent-pale:      #D8EFE5;

    --red:              #A63A3A;
    --red-pale:         #FCE8E6;

    --radius-sm:        8px;
    --radius-md:        12px;
    --radius-lg:        16px;
}

/* Reset & Basis */
*, html, body, [class*="css"] {
    font-family: 'Inter', 'DM Sans', system-ui, sans-serif !important;
    box-sizing: border-box;
}
.stApp { background: var(--page-bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2.25rem 5rem !important;
    max-width: 1300px !important;
}

/* ─────── SIDEBAR ─────── */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-border) !important;
    min-width: 230px !important;
    max-width: 230px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.75rem 1.25rem 2rem !important;
}
[data-testid="stSidebar"] * { color: var(--nav-idle) !important; }

/* Tombol navigasi sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    color: var(--nav-idle) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 0.9rem !important;
    width: 100% !important;
    text-align: left !important;
    cursor: pointer !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    box-shadow: none !important;
    transform: none !important;
    margin-bottom: 3px !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--nav-hover-bg) !important;
    color: #FFFFFF !important;
    box-shadow: none !important;
    transform: none !important;
}
[data-testid="stSidebar"] .stButton > button:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* Navigasi aktif */
.nav-item-active .stButton > button {
    background: var(--nav-active-bg) !important;
    color: var(--nav-active) !important;
    font-weight: 600 !important;
}
.nav-item-active .stButton > button:hover {
    background: #1A6237 !important;
}

/* ─────── TIPOGRAFI ─────── */
h1, h2, h3, h4 {
    font-family: 'Inter', 'DM Sans', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}
p, span, div, li { color: var(--text-secondary) !important; }
label { color: var(--text-secondary) !important; font-weight: 500; }

/* ─────── METRIK KPI ─────── */
[data-testid="stMetric"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem 1.25rem !important;
    box-shadow: var(--card-shadow) !important;
}
[data-testid="stMetricLabel"] > div {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
    line-height: 1.15 !important;
}
[data-testid="stMetricDelta"] * { font-size: 0.75rem !important; }

/* ─────── KARTU ─────── */
.eco-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    box-shadow: var(--card-shadow);
    margin-bottom: 1.2rem;
}
.eco-card-dark {
    background: linear-gradient(145deg, #0B1C13 0%, #124022 50%, #165C34 100%);
    border: 1px solid #1F402B;
    border-radius: var(--radius-lg);
    padding: 1.75rem 2rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 10px 28px rgba(15,26,18,0.25);
}
.eco-card-flat {
    background: var(--page-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
}

/* ─────── FILTER BAR ─────── */
.filter-bar {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md);
    padding: 1rem 1.4rem 1.1rem;
    margin-bottom: 1.4rem;
    box-shadow: var(--card-shadow);
}

/* ─────── FORM ELEMENTS ─────── */
.stSelectbox label, .stSlider > label,
.stNumberInput label, .stMultiSelect label,
.stTextInput label {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    margin-bottom: 0.2rem !important;
}
[data-baseweb="select"] > div {
    border-radius: var(--radius-sm) !important;
    border-color: var(--card-border) !important;
    background: var(--page-bg) !important;
}
[data-baseweb="select"] * { color: var(--text-primary) !important; }
[data-baseweb="input"] > div > input {
    border-radius: var(--radius-sm) !important;
    border-color: var(--card-border) !important;
    background: var(--page-bg) !important;
    color: var(--text-primary) !important;
}

/* ─────── TOMBOL UTAMA ─────── */
.block-container .stButton > button {
    background: var(--accent-dark) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.6rem 1.4rem !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    transition: background 0.2s ease !important;
    box-shadow: none !important;
    transform: none !important;
}
.block-container .stButton > button:hover {
    background: var(--accent-mid) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ─────── LABEL BAGIAN ─────── */
.sec-label {
    display: block;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted) !important;
    margin-bottom: 0.25rem;
}
.page-title {
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin: 0 0 0.35rem;
}
.page-sub {
    font-size: 0.85rem;
    color: var(--text-muted) !important;
    line-height: 1.65;
    margin: 0 0 1.6rem;
}
.card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary) !important;
    letter-spacing: -0.01em;
    margin: 0 0 0.12rem;
}
.card-sub {
    font-size: 0.75rem;
    color: var(--text-muted) !important;
    margin: 0 0 1rem;
    line-height: 1.5;
}

/* ─────── RESULT HERO ─────── */
.result-eyebrow {
    display: block;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-light) !important;
    margin-bottom: 0.5rem;
}
.result-number {
    font-size: 2.85rem;
    font-weight: 700;
    color: #FFFFFF !important;
    letter-spacing: -0.03em;
    line-height: 1;
}
.result-unit { font-size: 1rem; font-weight: 300; color: rgba(255,255,255,0.5) !important; }
.result-meta {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.45) !important;
    margin-top: 0.7rem;
    line-height: 1.8;
}
.result-meta strong { color: var(--accent-light) !important; }

/* ─────── POLICY STRIP ─────── */
.policy-strip {
    background: var(--page-bg);
    border-radius: var(--radius-sm);
    border-left: 3px solid var(--accent-mid);
    padding: 0.9rem 1.1rem;
    margin-top: 0.9rem;
}
.ps-label {
    display: block;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted) !important;
    margin-bottom: 0.15rem;
}
.ps-val {
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em;
}
.ps-unit { font-size: 0.9rem; font-weight: 400; color: var(--text-muted) !important; }

/* ─────── BADGE ─────── */
.badge-green {
    display: inline-block;
    background: var(--accent-pale);
    color: var(--accent-mid) !important;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.18rem 0.65rem;
    border-radius: 100px;
    border: 1px solid #B8E0C8;
}

/* ─────── EXPANDER ─────── */
.stExpander {
    border: 1px solid var(--card-border) !important;
    border-radius: var(--radius-sm) !important;
    background: var(--page-bg) !important;
}
details > summary > span { color: var(--text-muted) !important; }

/* ─────── ALERTS ─────── */
.stSuccess > div, .stError > div { border-radius: var(--radius-sm) !important; font-size: 0.84rem !important; }

/* ─────── TABLE ─────── */
.stDataFrame { border-radius: var(--radius-sm) !important; overflow: hidden !important; }
thead tr th {
    background: var(--page-bg) !important;
    color: var(--text-muted) !important;
    font-size: 0.62rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--card-border) !important;
    padding: 0.6rem 0.75rem !important;
}

/* ─────── DIVIDERS ─────── */
hr { border-color: var(--sidebar-border) !important; margin: 1rem 0 !important; }
.divider-light { border-color: var(--card-border) !important; }

/* ─────── TOGGLE ─────── */
.stToggle label span { color: var(--text-secondary) !important; font-size: 0.85rem !important; }

/* ─────── SCROLLBAR ─────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2E4A36; border-radius: 4px; }

/* ─────── MOBILE RESPONSIVE ─────── */
@media (max-width: 768px) {
    /* Sidebar lebih longgar di mobile (Streamlit akan mengganti mode) */
    [data-testid="stSidebar"] {
        min-width: 0 !important;
        max-width: 100% !important;
    }
    .block-container {
        padding: 1rem 1rem 4rem !important;
    }
    /* Paksa kolom Streamlit bertumpuk vertikal */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: 1 1 100% !important;
        width: 100% !important;
    }
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    .eco-card, .eco-card-dark, .eco-card-flat {
        padding: 1rem !important;
    }
    .page-title { font-size: 1.4rem; }
    .page-sub { font-size: 0.8rem; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    paths = [
        "/content/drive/MyDrive/Tugas Week 12/global_deforestation_2000_2025.csv",
        "global_deforestation_2000_2025.csv"
    ]

    def region(c):
        m = {
            'brazil':'Amerika Selatan','colombia':'Amerika Selatan',
            'peru':'Amerika Selatan','argentina':'Amerika Selatan',
            'indonesia':'Asia Tenggara','malaysia':'Asia Tenggara',
            'thailand':'Asia Tenggara','vietnam':'Asia Tenggara',
            'india':'Asia','china':'Asia',
            'canada':'Amerika Utara','usa':'Amerika Utara',
            'congo':'Afrika','nigeria':'Afrika',
            'russia':'Eropa & Asia','ukraine':'Eropa & Asia',
            'australia':'Oseania','new zealand':'Oseania',
        }
        return m.get(str(c).lower(), 'Lainnya')

    for p in paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            if 'Region' not in df.columns:
                df['Region'] = df['Country'].apply(region)
            return df

    # Dummy fallback
    np.random.seed(42)
    countries = ['Brazil','Indonesia','Canada','Russia','USA',
                 'Congo','Australia','India','China','Malaysia']
    rows = []
    for c in countries:
        bf = np.random.uniform(100000, 600000)
        bc = np.random.uniform(8e9, 4.5e10)
        for y in range(2000, 2026):
            d  = np.random.uniform(0.3, 3.0)
            a  = np.random.uniform(0.1, 2.0)
            fa = bf * (1 - 0.01 * (y-2000) * (d - a*0.4))
            rows.append({
                'Country': c, 'Year': y,
                'Forest_Area_km2': max(fa, 5000),
                'Land_Area_km2': bf * np.random.uniform(1.3, 2.2),
                'Annual_Deforestation_Rate': d,
                'Annual_Afforestation_Rate': a,
                'Total_Carbon_Stock_Tonnes': max(bc*(fa/bf)*np.random.uniform(0.97,1.03), 1e8),
                'Primary_Driver_of_Change': np.random.choice(
                    ['Pertanian','Kebakaran','Pertambangan','Penebangan'],
                    p=[0.45,0.25,0.15,0.15]
                ),
                'Region': region(c)
            })
    return pd.DataFrame(rows)


def predict_carbon(f: dict) -> float:
    log_f = np.log1p(max(f['Forest_Area_km2'], 1.0))
    ratio = f['Forest_Area_km2'] / (f['Land_Area_km2'] + 1e-6)
    val = (4.2 + 0.94*log_f + 0.08*ratio
           - 0.04*f['Annual_Deforestation_Rate']
           + 0.025*f.get('Annual_Afforestation_Rate', 0))
    return max(np.expm1(val), 0)


df       = load_data()
COUNTRIES = sorted([str(x) for x in df['Country'].dropna().unique()])
DRIVERS   = sorted([str(x) for x in df['Primary_Driver_of_Change'].dropna().unique()])
REGIONS   = sorted([str(x) for x in df['Region'].dropna().unique()])
YEAR_MIN  = int(df['Year'].min()) if not df['Year'].isnull().all() else 2000
YEAR_MAX  = int(df['Year'].max()) if not df['Year'].isnull().all() else 2025

# Inisialisasi default filter
if st.session_state.applied_region  is None: st.session_state.applied_region  = REGIONS
if st.session_state.applied_country is None: st.session_state.applied_country = COUNTRIES
if st.session_state.applied_driver  is None: st.session_state.applied_driver  = DRIVERS
if st.session_state.applied_year    is None: st.session_state.applied_year    = YEAR_MAX

# Palet & pengaturan chart (lebih lembut)
CSCALE = [[0.0, '#D8EFE5'], [0.3, '#6CCB9A'], [0.65, '#165C34'], [1.0, '#0C2618']]
COLORS  = ['#0C2618','#165C34','#1E9E54','#6CCB9A','#B8E0C8','#D8EFE5']
CHART   = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
               margin=dict(l=0,r=0,t=4,b=0), font=dict(family='Inter, DM Sans', color='#7A8C81'))
AX_X    = dict(showgrid=False, tickfont=dict(family='Inter, DM Sans', size=10, color='#7A8C81'),
               linecolor='#DDE4DE', linewidth=1)
AX_Y    = dict(showgrid=True, gridcolor='#EDF2ED', gridwidth=1,
               tickfont=dict(family='Inter, DM Sans', size=10, color='#7A8C81'), zeroline=False)
LEG     = dict(font=dict(family='Inter, DM Sans', size=10, color='#3C4D42'), bgcolor='rgba(0,0,0,0)')


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown("""
    <div style="margin-bottom:2rem;padding-bottom:1.25rem;
                border-bottom:1px solid #1E2E23;">
      <div style="display:flex;align-items:center;gap:7px;margin-bottom:2px;">
        <div style="width:7px;height:7px;border-radius:50%;
                    background:#1E9E54;flex-shrink:0;"></div>
        <span style="font-size:1rem;font-weight:600;letter-spacing:-0.02em;
                     color:#E8F4EC !important;">EcoAnalytics</span>
      </div>
      <p style="font-size:0.58rem;color:#627A6B !important;letter-spacing:0.12em;
                text-transform:uppercase;margin:0 0 0 14px;">
        Global Carbon Stock
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Navigasi
    nav_pages = [
        ("dashboard", "🌍", "Dashboard"),
        ("simulator", "📈", "Simulator"),
        ("kebijakan", "⚖️", "Kebijakan"),
    ]
    for key, icon, label in nav_pages:
        is_active = st.session_state.page == key
        open_tag = "<div class='nav-item-active'>" if is_active else "<div>"
        st.markdown(open_tag, unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Info footer
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown("""<hr style="border-color:#1E2E23 !important;">""", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:0 0.25rem;">
      <p style="font-size:0.58rem;font-weight:600;letter-spacing:0.1em;
                text-transform:uppercase;color:#627A6B !important;margin-bottom:0.5rem;">
        Tentang
      </p>
      <p style="font-size:0.75rem;color:#627A6B !important;line-height:1.8;margin:0;">
        <span style="color:#6CCB9A !important;font-weight:600;">Kelompok 6</span><br>
        Python System Analytics<br>
        Fak. Teknologi Informasi
      </p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
page = st.session_state.page
# ─────────────────────────────────────────────────────────────


# ═══════════════════════ DASHBOARD ══════════════════════════
if page == "dashboard":

    st.markdown("""
    <span class='sec-label'>Pemantauan</span>
    <p class='page-title'>Dashboard Stok Karbon Global</p>
    <p class='page-sub'>Distribusi biomassa, tren deforestasi, dan tutupan hutan dunia.</p>
    """, unsafe_allow_html=True)

    # ── Filter Bar (dua baris agar ramah mobile) ──
    st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)
    st.markdown("""<p style="font-size:0.6rem;font-weight:600;letter-spacing:0.1em;
        text-transform:uppercase;color:#7A8C81 !important;margin:0 0 0.75rem;">
        Filter Data</p>""", unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        sel_region = st.multiselect("Kawasan", REGIONS,
                                    default=st.session_state.applied_region,
                                    placeholder="Semua kawasan")
    with fc2:
        sel_country = st.multiselect("Negara", COUNTRIES,
                                     default=st.session_state.applied_country,
                                     placeholder="Semua negara")
    with fc3:
        sel_driver  = st.multiselect("Pemicu", DRIVERS,
                                     default=st.session_state.applied_driver,
                                     placeholder="Semua pemicu")

    fc4, fc5, fc6 = st.columns([2, 1, 1])
    with fc4:
        sel_year = st.selectbox("Tahun",
                                list(range(YEAR_MIN, YEAR_MAX + 1)),
                                index=list(range(YEAR_MIN, YEAR_MAX+1)).index(
                                    st.session_state.applied_year))
    with fc5:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        apply_btn = st.button("Terapkan")
    with fc6:
        st.write("")   # dummy

    if apply_btn:
        st.session_state.applied_region  = sel_region  or REGIONS
        st.session_state.applied_country = sel_country or COUNTRIES
        st.session_state.applied_driver  = sel_driver  or DRIVERS
        st.session_state.applied_year    = sel_year
        st.session_state.filters_applied = True
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Terapkan filter ──
    AR = st.session_state.applied_region
    AC = st.session_state.applied_country
    AD = st.session_state.applied_driver
    AY = st.session_state.applied_year

    df_f  = df[
        df['Region'].astype(str).isin(AR) &
        df['Country'].astype(str).isin(AC) &
        df['Primary_Driver_of_Change'].astype(str).isin(AD)
    ]
    df_yr = df_f[df_f['Year'] == AY]

    # ── KPI ──
    total_c  = df_yr['Total_Carbon_Stock_Tonnes'].sum()
    total_f  = df_yr['Forest_Area_km2'].sum()
    avg_d    = df_yr['Annual_Deforestation_Rate'].mean()
    avg_a    = df_yr['Annual_Afforestation_Rate'].mean()
    base_d   = df[df['Year']==YEAR_MIN]['Annual_Deforestation_Rate'].mean()
    if np.isnan(base_d): base_d = 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Stok Karbon Total",  f"{total_c/1e12:.2f} Tt")
    k2.metric("Luas Hutan",         f"{total_f/1e6:.2f} jt km²")
    k3.metric("Rata‑rata Deforestasi", f"{avg_d:.2f}%/thn",
              delta=f"{avg_d-base_d:+.2f}% vs {YEAR_MIN}",
              delta_color="inverse")
    k4.metric("Rata‑rata Aforestasi",  f"{avg_a:.2f}%/thn")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Peta + Donut ──
    col_a, col_b = st.columns([3, 2], gap="large")

    with col_a:
        st.markdown("""<div class='eco-card'>
          <span class='card-title'>Distribusi Stok Karbon per Negara</span>
          <p class='card-sub'>Intensitas cadangan karbon pada tahun yang dipilih.</p>
        """, unsafe_allow_html=True)
        fig_map = px.choropleth(
            df_yr, locations="Country", locationmode="country names",
            color="Total_Carbon_Stock_Tonnes",
            color_continuous_scale=CSCALE,
            labels={"Total_Carbon_Stock_Tonnes":"Stok Karbon (T)"}
        )
        fig_map.update_layout(
            **CHART,
            geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#D0DDD0",
                     projection_type='natural earth', bgcolor='rgba(0,0,0,0)',
                     showland=True, landcolor="#EEF3EE",
                     showocean=True, oceancolor="#E6EEF4"),
            coloraxis_colorbar=dict(title="", thickness=5, len=0.45,
                                    tickfont=dict(family='Inter, DM Sans', size=9, color='#7A8C81'))
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("""<div class='eco-card'>
          <span class='card-title'>Pemicu Utama Deforestasi</span>
          <p class='card-sub'>Proporsi faktor penyebab kehilangan tutupan hutan.</p>
        """, unsafe_allow_html=True)
        drv = df_f.groupby('Primary_Driver_of_Change').size().reset_index(name='n')
        fig_pie = go.Figure(go.Pie(
            labels=drv['Primary_Driver_of_Change'], values=drv['n'],
            hole=0.66,
            marker_colors=['#0C2618','#165C34','#1E9E54','#6CCB9A'],
            textfont=dict(family='Inter, DM Sans', size=11),
            hovertemplate="<b>%{label}</b><br>%{value} kasus<extra></extra>"
        ))
        fig_pie.update_layout(
            **CHART,
            showlegend=True,
            legend=dict(**LEG, orientation='v', x=0.6, y=0.5, yanchor='middle'),
            annotations=[dict(
                text=f"<b>{drv['n'].sum()}</b><br><span style='font-size:9px'>Total</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(family='Inter, DM Sans', size=16, color='#0F1A12')
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tren + Peringkat ──
    col_c, col_d = st.columns([3, 2], gap="large")

    with col_c:
        st.markdown("""<div class='eco-card'>
          <span class='card-title'>Tren Stok Karbon 2000–2025</span>
          <p class='card-sub'>Perubahan cadangan karbon tahunan per negara.</p>
        """, unsafe_allow_html=True)
        trend = df_f.groupby(['Year','Country'])['Total_Carbon_Stock_Tonnes'].mean().reset_index()
        fig_tr = px.line(trend, x='Year', y='Total_Carbon_Stock_Tonnes', color='Country',
                         color_discrete_sequence=COLORS,
                         labels={'Total_Carbon_Stock_Tonnes':'Stok Karbon (T)','Year':'Tahun'})
        fig_tr.update_layout(**CHART, xaxis=AX_X, yaxis=AX_Y,
                             legend=dict(**LEG), hovermode='x unified')
        fig_tr.update_traces(line=dict(width=1.8))
        st.plotly_chart(fig_tr, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d:
        st.markdown("""<div class='eco-card'>
          <span class='card-title'>Peringkat Negara</span>
          <p class='card-sub'>Stok karbon tertinggi pada tahun terpilih.</p>
        """, unsafe_allow_html=True)
        top8 = df_yr.nlargest(8, 'Total_Carbon_Stock_Tonnes')
        fig_bar = go.Figure(go.Bar(
            x=top8['Total_Carbon_Stock_Tonnes']/1e9,
            y=top8['Country'],
            orientation='h',
            marker=dict(color=top8['Total_Carbon_Stock_Tonnes'],
                        colorscale=[[0,'#B8E0C8'],[1,'#0C2618']], showscale=False),
            text=[f"{v:.1f} Gt" for v in top8['Total_Carbon_Stock_Tonnes']/1e9],
            textposition='outside',
            textfont=dict(family='Inter, DM Sans', size=10, color='#7A8C81'),
            hovertemplate="<b>%{y}</b>: %{x:.2f} Gt<extra></extra>"
        ))
        fig_bar.update_layout(
            **CHART,
            xaxis=dict(**AX_X, title=dict(text='Giga Ton',
                        font=dict(family='Inter, DM Sans', size=10, color='#7A8C81'))),
            yaxis=dict(**AX_Y, showgrid=False,
                       tickfont=dict(family='Inter, DM Sans', size=11, color='#3C4D42')),
            margin=dict(l=0, r=58, t=4, b=0), height=295
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tabel Detail ──
    st.markdown("""<div class='eco-card'>
      <span class='card-title'>Data Detail</span>
      <p class='card-sub'>Ringkasan terfilter untuk tahun yang dipilih.</p>
    """, unsafe_allow_html=True)
    tbl = df_yr[['Country','Region','Forest_Area_km2','Annual_Deforestation_Rate',
                 'Annual_Afforestation_Rate','Total_Carbon_Stock_Tonnes',
                 'Primary_Driver_of_Change']].copy()
    tbl.columns = ['Negara','Kawasan','Luas Hutan (km²)','Deforestasi (%)',
                   'Aforestasi (%)','Stok Karbon (Ton)','Pemicu Utama']
    for col, fmt in [('Luas Hutan (km²)','{:,.0f}'),('Stok Karbon (Ton)','{:,.0f}'),
                     ('Deforestasi (%)','{:.2f}'),('Aforestasi (%)','{:.2f}')]:
        tbl[col] = tbl[col].map(fmt.format)
    st.dataframe(tbl, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════ SIMULATOR ══════════════════════════
elif page == "simulator":

    st.markdown("""
    <span class='sec-label'>Pemodelan Prediktif</span>
    <p class='page-title'>Simulator Proyeksi Ekologi</p>
    <p class='page-sub'>Atur parameter dan lihat proyeksi cadangan karbon berdasarkan model estimasi historis.</p>
    """, unsafe_allow_html=True)

    with st.form("form_sim"):
        st.markdown("<div class='eco-card'>", unsafe_allow_html=True)
        st.markdown("""<p style="font-size:0.6rem;font-weight:600;letter-spacing:0.1em;
            text-transform:uppercase;color:#7A8C81 !important;margin:0 0 0.9rem;">
            Konfigurasi Skenario</p>""", unsafe_allow_html=True)

        r1c1, r1c2, r1c3 = st.columns([1,1,2])
        negara     = r1c1.selectbox("Negara Fokus", COUNTRIES)
        pemicu     = r1c2.selectbox("Pemicu Utama", DRIVERS)
        thn_target = r1c3.slider("Target Tahun Proyeksi", 2026, 2060, 2035)

        st.markdown("<hr style='border-color:#DDE4DE !important;margin:1rem 0 !important;'>",
                    unsafe_allow_html=True)
        st.markdown("""<p style="font-size:0.6rem;font-weight:600;letter-spacing:0.1em;
            text-transform:uppercase;color:#7A8C81 !important;margin:0 0 0.9rem;">
            Skenario Intervensi</p>""", unsafe_allow_html=True)

        s1, s2 = st.columns(2, gap="large")
        laju_d = s1.slider("Laju Deforestasi  (% / tahun)", 0.0, 5.0, 1.2, 0.1)
        laju_a = s2.slider("Laju Aforestasi  (% / tahun)",  0.0, 5.0, 0.5, 0.1)

        with st.expander("Parameter Lanjutan"):
            a1, a2 = st.columns(2)
            luas_h = a1.number_input("Luas Hutan Awal (km²)",   value=250000, step=5000)
            luas_l = a2.number_input("Luas Total Daratan (km²)", value=400000, step=5000)
            sken   = st.selectbox("Skenario Iklim",
                                  ["Optimis (RCP 2.6)","Moderat (RCP 4.5)","Pesimis (RCP 8.5)"])

        st.write("")
        run_btn = st.form_submit_button("▶  Jalankan Simulasi")
        st.markdown("</div>", unsafe_allow_html=True)

    if run_btn:
        with st.spinner("Menghitung trayektori..."):
            time.sleep(0.7)
            f_iklim = {"Optimis (RCP 2.6)":1.02,"Moderat (RCP 4.5)":1.0,
                       "Pesimis (RCP 8.5)":0.97}.get(sken, 1.0)
            hasil_list, thn_list = [], []
            for y in range(YEAR_MAX, thn_target+1):
                fa = luas_h * (1+(laju_a-laju_d)/100)**(y-YEAR_MAX)
                hasil_list.append(predict_carbon({
                    'Year':y,'Forest_Area_km2':max(fa*f_iklim,1000),
                    'Land_Area_km2':luas_l,'Annual_Deforestation_Rate':laju_d,
                    'Annual_Afforestation_Rate':laju_a
                }))
                thn_list.append(y)

        h_end   = hasil_list[-1]
        h_start = hasil_list[0]
        pct     = (h_end-h_start)/h_start*100
        net     = laju_a - laju_d

        st.markdown(f"""
        <div class='eco-card-dark'>
          <span class='result-eyebrow'>Proyeksi Cadangan Karbon — {thn_target}</span>
          <div class='result-number'>{h_end:,.0f}
            <span class='result-unit'> Ton</span>
          </div>
          <p class='result-meta'>
            Negara: <strong>{negara}</strong>&emsp;
            Pemicu: <strong>{pemicu}</strong>&emsp;
            Tren: <strong>{'Pemulihan' if net>=0 else 'Penurunan'}</strong>&emsp;
            Δ: <strong>{pct:+.1f}%</strong>
          </p>
        </div>
        """, unsafe_allow_html=True)

        g1, g2 = st.columns([3,1], gap="large")
        with g1:
            st.markdown("""<div class='eco-card'>
              <span class='card-title'>Trayektori Proyeksi</span>
              <p class='card-sub'>Estimasi cadangan karbon hingga tahun target.</p>
            """, unsafe_allow_html=True)
            df_proj = pd.DataFrame({'Tahun':thn_list,'Stok Karbon':hasil_list})
            fg = go.Figure(go.Scatter(
                x=df_proj['Tahun'], y=df_proj['Stok Karbon'],
                mode='lines', line=dict(color='#165C34', width=2.5),
                fill='tozeroy', fillcolor='rgba(22,92,52,0.07)',
                hovertemplate="Tahun %{x}<br>%{y:,.0f} Ton<extra></extra>"
            ))
            fg.update_layout(**CHART, xaxis=AX_X, yaxis=AX_Y, height=235)
            st.plotly_chart(fg, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with g2:
            st.markdown("<div class='eco-card-flat'>", unsafe_allow_html=True)
            st.markdown("<span class='card-title'>Ringkasan</span>", unsafe_allow_html=True)
            st.write("")
            st.metric("Stok Awal (2025)",  f"{h_start:,.0f} T")
            st.metric("Stok Target",       f"{h_end:,.0f} T",
                      delta=f"{pct:+.1f}%",
                      delta_color="normal" if pct>0 else "inverse")
            st.metric("Laju Bersih",       f"{net:+.1f}%/thn",
                      delta_color="normal" if net>0 else "inverse")
            st.markdown("</div>", unsafe_allow_html=True)

        if net >= 0:
            st.success(f"Skenario Positif — Aforestasi melampaui deforestasi sebesar {net:.1f}%/thn. "
                       f"Ekosistem diproyeksikan pulih bertahap hingga {thn_target}.")
        else:
            st.error(f"Peringatan — Deforestasi mendominasi sebesar {abs(net):.1f}%/thn. "
                     f"Cadangan karbon menyusut kritis hingga {thn_target}.")


# ═══════════════════════ KEBIJAKAN ══════════════════════════
else:

    st.markdown("""
    <span class='sec-label'>Laboratorium Regulasi</span>
    <p class='page-title'>Simulator Dampak Kebijakan</p>
    <p class='page-sub'>Aktifkan intervensi regulasi dan amati dampaknya terhadap ekosistem hutan 2030.</p>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([4,6], gap="large")

    with col_l:
        st.markdown("<div class='eco-card'>", unsafe_allow_html=True)
        st.markdown("""<p style="font-size:0.6rem;font-weight:600;letter-spacing:0.1em;
            text-transform:uppercase;color:#7A8C81 !important;margin:0 0 1rem;">
            Panel Intervensi</p>
            <h4 style="font-size:0.95rem;margin:0 0 1.2rem;color:#0F1A12 !important;">
            Kontrol Regulasi</h4>""", unsafe_allow_html=True)

        p1 = st.toggle("Moratorium Penebangan Komersial",
                        help="Mengurangi deforestasi industri kayu hingga 70%.")
        st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
        p2 = st.toggle("Dana Reboisasi Masif",
                        help="Mendongkrak laju aforestasi 3× melalui investasi publik.")
        st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
        p3 = st.toggle("Sanksi Tegas Pembakaran Lahan",
                        help="Menghapus pembakaran sebagai pemicu kerusakan hutan.")
        st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
        p4 = st.toggle("Insentif Petani Hutan",
                        help="Memotivasi petani untuk menjaga hutan bukan membuka lahan.")

        st.markdown("<hr style='border-color:#DDE4DE !important;margin:1.1rem 0 !important;'>",
                    unsafe_allow_html=True)

        aktif = {"Moratorium Penebangan":p1,"Dana Reboisasi":p2,
                 "Sanksi Pembakaran":p3,"Insentif Petani":p4}
        n_aktif = sum(aktif.values())

        if n_aktif:
            st.markdown(f"<span class='badge-green'>{n_aktif} Kebijakan Aktif</span>",
                        unsafe_allow_html=True)
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
            for nm, val in aktif.items():
                if val:
                    st.markdown(
                        f"<p style='font-size:0.79rem;color:#165C34 !important;"
                        f"margin:3px 0;font-weight:600;'>✓ {nm}</p>",
                        unsafe_allow_html=True)
        else:
            st.markdown(
                "<p style='font-size:0.79rem;color:#7A8C81 !important;"
                "font-style:italic;margin:0;'>Belum ada intervensi aktif.</p>",
                unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        bd, ba = 2.0, 0.5
        if p1: bd *= 0.3
        if p2: ba *= 3.0
        if p3: bd *= 0.8
        if p4: ba *= 1.4; bd *= 0.9

        pp  = {'Year':2030,'Forest_Area_km2':400000,'Land_Area_km2':600000,
               'Annual_Deforestation_Rate':bd,'Annual_Afforestation_Rate':ba}
        h_pol  = predict_carbon(pp)
        h_base = predict_carbon({**pp,'Annual_Deforestation_Rate':2.0,'Annual_Afforestation_Rate':0.5})
        pct_pol = (h_pol-h_base)/h_base*100

        st.markdown("<div class='eco-card'>", unsafe_allow_html=True)
        st.markdown("""<p style="font-size:0.6rem;font-weight:600;letter-spacing:0.1em;
            text-transform:uppercase;color:#7A8C81 !important;margin:0 0 1rem;">
            Dampak Proyeksi 2030</p>
            <h4 style="font-size:0.95rem;margin:0 0 1.2rem;color:#0F1A12 !important;">
            Hasil Simulasi</h4>""", unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Deforestasi", f"{bd:.2f}%",
                  delta=f"{bd-2.0:+.2f}%" if bd!=2.0 else None, delta_color="inverse")
        m2.metric("Aforestasi",  f"{ba:.2f}%",
                  delta=f"{ba-0.5:+.2f}%" if ba!=0.5 else None)
        m3.metric("Δ Stok Karbon", f"{pct_pol:+.1f}%",
                  delta="vs. baseline", delta_color="normal" if pct_pol>=0 else "inverse")

        st.markdown(f"""
        <div class='policy-strip'>
          <span class='ps-label'>Estimasi Stok Karbon 2030</span>
          <div class='ps-val'>{h_pol:,.0f}
            <span class='ps-unit'> Ton</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
    st.markdown("""<div class='eco-card'>
      <span class='card-title'>Proyeksi Jangka Panjang 2025–2040</span>
      <p class='card-sub'>Trayektori stok karbon: skenario baseline vs. kebijakan aktif.</p>
    """, unsafe_allow_html=True)

    yrs = list(range(2025, 2041))
    b_traj, p_traj = [], []
    for y in yrs:
        t = y-2025
        b_traj.append(predict_carbon({
            'Year':y,'Forest_Area_km2':400000*(1-0.015)**t,
            'Land_Area_km2':600000,'Annual_Deforestation_Rate':2.0,
            'Annual_Afforestation_Rate':0.5
        }))
        p_traj.append(predict_carbon({
            'Year':y,'Forest_Area_km2':400000*(1+(ba-bd)/100)**t,
            'Land_Area_km2':600000,'Annual_Deforestation_Rate':bd,
            'Annual_Afforestation_Rate':ba
        }))

    fl = go.Figure()
    fl.add_trace(go.Scatter(
        x=yrs, y=b_traj, mode='lines', name='Tanpa Kebijakan',
        line=dict(color='#A63A3A', width=2, dash='dot'),
        fill='tozeroy', fillcolor='rgba(166,58,58,0.05)'
    ))
    fl.add_trace(go.Scatter(
        x=yrs, y=p_traj, mode='lines', name='Dengan Kebijakan',
        line=dict(color='#165C34', width=2.5),
        fill='tozeroy', fillcolor='rgba(22,92,52,0.07)'
    ))
    fl.update_layout(**CHART, xaxis=AX_X, yaxis=AX_Y,
                     legend=dict(**LEG), hovermode='x unified', height=255)
    st.plotly_chart(fl, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
