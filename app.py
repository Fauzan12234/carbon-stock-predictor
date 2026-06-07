import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import joblib

# Konfigurasi Halaman
st.set_page_config(
    page_title="Global Carbon Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inisialisasi State
if "page" not in st.session_state: st.session_state.page = "dashboard"
if "filters_applied" not in st.session_state: st.session_state.filters_applied = False
if "applied_region" not in st.session_state: st.session_state.applied_region = []
if "applied_country" not in st.session_state: st.session_state.applied_country = []
if "applied_driver" not in st.session_state: st.session_state.applied_driver = []
if "applied_year" not in st.session_state: st.session_state.applied_year = None
if "adv_open" not in st.session_state: st.session_state.adv_open = False
if "sim_run" not in st.session_state: st.session_state.sim_run = False
if "pol_run" not in st.session_state: st.session_state.pol_run = False

# ============================================================
# CSS — PIXEL ART GREEN THEME (REVISED)
# Palet ketat: #FFFFFF · #DCFCE7/#BBF7D0/#4ADE80/#22C55E · #166534/#064E3B
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

/* ── GLOBAL RESET ─────────────────────────────────────────── */
* {
    font-family: 'Press Start 2P', cursive !important;
    color: #064E3B !important;
    box-sizing: border-box !important;
}

/* ── APP BACKGROUND — semua layer ─────────────────────────── */
html, body {
    background-color: #F0FDF4 !important;
    background-image: none !important;
}
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background-color: #F0FDF4 !important;
    background-image: none !important;
}
[data-testid="stHeader"] {
    background-color: #F0FDF4 !important;
    border-bottom: 3px solid #22C55E !important;
    box-shadow: none !important;
}
[data-testid="stBottomBlockContainer"],
[data-testid="stStatusWidget"],
footer {
    background-color: #F0FDF4 !important;
}
[data-testid="stSidebar"] { display: none !important; }

/* Block container — lebih lega */
.block-container {
    padding: 3rem 3.5rem 8rem !important;
    max-width: 1280px !important;
    background-color: transparent !important;
}

/* ── KARTU CONTAINER (PIXEL SOLID) ────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    box-shadow: 6px 6px 0px #22C55E !important;
    padding: 2rem 2rem !important;
    margin-bottom: 2.25rem !important;
}

/* ── TOMBOL ────────────────────────────────────────────────── */
.stButton > button {
    background-color: #4ADE80 !important;
    color: #064E3B !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    box-shadow: 4px 4px 0px #064E3B !important;
    font-family: 'Press Start 2P', cursive !important;
    font-size: 0.65rem !important;
    padding: 0.75rem 1rem !important;
    line-height: 1.6 !important;
    transition: none !important;
    cursor: pointer !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0px #064E3B !important;
    background-color: #22C55E !important;
}
.stButton > button:active {
    transform: translate(4px, 4px) !important;
    box-shadow: none !important;
}

/* ── METRIK ────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background-color: #DCFCE7 !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    padding: 1.25rem 1rem !important;
    text-align: center !important;
    box-shadow: 4px 4px 0px #22C55E !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] p {
    font-size: 0.58rem !important;
    color: #064E3B !important;
    line-height: 1.7 !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 1.1rem !important;
    color: #064E3B !important;
}
[data-testid="stMetricDelta"] { display: none !important; }

/* ── LABEL FORM ────────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p,
.stSelectbox label,
.stMultiSelect label,
.stSlider > label,
.stNumberInput label,
.stTextInput label {
    font-size: 0.65rem !important;
    color: #064E3B !important;
    margin-bottom: 0.5rem !important;
    display: block !important;
    line-height: 1.7 !important;
}

/* ── SELECT / DROPDOWN ─────────────────────────────────────── */
/* Outer wrapper */
div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
}
/* Trigger box */
div[data-baseweb="select"] > div:first-child {
    background-color: #FFFFFF !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    min-height: 2.8rem !important;
    padding: 0.35rem 0.75rem !important;
    cursor: pointer !important;
}
div[data-baseweb="select"] > div:first-child:hover,
div[data-baseweb="select"] > div:first-child:focus-within {
    background-color: #F0FDF4 !important;
    border-color: #064E3B !important;
    box-shadow: 3px 3px 0px #22C55E !important;
}
/* Teks nilai & placeholder */
div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] [class*="placeholder"],
div[data-baseweb="select"] [class*="singleValue"],
div[data-baseweb="select"] [class*="Input"] {
    color: #064E3B !important;
    font-size: 0.65rem !important;
    font-family: 'Press Start 2P', cursive !important;
    background-color: transparent !important;
}
/* Ikon panah */
div[data-baseweb="select"] svg,
div[data-baseweb="select"] [class*="indicatorContainer"] svg {
    fill: #064E3B !important;
    color: #064E3B !important;
}

/* ── DROPDOWN POPOVER / MENU ───────────────────────────────── */
[data-baseweb="popover"] {
    background-color: #FFFFFF !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    box-shadow: 6px 6px 0px #22C55E !important;
    overflow: hidden !important;
}
[data-baseweb="popover"] > div,
[data-baseweb="popover"] > div > div {
    background-color: #FFFFFF !important;
}
ul[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: none !important;
    padding: 4px 4px !important;
    margin: 0 !important;
}
li[data-baseweb="option"],
[role="option"] {
    background-color: #FFFFFF !important;
    color: #064E3B !important;
    font-family: 'Press Start 2P', cursive !important;
    font-size: 0.58rem !important;
    padding: 0.75rem 0.9rem !important;
    cursor: pointer !important;
    border-bottom: 2px solid #F0FDF4 !important;
    line-height: 1.6 !important;
}
li[data-baseweb="option"]:last-child,
[role="option"]:last-child {
    border-bottom: none !important;
}
li[data-baseweb="option"]:hover,
[role="option"]:hover {
    background-color: #DCFCE7 !important;
}
li[data-baseweb="option"][aria-selected="true"],
[role="option"][aria-selected="true"] {
    background-color: #BBF7D0 !important;
    color: #064E3B !important;
}

/* ── MULTISELECT TAGS ──────────────────────────────────────── */
span[data-baseweb="tag"] {
    background-color: #4ADE80 !important;
    border: 2px solid #064E3B !important;
    border-radius: 0px !important;
    padding: 0.2rem 0.5rem !important;
    margin: 2px !important;
    box-shadow: 2px 2px 0px #064E3B !important;
}
span[data-baseweb="tag"] span {
    color: #064E3B !important;
    font-size: 0.55rem !important;
    font-family: 'Press Start 2P', cursive !important;
}
span[data-baseweb="tag"] button,
span[data-baseweb="tag"] [role="presentation"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    cursor: pointer !important;
}
span[data-baseweb="tag"] svg,
span[data-baseweb="tag"] button svg {
    fill: #064E3B !important;
    color: #064E3B !important;
}

/* ── NUMBER INPUT ──────────────────────────────────────────── */
div[data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    overflow: hidden !important;
}
div[data-baseweb="base-input"] input {
    background-color: #FFFFFF !important;
    color: #064E3B !important;
    font-size: 0.65rem !important;
    font-family: 'Press Start 2P', cursive !important;
    border: none !important;
    padding: 0.5rem 0.75rem !important;
}
div[data-baseweb="base-input"]:focus-within {
    border-color: #064E3B !important;
    box-shadow: 4px 4px 0px #22C55E !important;
}
/* Tombol +/- number input */
[data-testid="stNumberInputContainer"] button {
    background-color: #DCFCE7 !important;
    border: none !important;
    border-left: 3px solid #064E3B !important;
    color: #064E3B !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    padding: 0.3rem 0.6rem !important;
}
[data-testid="stNumberInputContainer"] button:hover {
    background-color: #4ADE80 !important;
    box-shadow: none !important;
}
[data-testid="stNumberInputContainer"] button svg {
    fill: #064E3B !important;
    color: #064E3B !important;
}

/* ── SLIDER ────────────────────────────────────────────────── */
/* Label nilai */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"],
.stSlider p {
    font-size: 0.55rem !important;
    color: #064E3B !important;
    font-family: 'Press Start 2P', cursive !important;
}
/* Track warna */
.stSlider > div > div > div > div {
    background-color: #DCFCE7 !important;
}
/* Thumb */
.stSlider > div > div > div > div > div[role="slider"],
[data-testid="stSlider"] [role="slider"] {
    background-color: #064E3B !important;
    border: 3px solid #064E3B !important;
    box-shadow: 3px 3px 0px #22C55E !important;
    width: 20px !important;
    height: 20px !important;
}
/* Bagian track yang aktif (terisi) */
.stSlider > div > div > div > div:nth-child(2) {
    background-color: #4ADE80 !important;
}

/* ── TOGGLE ────────────────────────────────────────────────── */
[data-testid="stToggle"] label p {
    font-size: 0.65rem !important;
    color: #064E3B !important;
    font-family: 'Press Start 2P', cursive !important;
}
[data-testid="stToggle"] div[role="switch"] {
    border: 3px solid #064E3B !important;
    background-color: #DCFCE7 !important;
}
[data-testid="stToggle"] div[role="switch"][aria-checked="true"] {
    background-color: #4ADE80 !important;
    border-color: #064E3B !important;
}
[data-testid="stToggle"] div[role="switch"] > div {
    background-color: #FFFFFF !important;
    border: 2px solid #064E3B !important;
    box-shadow: 2px 2px 0px #064E3B !important;
}

/* ── DIVIDER ───────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 3px solid #DCFCE7 !important;
    margin: 1.75rem 0 !important;
}

/* ── COLUMNS SPACING ───────────────────────────────────────── */
[data-testid="stColumns"] > [data-testid="column"] {
    padding-left: 0.6rem !important;
    padding-right: 0.6rem !important;
}
[data-testid="stColumns"] > [data-testid="column"]:first-child {
    padding-left: 0 !important;
}
[data-testid="stColumns"] > [data-testid="column"]:last-child {
    padding-right: 0 !important;
}

/* ── TEKS CUSTOM ───────────────────────────────────────────── */
.title-text {
    font-size: 1.35rem !important;
    margin-bottom: 0.75rem !important;
    color: #064E3B !important;
    text-transform: uppercase;
    line-height: 1.7;
    letter-spacing: 0.03rem;
}
.sub-text {
    font-size: 0.65rem !important;
    margin-bottom: 0.5rem !important;
    color: #166534 !important;
    line-height: 2;
}
.header-text {
    font-size: 0.88rem !important;
    margin-bottom: 1.25rem !important;
    color: #064E3B !important;
    padding-bottom: 0.65rem !important;
    border-bottom: 3px solid #DCFCE7 !important;
    display: block !important;
    line-height: 1.5 !important;
}
.insight-text {
    font-size: 0.68rem !important;
    line-height: 2.1 !important;
    color: #064E3B !important;
    background-color: #DCFCE7 !important;
    padding: 1.5rem 1.75rem !important;
    border: 4px dashed #064E3B !important;
    border-radius: 0 !important;
    margin-top: 1.5rem !important;
}

/* ── MARKDOWN & TEKS UMUM ──────────────────────────────────── */
.stMarkdown p,
.stMarkdown span,
p, span {
    color: #064E3B !important;
}
.stMarkdown p {
    font-size: 0.65rem !important;
    line-height: 1.9 !important;
}

/* ── PLOTLY CHART ──────────────────────────────────────────── */
.js-plotly-plot, .plotly, .stPlotlyChart {
    background: transparent !important;
}

/* ── OVERLAY / PORTAL FALLBACK ─────────────────────────────── */
/* Memastikan elemen popover yang di-mount di root juga putih */
[data-baseweb="tooltip"],
[data-baseweb="layer"] {
    background-color: #FFFFFF !important;
}

</style>
""", unsafe_allow_html=True)

# Navigasi Menu
nav_1, nav_2, nav_3 = st.columns(3)
with nav_1:
    if st.button("DASHBOARD", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()
with nav_2:
    if st.button("SIMULATOR", use_container_width=True):
        st.session_state.page = "simulator"
        st.rerun()
with nav_3:
    if st.button("KEBIJAKAN", use_container_width=True):
        st.session_state.page = "kebijakan"
        st.rerun()

st.write("")
st.write("")

# Fungsi Load Dataset
@st.cache_data
def load_data():
    paths = ["global_deforestation_2000_2025 (2).csv", "/content/drive/MyDrive/Tugas Week 12/global_deforestation_2000_2025.csv", "global_deforestation_2000_2025.csv"]
    def region(c):
        m = {
            "brazil": "Amerika Selatan", "colombia": "Amerika Selatan", "peru": "Amerika Selatan",
            "indonesia": "Asia Tenggara", "malaysia": "Asia Tenggara", "thailand": "Asia Tenggara",
            "india": "Asia", "china": "Asia", "canada": "Amerika Utara", "usa": "Amerika Utara",
            "congo": "Afrika", "nigeria": "Afrika", "russia": "Eropa & Asia", "australia": "Oseania"
        }
        return m.get(str(c).lower(), "Lainnya")

    for p in paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            if "Region" not in df.columns: df["Region"] = df["Country"].apply(region)
            return df

    np.random.seed(42)
    countries = ["Brazil", "Indonesia", "Canada", "Russia", "USA", "Congo", "Australia", "India"]
    rows = []
    for c in countries:
        bf = np.random.uniform(100000, 600000)
        bc = np.random.uniform(8e9, 4.5e10)
        for y in range(2000, 2026):
            d = np.random.uniform(0.3, 3.0)
            a = np.random.uniform(0.1, 2.0)
            fa = bf * (1 - 0.01 * (y - 2000) * (d - a * 0.4))
            rows.append({
                "Country": c, "Year": y, "Forest_Area_km2": max(fa, 5000), "Land_Area_km2": bf * np.random.uniform(1.3, 2.2),
                "Forest_Cover_Pct": (fa / (bf * np.random.uniform(1.3, 2.2))) * 100,
                "Annual_Deforestation_Rate": d, "Annual_Afforestation_Rate": a,
                "Total_Carbon_Stock_Tonnes": max(bc * (fa / bf) * np.random.uniform(0.97, 1.03), 1e8),
                "Primary_Driver_of_Change": np.random.choice(["Agriculture", "Logging", "Fire", "Mining"]),
                "Region": region(c),
            })
    return pd.DataFrame(rows)

# Fungsi Prediksi Karbon ML
@st.cache_resource
def load_ml_model():
    paths = ["model_xgboost.pkl", "/content/drive/MyDrive/Tugas Week 12/model_xgboost.pkl"]
    for p in paths:
        if os.path.exists(p):
            try: return joblib.load(p)
            except: pass
    return None

ml_model = load_ml_model()

def predict_carbon(f: dict) -> float:
    if ml_model is not None:
        try:
            df_pred = pd.DataFrame([f])
            return float(ml_model.predict(df_pred)[0])
        except: pass
    log_f = np.log1p(max(f.get("Forest_Area_km2", 1000), 1.0))
    ratio = f.get("Forest_Area_km2", 1000) / (f.get("Land_Area_km2", 1000) + 1e-6)
    val = (4.2 + 0.94 * log_f + 0.08 * ratio - 0.04 * f.get("Annual_Deforestation_Rate", 0) + 0.025 * f.get("Annual_Afforestation_Rate", 0))
    return max(np.expm1(val), 0)

# Persiapan Data Global
df = load_data()
COUNTRIES = sorted([str(x) for x in df["Country"].dropna().unique()])
DRIVERS = sorted([str(x) for x in df["Primary_Driver_of_Change"].dropna().unique()])
REGIONS = sorted([str(x) for x in df["Region"].dropna().unique()])
YEAR_MIN = int(df["Year"].min()) if not df["Year"].isnull().all() else 2000
YEAR_MAX = int(df["Year"].max()) if not df["Year"].isnull().all() else 2025

if st.session_state.applied_year is None: st.session_state.applied_year = (YEAR_MIN, YEAR_MAX)

# Styling Chart Plotly — palette hijau ketat
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Press Start 2P", color="#064E3B", size=9),
    margin=dict(l=10, r=10, t=30, b=10),
)
AX_STYLE = dict(
    showgrid=True, gridcolor="#DCFCE7", gridwidth=2,
    linecolor="#064E3B", linewidth=3,
    tickfont=dict(family="Press Start 2P", color="#064E3B", size=7),
    zeroline=True, zerolinecolor="#064E3B", zerolinewidth=3,
)
MAP_SCALE = [[0.0, "#DCFCE7"], [1.0, "#166534"]]

def get_filtered_data():
    y_min, y_max = st.session_state.applied_year
    if not st.session_state.filters_applied:
        return df, df[(df["Year"] >= y_min) & (df["Year"] <= y_max)]

    dff = df.copy()
    if st.session_state.applied_region: dff = dff[dff["Region"].astype(str).isin(st.session_state.applied_region)]
    if st.session_state.applied_country: dff = dff[dff["Country"].astype(str).isin(st.session_state.applied_country)]
    if st.session_state.applied_driver: dff = dff[dff["Primary_Driver_of_Change"].astype(str).isin(st.session_state.applied_driver)]
    df_yr = dff[(dff["Year"] >= y_min) & (dff["Year"] <= y_max)]
    return dff, df_yr

page = st.session_state.page

# ==================== HALAMAN 1: DASHBOARD ====================
if page == "dashboard":
    with st.container(border=True):
        st.markdown("<div class='title-text'>DASHBOARD KARBON</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Pantau ketersediaan area hutan dan cadangan karbon di seluruh dunia.</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='header-text'>Filter Data Pilihan</div>", unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1: sel_region = st.multiselect("KAWASAN", REGIONS, default=[])
        with f2: sel_country = st.multiselect("NEGARA", COUNTRIES, default=[])
        with f3: sel_driver = st.multiselect("PENYEBAB", DRIVERS, default=[])

        st.write("")
        sel_year = st.slider("RENTANG TAHUN", min_value=YEAR_MIN, max_value=YEAR_MAX, value=st.session_state.applied_year)
        st.write("")

        if st.button("TERAPKAN VISUALISASI", use_container_width=True):
            st.session_state.applied_region = sel_region
            st.session_state.applied_country = sel_country
            st.session_state.applied_driver = sel_driver
            st.session_state.applied_year = sel_year
            st.session_state.filters_applied = True
            st.rerun()

    df_f, df_yr = get_filtered_data()

    if not df_yr.empty:
        df_agg = df_yr.groupby("Country", as_index=False).mean(numeric_only=True)
        total_c = df_agg["Total_Carbon_Stock_Tonnes"].sum() / 1e12
        total_f = df_agg["Forest_Area_km2"].sum() / 1e6
        avg_d = df_agg["Annual_Deforestation_Rate"].mean()
        avg_a = df_agg["Annual_Afforestation_Rate"].mean()
    else:
        df_agg = pd.DataFrame()
        total_c = total_f = avg_d = avg_a = 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("TOT KARBON", f"{total_c:.2f} Tt")
    k2.metric("LUAS HUTAN", f"{total_f:.2f} Jt")
    k3.metric("RATA HILANG", f"{avg_d:.2f}%")
    k4.metric("RATA TUMBUH", f"{avg_a:.2f}%")

    st.write("")

    with st.container(border=True):
        st.markdown("<div class='header-text'>Peta Intensitas Karbon</div>", unsafe_allow_html=True)
        if not df_agg.empty:
            fig_map = px.choropleth(
                df_agg, locations="Country", locationmode="country names",
                color="Total_Carbon_Stock_Tonnes", color_continuous_scale=MAP_SCALE
            )
            fig_map.update_layout(
                **CHART_LAYOUT,
                geo=dict(
                    showframe=True, framecolor="#064E3B", framewidth=3, showcoastlines=True, coastlinecolor="#064E3B",
                    bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#FFFFFF", showocean=True, oceancolor="#BBF7D0"
                ), coloraxis_showscale=False
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.markdown("Data kosong.")

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("<div class='header-text'>Faktor Hutan Hilang</div>", unsafe_allow_html=True)
            if not df_f.empty:
                drv = df_f.groupby("Primary_Driver_of_Change").size().reset_index(name="n")
                fig_drv = go.Figure(go.Bar(
                    x=drv["n"], y=drv["Primary_Driver_of_Change"], orientation="h",
                    marker=dict(color="#4ADE80", line=dict(color="#064E3B", width=4))
                ))
                fig_drv.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
                st.plotly_chart(fig_drv, use_container_width=True)
            else:
                st.markdown("Data kosong.")

    with col_b:
        with st.container(border=True):
            st.markdown("<div class='header-text'>Top Karbon</div>", unsafe_allow_html=True)
            if not df_agg.empty:
                top = df_agg.nlargest(5, "Total_Carbon_Stock_Tonnes")
                fig_top = go.Figure(go.Bar(
                    x=top["Total_Carbon_Stock_Tonnes"] / 1e9, y=top["Country"], orientation="h",
                    marker=dict(color="#22C55E", line=dict(color="#064E3B", width=4))
                ))
                fig_top.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.markdown("Data kosong.")

# ==================== HALAMAN 2: SIMULATOR ====================
elif page == "simulator":
    with st.container(border=True):
        st.markdown("<div class='title-text'>SIMULATOR MASA DEPAN</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Atur konfigurasi untuk memprediksi sisa karbon di masa depan.</div>", unsafe_allow_html=True)

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        negara = c1.selectbox("NEGARA", COUNTRIES)
        thn_target = c2.slider("TAHUN", 2026, 2050, 2035)
        pemicu = c3.selectbox("PENYEBAB", DRIVERS)

        base_data = df[df["Country"] == negara]
        def_land = float(base_data["Land_Area_km2"].values[0]) if not base_data.empty else 400000.0
        def_forest = float(base_data[base_data["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) if not base_data.empty else 250000.0
        def_d = float(base_data["Annual_Deforestation_Rate"].mean()) if not base_data.empty else 1.2
        def_a = float(base_data["Annual_Afforestation_Rate"].mean()) if not base_data.empty else 0.5

        st.write("")
        st.write("---")
        st.write("")

        if st.button("BUKA / TUTUP ADVANCED", use_container_width=True):
            st.session_state.adv_open = not st.session_state.adv_open
            st.session_state.sim_run = False

        if st.session_state.adv_open:
            st.write("")
            s1, s2 = st.columns(2)
            laju_d = s1.slider("KECEPATAN HILANG (%)", 0.0, 5.0, def_d, 0.1)
            laju_a = s2.slider("KECEPATAN TUMBUH (%)", 0.0, 5.0, def_a, 0.1)

            st.write("")
            a1, a2 = st.columns(2)
            luas_h_input = a1.number_input("LUAS HUTAN AWAL", min_value=0.0, value=def_forest, step=1000.0)
            luas_l_input = a2.number_input("LUAS DARATAN", min_value=0.0, value=def_land, step=1000.0)
        else:
            laju_d, laju_a = def_d, def_a
            luas_h_input, luas_l_input = def_forest, def_land

        st.write("")
        if st.button("JALANKAN SIMULASI", use_container_width=True):
            st.session_state.sim_run = True

    if st.session_state.sim_run:
        hasil_list, thn_list = [], []

        for y in range(YEAR_MAX, thn_target + 1):
            fa = luas_h_input * (1 + (laju_a - laju_d) / 100) ** (y - YEAR_MAX)
            hasil = predict_carbon({
                "Country": negara, "Primary_Driver_of_Change": pemicu, "Year": y,
                "Forest_Area_km2": max(fa, 1000), "Land_Area_km2": luas_l_input,
                "Forest_Cover_Pct": (max(fa, 1000) / luas_l_input) * 100 if luas_l_input > 0 else 0,
                "Annual_Deforestation_Rate": laju_d, "Annual_Afforestation_Rate": laju_a
            })
            hasil_list.append(hasil)
            thn_list.append(y)

        start_carbon = hasil_list[0]
        end_carbon = hasil_list[-1]
        diff_carbon = end_carbon - start_carbon
        persentase_perubahan = (diff_carbon / start_carbon) * 100 if start_carbon > 0 else 0

        with st.container(border=True):
            st.markdown("<div class='header-text'>Prediksi Karbon Visual</div>", unsafe_allow_html=True)
            fig_line = go.Figure(go.Scatter(
                x=thn_list, y=hasil_list, mode="lines+markers",
                line=dict(color="#064E3B", width=4),
                marker=dict(size=12, color="#FFFFFF", line=dict(color="#064E3B", width=4))
            ))
            fig_line.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
            st.plotly_chart(fig_line, use_container_width=True)

            if persentase_perubahan > 0:
                insight_msg = f"TREN POSITIF: Hutan tumbuh {laju_a:.2f}%, hilang {laju_d:.2f}%. Stok karbon {negara} naik {persentase_perubahan:.2f}%. Tahun {thn_target} capai {end_carbon:,.0f} Ton."
            elif persentase_perubahan < 0:
                insight_msg = f"KRISIS MENURUN: Hutan hilang {laju_d:.2f}% vs tumbuh {laju_a:.2f}%. Karbon {negara} susut {abs(persentase_perubahan):.2f}%. Tersisa {end_carbon:,.0f} Ton pada {thn_target}."
            else:
                insight_msg = f"STAGNAN: Kondisi stabil. Karbon bertahan di {end_carbon:,.0f} Ton hingga {thn_target}."

            st.markdown(f"<div class='insight-text'>{insight_msg}</div>", unsafe_allow_html=True)

# ==================== HALAMAN 3: KEBIJAKAN ====================
else:
    with st.container(border=True):
        st.markdown("<div class='title-text'>SIMULATOR KEBIJAKAN</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Coba terapkan kebijakan berbasis riset global dan lihat dampaknya di 2030.</div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        with st.container(border=True):
            st.markdown("<div class='header-text'>Panel Kebijakan</div>", unsafe_allow_html=True)
            negara_kebijakan = st.selectbox("PILIH NEGARA", COUNTRIES)

            st.write("")
            p1 = st.toggle("STOP TEBANG KOMERSIAL")
            p2 = st.toggle("TAMBAH DANA REBOISASI")
            p3 = st.toggle("HUKUM TEGAS BAKAR")
            p4 = st.toggle("INSENTIF PETANI (PES)")

            st.write("")
            if st.button("TERAPKAN ATURAN", use_container_width=True):
                st.session_state.pol_run = True

    with col_r:
        if st.session_state.pol_run:

            base_data_pol = df[df["Country"] == negara_kebijakan]
            pol_land = float(base_data_pol["Land_Area_km2"].values[0]) if not base_data_pol.empty else 600000.0
            pol_forest = float(base_data_pol[base_data_pol["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) if not base_data_pol.empty else 400000.0

            bd = float(base_data_pol["Annual_Deforestation_Rate"].mean()) if not base_data_pol.empty else 2.0
            ba = float(base_data_pol["Annual_Afforestation_Rate"].mean()) if not base_data_pol.empty else 0.5

            kebijakan_diterapkan = []

            # --- LOGIKA KEBIJAKAN BERDASARKAN RISET & STUDI KASUS GLOBAL ---

            if p1:
                # P1. Stop Tebang Komersial (Moratorium)
                # Referensi: Kebijakan Moratorium Hutan Indonesia & Soy Moratorium Brazil.
                # Riset WRI (World Resources Institute) & CIFOR menunjukkan kebijakan moratorium efektif
                # menurunkan angka deforestasi sekitar 30% - 40%. Di sini kita asumsikan penurunan 35% (pengali 0.65).
                bd *= 0.65
                kebijakan_diterapkan.append("[WRI/CIFOR] Moratorium menurunkan laju tebang hingga 35%.")

            if p2:
                # P2. Tambah Dana Reboisasi (REDD+ / Bonn Challenge)
                # Referensi: Program REDD+ PBB dan "Grain for Green" di Tiongkok.
                # Insentif pendanaan berskala nasional terbukti bisa meningkatkan laju aforestasi (hutan tumbuh)
                # secara signifikan. Kita gunakan pengali 1.5 (peningkatan 50% dari rata-rata).
                ba *= 1.5
                kebijakan_diterapkan.append("[REDD+] Injeksi dana mem-boost laju aforestasi sebesar 50%.")

            if p3:
                # P3. Hukum Tegas Bakar Hutan
                # Referensi: Evaluasi kebijakan pencegahan karhutla pasca-2015 di Asia Tenggara (Studi Bank Dunia).
                # Penegakan hukum dan patroli mampu menekan deforestasi akibat api sekitar 25% (pengali 0.75).
                bd *= 0.75
                kebijakan_diterapkan.append("[Bank Dunia] Hukum karhutla memangkas hilangnya hutan sebesar 25%.")

            if p4:
                # P4. Insentif Petani (Payment for Environmental Services / PES)
                # Referensi: Studi kasus program PES di Kosta Rika (FAO).
                # Memberikan insentif finansial pada petani untuk menjaga pohon (agroforestri) dapat
                # menekan deforestasi ~15% (pengali 0.85) dan menaikkan tutupan pohon ~20% (pengali 1.2).
                ba *= 1.2; bd *= 0.85
                kebijakan_diterapkan.append("[FAO-PES] Insentif petani menaikkan tumbuh hutan 20% & menekan hilangnya 15%.")

            h_pol = predict_carbon({
                "Country": negara_kebijakan, "Primary_Driver_of_Change": "None", "Year": 2030,
                "Forest_Area_km2": pol_forest, "Land_Area_km2": pol_land,
                "Forest_Cover_Pct": (pol_forest / pol_land) * 100 if pol_land > 0 else 0,
                "Annual_Deforestation_Rate": bd, "Annual_Afforestation_Rate": ba
            })

            with st.container(border=True):
                st.markdown(f"<div class='header-text'>Proyeksi {negara_kebijakan} (2030)</div>", unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("HUTAN HILANG", f"{bd:.2f}%")
                m2.metric("HUTAN TUMBUH", f"{ba:.2f}%")
                st.write("")
                st.metric("ESTIMASI KARBON", f"{h_pol:,.0f} Ton")

                if not kebijakan_diterapkan:
                    penjelasan = "Tidak ada aturan. Lingkungan bergerak sesuai standar historis saat ini."
                else:
                    penjelasan = f"DAMPAK KEBIJAKAN TERUKUR:<br><br> • {'<br> • '.join(kebijakan_diterapkan)}"

                st.markdown(f"<div class='insight-text'>{penjelasan}</div>", unsafe_allow_html=True)
