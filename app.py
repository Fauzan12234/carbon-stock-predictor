import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import joblib
import io

# ─── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="Global Carbon Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── SESSION STATE ────────────────────────────────────────────
_def = {
    "page": "dashboard",
    "filters_applied": False,
    "applied_region": [],
    "applied_country": [],
    "applied_driver": [],
    "applied_year": None,
    "adv_open": False,
    "sim_run": False,
    "pol_run": False,
    "sim_results": None,
}
for _k, _v in _def.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─── CSS — PIXEL ART GREEN THEME ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

/* ── GLOBAL ─── */
* {
    font-family: 'Press Start 2P', cursive !important;
    color: #064E3B !important;
    box-sizing: border-box !important;
}
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

.block-container {
    padding: 3rem 3.5rem 8rem !important;
    max-width: 1280px !important;
    background-color: transparent !important;
}

/* ── CONTAINER CARDS ─── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    box-shadow: 6px 6px 0px #22C55E !important;
    padding: 2rem !important;
    margin-bottom: 2.25rem !important;
}

/* ── BUTTONS ─── */
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

/* ── DOWNLOAD BUTTON ─── */
[data-testid="stDownloadButton"] > button {
    background-color: #064E3B !important;
    color: #FFFFFF !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    box-shadow: 4px 4px 0px #4ADE80 !important;
    font-family: 'Press Start 2P', cursive !important;
    font-size: 0.65rem !important;
    padding: 0.75rem 1rem !important;
    line-height: 1.6 !important;
    transition: none !important;
    cursor: pointer !important;
    width: 100% !important;
}
[data-testid="stDownloadButton"] > button:hover {
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0px #4ADE80 !important;
}
[data-testid="stDownloadButton"] > button span,
[data-testid="stDownloadButton"] > button p {
    color: #FFFFFF !important;
}

/* ── METRICS ─── */
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
    font-size: 0.55rem !important;
    color: #064E3B !important;
    line-height: 1.7 !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 1.0rem !important;
    color: #064E3B !important;
}
[data-testid="stMetricDelta"] { display: none !important; }

/* ── FORM LABELS ─── */
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

/* ── SELECT / DROPDOWN ─── */
div[data-baseweb="select"] { background-color: #FFFFFF !important; }
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
div[data-baseweb="select"] svg,
div[data-baseweb="select"] [class*="indicatorContainer"] svg {
    fill: #064E3B !important;
    color: #064E3B !important;
}

/* ── DROPDOWN MENU ─── */
[data-baseweb="popover"] {
    background-color: #FFFFFF !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    box-shadow: 6px 6px 0px #22C55E !important;
    overflow: hidden !important;
}
[data-baseweb="popover"] > div,
[data-baseweb="popover"] > div > div { background-color: #FFFFFF !important; }
ul[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: none !important;
    padding: 4px !important;
    margin: 0 !important;
}
li[data-baseweb="option"], [role="option"] {
    background-color: #FFFFFF !important;
    color: #064E3B !important;
    font-family: 'Press Start 2P', cursive !important;
    font-size: 0.58rem !important;
    padding: 0.75rem 0.9rem !important;
    cursor: pointer !important;
    border-bottom: 2px solid #F0FDF4 !important;
    line-height: 1.6 !important;
}
li[data-baseweb="option"]:last-child, [role="option"]:last-child { border-bottom: none !important; }
li[data-baseweb="option"]:hover, [role="option"]:hover { background-color: #DCFCE7 !important; }
li[data-baseweb="option"][aria-selected="true"], [role="option"][aria-selected="true"] {
    background-color: #BBF7D0 !important;
    color: #064E3B !important;
}

/* ── MULTISELECT TAGS ─── */
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
span[data-baseweb="tag"] button, span[data-baseweb="tag"] [role="presentation"] {
    background: transparent !important; border: none !important; box-shadow: none !important; cursor: pointer !important;
}
span[data-baseweb="tag"] svg, span[data-baseweb="tag"] button svg {
    fill: #064E3B !important; color: #064E3B !important;
}

/* ── NUMBER INPUT ─── */
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
[data-testid="stNumberInputContainer"] button {
    background-color: #DCFCE7 !important;
    border: none !important;
    border-left: 3px solid #064E3B !important;
    color: #064E3B !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    padding: 0.3rem 0.6rem !important;
}
[data-testid="stNumberInputContainer"] button:hover { background-color: #4ADE80 !important; }
[data-testid="stNumberInputContainer"] button svg { fill: #064E3B !important; color: #064E3B !important; }

/* ── SLIDER ─── */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"],
.stSlider p {
    font-size: 0.55rem !important;
    color: #064E3B !important;
    font-family: 'Press Start 2P', cursive !important;
}
.stSlider > div > div > div > div { background-color: #DCFCE7 !important; }
.stSlider > div > div > div > div > div[role="slider"],
[data-testid="stSlider"] [role="slider"] {
    background-color: #064E3B !important;
    border: 3px solid #064E3B !important;
    box-shadow: 3px 3px 0px #22C55E !important;
    width: 20px !important;
    height: 20px !important;
}
.stSlider > div > div > div > div:nth-child(2) { background-color: #4ADE80 !important; }

/* ── TOGGLE ─── */
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

/* ── DIVIDER ─── */
hr {
    border: none !important;
    border-top: 3px solid #DCFCE7 !important;
    margin: 1.75rem 0 !important;
}

/* ── COLUMN SPACING ─── */
[data-testid="stColumns"] > [data-testid="column"] {
    padding-left: 0.6rem !important;
    padding-right: 0.6rem !important;
}
[data-testid="stColumns"] > [data-testid="column"]:first-child { padding-left: 0 !important; }
[data-testid="stColumns"] > [data-testid="column"]:last-child { padding-right: 0 !important; }

/* ── CUSTOM TEXT ─── */
.title-text {
    font-size: 1.2rem !important;
    margin-bottom: 0.75rem !important;
    color: #064E3B !important;
    text-transform: uppercase;
    line-height: 1.7;
    letter-spacing: 0.03rem;
}
.sub-text {
    font-size: 0.62rem !important;
    margin-bottom: 0.5rem !important;
    color: #166534 !important;
    line-height: 2;
}
.header-text {
    font-size: 0.82rem !important;
    margin-bottom: 1.25rem !important;
    color: #064E3B !important;
    padding-bottom: 0.65rem !important;
    border-bottom: 3px solid #DCFCE7 !important;
    display: block !important;
    line-height: 1.5 !important;
}
.insight-text {
    font-size: 0.65rem !important;
    line-height: 2.2 !important;
    color: #064E3B !important;
    background-color: #DCFCE7 !important;
    padding: 1.5rem 1.75rem !important;
    border: 4px dashed #064E3B !important;
    border-radius: 0 !important;
    margin-top: 1.5rem !important;
}
.badge-pos {
    display:inline-block;
    background-color:#4ADE80 !important;
    border:3px solid #064E3B !important;
    padding:0.3rem 0.7rem !important;
    font-size:0.58rem !important;
    color:#064E3B !important;
    margin-right:0.5rem;
    box-shadow:3px 3px 0 #064E3B;
}
.badge-neg {
    display:inline-block;
    background-color:#FEF9C3 !important;
    border:3px solid #064E3B !important;
    padding:0.3rem 0.7rem !important;
    font-size:0.58rem !important;
    color:#064E3B !important;
    margin-right:0.5rem;
    box-shadow:3px 3px 0 #064E3B;
}

/* ── MARKDOWN GENERAL ─── */
.stMarkdown p, .stMarkdown span, p, span { color: #064E3B !important; }
.stMarkdown p { font-size: 0.65rem !important; line-height: 1.9 !important; }

/* ── PLOTLY — SOLID WHITE (CRITICAL FIX) ─── */
/* Ensures the outer chart wrapper has a solid white background */
.stPlotlyChart > div:first-child {
    background-color: #FFFFFF !important;
    border: 3px solid #064E3B !important;
    box-shadow: 4px 4px 0px #22C55E !important;
    padding: 6px !important;
}

/* ── PORTAL / OVERLAY ─── */
[data-baseweb="tooltip"],
[data-baseweb="layer"] { background-color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# ─── NAVIGATION ───────────────────────────────────────────────
n1, n2, n3, n4 = st.columns(4)
with n1:
    if st.button("📊 DASHBOARD", use_container_width=True):
        st.session_state.page = "dashboard"; st.rerun()
with n2:
    if st.button("🔮 SIMULATOR", use_container_width=True):
        st.session_state.page = "simulator"; st.rerun()
with n3:
    if st.button("⚖️ KEBIJAKAN", use_container_width=True):
        st.session_state.page = "kebijakan"; st.rerun()
with n4:
    if st.button("⚔️ KOMPARASI", use_container_width=True):
        st.session_state.page = "komparasi"; st.rerun()

st.write("")
st.write("")

# ─── DATA LOADING ─────────────────────────────────────────────
@st.cache_data
def load_data():
    paths = [
        "global_deforestation_2000_2025 (2).csv",
        "/content/drive/MyDrive/Tugas Week 12/global_deforestation_2000_2025.csv",
        "global_deforestation_2000_2025.csv",
    ]
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
            if "Region" not in df.columns:
                df["Region"] = df["Country"].apply(region)
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
            land = bf * np.random.uniform(1.3, 2.2)
            rows.append({
                "Country": c, "Year": y,
                "Forest_Area_km2": max(fa, 5000),
                "Land_Area_km2": land,
                "Forest_Cover_Pct": (max(fa, 5000) / land) * 100,
                "Annual_Deforestation_Rate": d,
                "Annual_Afforestation_Rate": a,
                "Total_Carbon_Stock_Tonnes": max(bc * (fa / bf) * np.random.uniform(0.97, 1.03), 1e8),
                "Primary_Driver_of_Change": np.random.choice(["Agriculture", "Logging", "Fire", "Mining"]),
                "Region": region(c),
            })
    return pd.DataFrame(rows)

@st.cache_resource
def load_ml_model():
    paths = [
        "model_xgboost.pkl",
        "/content/drive/MyDrive/Tugas Week 12/model_xgboost.pkl",
    ]
    for p in paths:
        if os.path.exists(p):
            try: return joblib.load(p)
            except: pass
    return None

ml_model = load_ml_model()

def predict_carbon(f: dict) -> float:
    if ml_model is not None:
        try:
            return float(ml_model.predict(pd.DataFrame([f]))[0])
        except: pass
    log_f = np.log1p(max(f.get("Forest_Area_km2", 1000), 1.0))
    ratio = f.get("Forest_Area_km2", 1000) / (f.get("Land_Area_km2", 1000) + 1e-6)
    val = (4.2 + 0.94 * log_f + 0.08 * ratio
           - 0.04 * f.get("Annual_Deforestation_Rate", 0)
           + 0.025 * f.get("Annual_Afforestation_Rate", 0))
    return max(np.expm1(val), 0)

# ─── DATA SETUP ───────────────────────────────────────────────
df = load_data()
COUNTRIES = sorted([str(x) for x in df["Country"].dropna().unique()])
DRIVERS   = sorted([str(x) for x in df["Primary_Driver_of_Change"].dropna().unique()])
REGIONS   = sorted([str(x) for x in df["Region"].dropna().unique()])
YEAR_MIN  = int(df["Year"].min()) if not df["Year"].isnull().all() else 2000
YEAR_MAX  = int(df["Year"].max()) if not df["Year"].isnull().all() else 2025

if st.session_state.applied_year is None:
    st.session_state.applied_year = (YEAR_MIN, YEAR_MAX)

# ─── CHART STYLE CONSTANTS ────────────────────────────────────
# paper_bgcolor & plot_bgcolor = solid #FFFFFF (no transparency)
CHART_LAYOUT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Press Start 2P", color="#064E3B", size=9),
    margin=dict(l=10, r=90, t=45, b=15),
)
AX_STYLE = dict(
    showgrid=True, gridcolor="#DCFCE7", gridwidth=2,
    linecolor="#064E3B", linewidth=3,
    tickfont=dict(family="Press Start 2P", color="#064E3B", size=7),
    zeroline=True, zerolinecolor="#064E3B", zerolinewidth=2,
    automargin=True,
)
AX_STYLE_NOTICK = dict(**AX_STYLE, showticklabels=True)
MAP_SCALE = [[0.0, "#DCFCE7"], [1.0, "#166534"]]
LEGEND_STYLE = dict(
    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
    font=dict(family="Press Start 2P", color="#064E3B", size=7),
    bgcolor="#FFFFFF", bordercolor="#064E3B", borderwidth=2,
)
C1, C2 = "#4ADE80", "#064E3B"  # Primary, Secondary colors for charts


def _txt_font(size=7):
    return dict(family="Press Start 2P", color="#064E3B", size=size)


def get_filtered_data():
    y_min, y_max = st.session_state.applied_year
    if not st.session_state.filters_applied:
        return df, df[(df["Year"] >= y_min) & (df["Year"] <= y_max)]
    dff = df.copy()
    if st.session_state.applied_region:
        dff = dff[dff["Region"].astype(str).isin(st.session_state.applied_region)]
    if st.session_state.applied_country:
        dff = dff[dff["Country"].astype(str).isin(st.session_state.applied_country)]
    if st.session_state.applied_driver:
        dff = dff[dff["Primary_Driver_of_Change"].astype(str).isin(st.session_state.applied_driver)]
    return dff, dff[(dff["Year"] >= y_min) & (dff["Year"] <= y_max)]


page = st.session_state.page

# ═══════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════
if page == "dashboard":

    with st.container(border=True):
        st.markdown("<div class='title-text'>📊 DASHBOARD KARBON GLOBAL</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Pantau ketersediaan area hutan dan cadangan karbon di seluruh dunia.</div>", unsafe_allow_html=True)

    # ── FILTER PANEL ──────────────────────────────
    with st.container(border=True):
        st.markdown("<div class='header-text'>Filter Data</div>", unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1: sel_region  = st.multiselect("KAWASAN",  REGIONS,   default=[])
        with f2: sel_country = st.multiselect("NEGARA",   COUNTRIES, default=[])
        with f3: sel_driver  = st.multiselect("PENYEBAB", DRIVERS,   default=[])
        st.write("")
        sel_year = st.slider("RENTANG TAHUN", min_value=YEAR_MIN, max_value=YEAR_MAX,
                             value=st.session_state.applied_year)
        st.write("")
        if st.button("TERAPKAN VISUALISASI", use_container_width=True):
            st.session_state.applied_region  = sel_region
            st.session_state.applied_country = sel_country
            st.session_state.applied_driver  = sel_driver
            st.session_state.applied_year    = sel_year
            st.session_state.filters_applied = True
            st.rerun()

    df_f, df_yr = get_filtered_data()

    # ── KPI METRICS ───────────────────────────────
    if not df_yr.empty:
        df_agg = df_yr.groupby("Country", as_index=False).mean(numeric_only=True)
        total_c = df_agg["Total_Carbon_Stock_Tonnes"].sum() / 1e12
        total_f = df_agg["Forest_Area_km2"].sum() / 1e6
        avg_d   = df_agg["Annual_Deforestation_Rate"].mean()
        avg_a   = df_agg["Annual_Afforestation_Rate"].mean()
    else:
        df_agg = pd.DataFrame()
        total_c = total_f = avg_d = avg_a = 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("TOTAL KARBON",    f"{total_c:.2f} Tt")
    k2.metric("LUAS HUTAN",      f"{total_f:.2f} Jt km²")
    k3.metric("RATA HILANG/THN", f"{avg_d:.2f} %")
    k4.metric("RATA TUMBUH/THN", f"{avg_a:.2f} %")
    st.write("")

    # ── MAP ───────────────────────────────────────
    with st.container(border=True):
        st.markdown("<div class='header-text'>Peta Intensitas Stok Karbon</div>", unsafe_allow_html=True)
        if not df_agg.empty:
            fig_map = px.choropleth(
                df_agg, locations="Country", locationmode="country names",
                color="Total_Carbon_Stock_Tonnes", color_continuous_scale=MAP_SCALE,
            )
            fig_map.update_layout(
                **{**CHART_LAYOUT, "margin": dict(l=0, r=0, t=10, b=0)},
                geo=dict(
                    showframe=True, framecolor="#064E3B", framewidth=3,
                    showcoastlines=True, coastlinecolor="#064E3B",
                    bgcolor="#FFFFFF",
                    showland=True, landcolor="#FFFFFF",
                    showocean=True, oceancolor="#BBF7D0",
                ),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.markdown("Data kosong.")

    # ── CHART ROW 1: DRIVERS + TOP CARBON ─────────
    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown("<div class='header-text'>Penyebab Hilangnya Hutan</div>", unsafe_allow_html=True)
            if not df_f.empty:
                drv = df_f.groupby("Primary_Driver_of_Change").size().reset_index(name="n")
                mx_drv = drv["n"].max()
                fig_drv = go.Figure(go.Bar(
                    x=drv["n"], y=drv["Primary_Driver_of_Change"], orientation="h",
                    text=[str(v) for v in drv["n"]],
                    textposition="outside",
                    textfont=_txt_font(8),
                    cliponaxis=False,
                    marker=dict(color=C1, line=dict(color=C2, width=3)),
                ))
                fig_drv.update_layout(
                    **CHART_LAYOUT,
                    xaxis={**AX_STYLE, "range": [0, mx_drv * 1.35]},
                    yaxis=AX_STYLE,
                )
                st.plotly_chart(fig_drv, use_container_width=True)
            else:
                st.markdown("Data kosong.")

    with col_b:
        with st.container(border=True):
            st.markdown("<div class='header-text'>Top 5 Stok Karbon Negara</div>", unsafe_allow_html=True)
            if not df_agg.empty:
                top = df_agg.nlargest(5, "Total_Carbon_Stock_Tonnes")
                vals = top["Total_Carbon_Stock_Tonnes"] / 1e9
                fig_top = go.Figure(go.Bar(
                    x=vals, y=top["Country"], orientation="h",
                    text=[f"{v:.1f}B" for v in vals],
                    textposition="outside",
                    textfont=_txt_font(8),
                    cliponaxis=False,
                    marker=dict(color="#22C55E", line=dict(color=C2, width=3)),
                ))
                fig_top.update_layout(
                    **CHART_LAYOUT,
                    xaxis={**AX_STYLE, "range": [0, vals.max() * 1.35]},
                    yaxis=AX_STYLE,
                )
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.markdown("Data kosong.")

    # ── CHART ROW 2: HISTORICAL TREND ─────────────
    with st.container(border=True):
        st.markdown("<div class='header-text'>Tren Historis Stok Karbon (Gigaton)</div>", unsafe_allow_html=True)
        if not df_f.empty:
            trend = (df_f.groupby("Year", as_index=False)["Total_Carbon_Stock_Tonnes"]
                     .sum()
                     .assign(Karbon_Gt=lambda x: x["Total_Carbon_Stock_Tonnes"] / 1e9))

            # Show label every 5 years
            lbl_trend = [
                f"{v:.0f}" if yr % 5 == 0 else ""
                for yr, v in zip(trend["Year"], trend["Karbon_Gt"])
            ]
            fig_trend = go.Figure(go.Scatter(
                x=trend["Year"], y=trend["Karbon_Gt"],
                mode="lines+markers+text",
                text=lbl_trend,
                textposition="top center",
                textfont=_txt_font(7),
                line=dict(color=C2, width=3),
                marker=dict(size=8, color=C1, line=dict(color=C2, width=2)),
                fill="tozeroy",
                fillcolor="rgba(74,222,128,0.12)",
            ))
            fig_trend.update_layout(
                **{**CHART_LAYOUT, "margin": dict(l=10, r=20, t=40, b=10)},
                xaxis={**AX_STYLE, "title": None},
                yaxis={**AX_STYLE, "title": "Gigaton"},
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.markdown("Data kosong.")

    # ── CHART ROW 3: DEFORESTATION VS AFFORESTATION ──
    with st.container(border=True):
        st.markdown("<div class='header-text'>Laju Hilang vs Tumbuh Per Negara (Rata-rata)</div>", unsafe_allow_html=True)
        if not df_agg.empty:
            fig_dva = go.Figure()
            fig_dva.add_trace(go.Bar(
                name="Hilang", x=df_agg["Country"], y=df_agg["Annual_Deforestation_Rate"],
                text=[f"{v:.2f}%" for v in df_agg["Annual_Deforestation_Rate"]],
                textposition="outside",
                textfont=_txt_font(7),
                cliponaxis=False,
                marker=dict(color="#FCA5A5", line=dict(color=C2, width=2)),
            ))
            fig_dva.add_trace(go.Bar(
                name="Tumbuh", x=df_agg["Country"], y=df_agg["Annual_Afforestation_Rate"],
                text=[f"{v:.2f}%" for v in df_agg["Annual_Afforestation_Rate"]],
                textposition="outside",
                textfont=_txt_font(7),
                cliponaxis=False,
                marker=dict(color=C1, line=dict(color=C2, width=2)),
            ))
            fig_dva.update_layout(
                **{**CHART_LAYOUT, "margin": dict(l=10, r=20, t=60, b=10)},
                barmode="group",
                xaxis=AX_STYLE,
                yaxis={**AX_STYLE, "range": [0, df_agg["Annual_Deforestation_Rate"].max() * 1.4]},
                legend=LEGEND_STYLE,
            )
            st.plotly_chart(fig_dva, use_container_width=True)
        else:
            st.markdown("Data kosong.")


# ═══════════════════════════════════════════════════
# PAGE 2 — SIMULATOR
# ═══════════════════════════════════════════════════
elif page == "simulator":

    with st.container(border=True):
        st.markdown("<div class='title-text'>🔮 SIMULATOR MASA DEPAN</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Atur konfigurasi untuk memprediksi sisa karbon di masa depan.</div>", unsafe_allow_html=True)

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        negara     = c1.selectbox("NEGARA",    COUNTRIES)
        thn_target = c2.slider("TAHUN TARGET", 2026, 2050, 2035)
        pemicu     = c3.selectbox("PENYEBAB",  DRIVERS)

        base_data  = df[df["Country"] == negara]
        def_land   = float(base_data["Land_Area_km2"].values[0])     if not base_data.empty else 400000.0
        def_forest = float(base_data[base_data["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) \
                     if not base_data.empty else 250000.0
        def_d      = float(base_data["Annual_Deforestation_Rate"].mean()) if not base_data.empty else 1.2
        def_a      = float(base_data["Annual_Afforestation_Rate"].mean()) if not base_data.empty else 0.5

        st.write("")
        st.write("---")
        st.write("")

        if st.button("BUKA / TUTUP ADVANCED", use_container_width=True):
            st.session_state.adv_open = not st.session_state.adv_open
            st.session_state.sim_run  = False

        if st.session_state.adv_open:
            st.write("")
            s1, s2 = st.columns(2)
            laju_d        = s1.slider("KECEPATAN HILANG (%)", 0.0, 5.0, def_d, 0.1)
            laju_a        = s2.slider("KECEPATAN TUMBUH (%)", 0.0, 5.0, def_a, 0.1)
            st.write("")
            a1, a2        = st.columns(2)
            luas_h_input  = a1.number_input("LUAS HUTAN AWAL (km²)", min_value=0.0, value=def_forest, step=1000.0)
            luas_l_input  = a2.number_input("LUAS DARATAN (km²)",   min_value=0.0, value=def_land,   step=1000.0)
        else:
            laju_d, laju_a      = def_d, def_a
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
                "Forest_Area_km2":   max(fa, 1000),
                "Land_Area_km2":     luas_l_input,
                "Forest_Cover_Pct":  (max(fa, 1000) / luas_l_input) * 100 if luas_l_input > 0 else 0,
                "Annual_Deforestation_Rate": laju_d,
                "Annual_Afforestation_Rate": laju_a,
            })
            hasil_list.append(hasil)
            thn_list.append(y)

        start_c = hasil_list[0]
        end_c   = hasil_list[-1]
        pct     = ((end_c - start_c) / start_c) * 100 if start_c > 0 else 0

        # Save results to session
        df_sim = pd.DataFrame({"Tahun": thn_list, "Prediksi_Karbon_Ton": hasil_list})
        st.session_state.sim_results = df_sim

        with st.container(border=True):
            st.markdown("<div class='header-text'>Prediksi Karbon Visual</div>", unsafe_allow_html=True)

            # Labels only for key points
            n_pts   = len(hasil_list)
            labels  = [""] * n_pts
            labels[0]  = f"{hasil_list[0]:,.0f}"
            labels[-1] = f"{hasil_list[-1]:,.0f}"
            idx_min, idx_max = int(np.argmin(hasil_list)), int(np.argmax(hasil_list))
            if labels[idx_min] == "": labels[idx_min] = f"{hasil_list[idx_min]:,.0f}"
            if labels[idx_max] == "": labels[idx_max] = f"{hasil_list[idx_max]:,.0f}"

            fig_line = go.Figure(go.Scatter(
                x=thn_list, y=hasil_list,
                mode="lines+markers+text",
                text=labels,
                textposition="top center",
                textfont=_txt_font(7),
                line=dict(color=C2, width=4),
                marker=dict(size=10, color=C1, line=dict(color=C2, width=3)),
            ))
            fig_line.update_layout(
                **{**CHART_LAYOUT, "margin": dict(l=10, r=20, t=50, b=10)},
                xaxis=AX_STYLE,
                yaxis={**AX_STYLE, "title": "Ton Karbon"},
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # Insight box
            if pct > 0:
                msg = (f"TREN POSITIF: Hutan tumbuh {laju_a:.2f}%, hilang {laju_d:.2f}%. "
                       f"Karbon {negara} naik {pct:.2f}%. Capai {end_c:,.0f} Ton di {thn_target}.")
            elif pct < 0:
                msg = (f"KRISIS: Hutan hilang {laju_d:.2f}% vs tumbuh {laju_a:.2f}%. "
                       f"Karbon {negara} susut {abs(pct):.2f}%. Tersisa {end_c:,.0f} Ton di {thn_target}.")
            else:
                msg = f"STAGNAN: Kondisi stabil di {end_c:,.0f} Ton hingga {thn_target}."
            st.markdown(f"<div class='insight-text'>{msg}</div>", unsafe_allow_html=True)

        # ── HASIL TABLE & DOWNLOAD ─────────────────
        with st.container(border=True):
            st.markdown("<div class='header-text'>Tabel Hasil Prediksi</div>", unsafe_allow_html=True)

            df_display = df_sim.copy()
            df_display.columns = ["Tahun", "Prediksi Karbon (Ton)"]
            df_display["Prediksi Karbon (Ton)"] = df_display["Prediksi Karbon (Ton)"].map("{:,.0f}".format)
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            st.write("")
            d1, d2 = st.columns(2)
            with d1:
                csv_bytes = df_sim.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ UNDUH HASIL — CSV",
                    data=csv_bytes,
                    file_name=f"simulasi_{negara}_{thn_target}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with d2:
                # Summary TXT download
                summary = (
                    f"=== RINGKASAN SIMULASI ===\n"
                    f"Negara     : {negara}\n"
                    f"Tahun Akhir: {thn_target}\n"
                    f"Penyebab   : {pemicu}\n"
                    f"Laju Hilang: {laju_d:.2f}%\n"
                    f"Laju Tumbuh: {laju_a:.2f}%\n"
                    f"Karbon Awal: {start_c:,.0f} Ton\n"
                    f"Karbon Akhir: {end_c:,.0f} Ton\n"
                    f"Perubahan  : {pct:.2f}%\n"
                )
                st.download_button(
                    label="⬇️ UNDUH RINGKASAN — TXT",
                    data=summary.encode("utf-8"),
                    file_name=f"ringkasan_{negara}_{thn_target}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )


# ═══════════════════════════════════════════════════
# PAGE 3 — KEBIJAKAN
# ═══════════════════════════════════════════════════
elif page == "kebijakan":

    with st.container(border=True):
        st.markdown("<div class='title-text'>⚖️ SIMULATOR KEBIJAKAN</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Terapkan kebijakan berbasis riset global dan lihat dampaknya di 2030.</div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        with st.container(border=True):
            st.markdown("<div class='header-text'>Panel Kebijakan</div>", unsafe_allow_html=True)
            negara_kebijakan = st.selectbox("PILIH NEGARA", COUNTRIES)
            st.write("")
            p1 = st.toggle("STOP TEBANG KOMERSIAL")
            p2 = st.toggle("TAMBAH DANA REBOISASI")
            p3 = st.toggle("HUKUM TEGAS BAKAR HUTAN")
            p4 = st.toggle("INSENTIF PETANI (PES)")
            st.write("")
            if st.button("TERAPKAN ATURAN", use_container_width=True):
                st.session_state.pol_run = True

    with col_r:
        if st.session_state.pol_run:
            base_pol   = df[df["Country"] == negara_kebijakan]
            pol_land   = float(base_pol["Land_Area_km2"].values[0])   if not base_pol.empty else 600000.0
            pol_forest = float(base_pol[base_pol["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) \
                         if not base_pol.empty else 400000.0
            bd_base = bd = float(base_pol["Annual_Deforestation_Rate"].mean()) if not base_pol.empty else 2.0
            ba_base = ba = float(base_pol["Annual_Afforestation_Rate"].mean()) if not base_pol.empty else 0.5

            kebijakan_list = []
            if p1:
                bd *= 0.65
                kebijakan_list.append("[WRI/CIFOR] Moratorium → laju tebang turun 35%.")
            if p2:
                ba *= 1.5
                kebijakan_list.append("[REDD+] Dana reboisasi → aforestasi naik 50%.")
            if p3:
                bd *= 0.75
                kebijakan_list.append("[Bank Dunia] Hukum karhutla → hilang hutan turun 25%.")
            if p4:
                ba *= 1.2; bd *= 0.85
                kebijakan_list.append("[FAO-PES] Insentif petani → tumbuh +20%, hilang -15%.")

            h_pol = predict_carbon({
                "Country": negara_kebijakan, "Primary_Driver_of_Change": "None", "Year": 2030,
                "Forest_Area_km2": pol_forest, "Land_Area_km2": pol_land,
                "Forest_Cover_Pct": (pol_forest / pol_land) * 100 if pol_land > 0 else 0,
                "Annual_Deforestation_Rate": bd,
                "Annual_Afforestation_Rate": ba,
            })
            h_base = predict_carbon({
                "Country": negara_kebijakan, "Primary_Driver_of_Change": "None", "Year": 2030,
                "Forest_Area_km2": pol_forest, "Land_Area_km2": pol_land,
                "Forest_Cover_Pct": (pol_forest / pol_land) * 100 if pol_land > 0 else 0,
                "Annual_Deforestation_Rate": bd_base,
                "Annual_Afforestation_Rate": ba_base,
            })

            with st.container(border=True):
                st.markdown(f"<div class='header-text'>Proyeksi {negara_kebijakan} (2030)</div>", unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("LAJU HILANG",  f"{bd:.2f} %")
                m2.metric("LAJU TUMBUH",  f"{ba:.2f} %")
                st.write("")
                st.metric("ESTIMASI KARBON 2030", f"{h_pol:,.0f} Ton")

                if not kebijakan_list:
                    penjelasan = "Tidak ada aturan. Lingkungan bergerak sesuai historis."
                else:
                    penjelasan = "DAMPAK KEBIJAKAN TERUKUR:<br><br> • " + "<br> • ".join(kebijakan_list)
                st.markdown(f"<div class='insight-text'>{penjelasan}</div>", unsafe_allow_html=True)

            # ── BEFORE / AFTER CHART ──────────────────
            with st.container(border=True):
                st.markdown("<div class='header-text'>Perbandingan Sebelum vs Sesudah Kebijakan</div>", unsafe_allow_html=True)

                cats  = ["Laju Deforestasi (%)", "Laju Aforestasi (%)", "Karbon (x1B Ton)"]
                v_bef = [bd_base, ba_base, h_base / 1e9]
                v_aft = [bd,      ba,      h_pol  / 1e9]

                fig_ba = go.Figure()
                fig_ba.add_trace(go.Bar(
                    name="SEBELUM", x=cats, y=v_bef,
                    text=[f"{v:.2f}" for v in v_bef],
                    textposition="outside", textfont=_txt_font(7),
                    cliponaxis=False,
                    marker=dict(color="#BBF7D0", line=dict(color=C2, width=3)),
                ))
                fig_ba.add_trace(go.Bar(
                    name="SESUDAH", x=cats, y=v_aft,
                    text=[f"{v:.2f}" for v in v_aft],
                    textposition="outside", textfont=_txt_font(7),
                    cliponaxis=False,
                    marker=dict(color=C1, line=dict(color=C2, width=3)),
                ))
                fig_ba.update_layout(
                    **{**CHART_LAYOUT, "margin": dict(l=10, r=20, t=60, b=10)},
                    barmode="group",
                    xaxis=AX_STYLE,
                    yaxis={**AX_STYLE, "range": [0, max(max(v_bef), max(v_aft)) * 1.4]},
                    legend=LEGEND_STYLE,
                )
                st.plotly_chart(fig_ba, use_container_width=True)

                # Download before/after CSV
                df_ba = pd.DataFrame({"Metrik": cats, "Sebelum": v_bef, "Sesudah": v_aft})
                st.download_button(
                    "⬇️ UNDUH HASIL KEBIJAKAN — CSV",
                    data=df_ba.to_csv(index=False).encode("utf-8"),
                    file_name=f"kebijakan_{negara_kebijakan}_2030.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


# ═══════════════════════════════════════════════════
# PAGE 4 — KOMPARASI (NEW)
# ═══════════════════════════════════════════════════
elif page == "komparasi":

    with st.container(border=True):
        st.markdown("<div class='title-text'>⚔️ KOMPARASI 2 NEGARA</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Bandingkan dua negara secara langsung: karbon, hutan, dan tren historis.</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='header-text'>Pilih Dua Negara</div>", unsafe_allow_html=True)
        cx1, cx2 = st.columns(2)
        neg1 = cx1.selectbox("NEGARA 1", COUNTRIES, index=0)
        neg2 = cx2.selectbox("NEGARA 2", COUNTRIES, index=min(1, len(COUNTRIES) - 1))

    if neg1 == neg2:
        st.markdown("<div class='insight-text'>⚠ Pilih dua negara yang berbeda untuk komparasi.</div>", unsafe_allow_html=True)
        st.stop()

    d1_all = df[df["Country"] == neg1]
    d2_all = df[df["Country"] == neg2]
    d1_avg = d1_all.mean(numeric_only=True)
    d2_avg = d2_all.mean(numeric_only=True)

    # ── KPI SIDE BY SIDE ──────────────────────────
    with st.container(border=True):
        st.markdown("<div class='header-text'>Ringkasan Metrik (Rata-rata Historis)</div>", unsafe_allow_html=True)

        lbl1  = neg1[:8].upper()
        lbl2  = neg2[:8].upper()
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric(f"{lbl1}\nKARBON",    f"{d1_avg['Total_Carbon_Stock_Tonnes']/1e9:.1f}B Ton")
        m2.metric(f"{lbl1}\nHUTAN",     f"{d1_avg['Forest_Area_km2']/1e3:.0f}k km²")
        m3.metric(f"{lbl1}\nDEFOR",     f"{d1_avg['Annual_Deforestation_Rate']:.2f}%")
        m4.metric(f"{lbl2}\nKARBON",    f"{d2_avg['Total_Carbon_Stock_Tonnes']/1e9:.1f}B Ton")
        m5.metric(f"{lbl2}\nHUTAN",     f"{d2_avg['Forest_Area_km2']/1e3:.0f}k km²")
        m6.metric(f"{lbl2}\nDEFOR",     f"{d2_avg['Annual_Deforestation_Rate']:.2f}%")

    # ── GROUPED BAR — NORMALIZED COMPARISON ───────
    with st.container(border=True):
        st.markdown("<div class='header-text'>Perbandingan Multi-Metrik (Ternormalisasi 0-100)</div>", unsafe_allow_html=True)

        comp_metrics = {
            "Stok Karbon":      ("Total_Carbon_Stock_Tonnes", 1e9),
            "Luas Hutan":       ("Forest_Area_km2",           1e3),
            "Tutupan Hutan (%)":("Forest_Cover_Pct",          1),
            "Laju Tumbuh":      ("Annual_Afforestation_Rate", 1),
        }
        labels_comp, vals1_n, vals2_n = [], [], []
        for lbl, (col, scale) in comp_metrics.items():
            v1 = float(d1_avg.get(col, 0)) / scale
            v2 = float(d2_avg.get(col, 0)) / scale
            mx = max(v1, v2, 1e-9)
            labels_comp.append(lbl)
            vals1_n.append(round(v1 / mx * 100, 1))
            vals2_n.append(round(v2 / mx * 100, 1))

        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Bar(
            name=neg1, x=labels_comp, y=vals1_n,
            text=[f"{v}%" for v in vals1_n],
            textposition="outside", textfont=_txt_font(7),
            cliponaxis=False,
            marker=dict(color=C1, line=dict(color=C2, width=3)),
        ))
        fig_cmp.add_trace(go.Bar(
            name=neg2, x=labels_comp, y=vals2_n,
            text=[f"{v}%" for v in vals2_n],
            textposition="outside", textfont=_txt_font(7),
            cliponaxis=False,
            marker=dict(color="#166534", line=dict(color=C2, width=3)),
        ))
        fig_cmp.update_layout(
            **{**CHART_LAYOUT, "margin": dict(l=10, r=20, t=60, b=10)},
            barmode="group",
            xaxis=AX_STYLE,
            yaxis={**AX_STYLE, "range": [0, 130]},
            legend=LEGEND_STYLE,
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

    # ── LINE: CARBON TREND ────────────────────────
    with st.container(border=True):
        st.markdown("<div class='header-text'>Tren Stok Karbon (2000—2025)</div>", unsafe_allow_html=True)

        t1 = d1_all.groupby("Year")["Total_Carbon_Stock_Tonnes"].mean().reset_index()
        t2 = d2_all.groupby("Year")["Total_Carbon_Stock_Tonnes"].mean().reset_index()

        # Labels for first/last only
        def edge_labels(series, years):
            lbl = [""] * len(series)
            lbl[0]  = f"{series.iloc[0]/1e9:.1f}B"
            lbl[-1] = f"{series.iloc[-1]/1e9:.1f}B"
            return lbl

        fig_ct = go.Figure()
        fig_ct.add_trace(go.Scatter(
            x=t1["Year"], y=t1["Total_Carbon_Stock_Tonnes"] / 1e9,
            mode="lines+markers+text",
            name=neg1,
            text=edge_labels(t1["Total_Carbon_Stock_Tonnes"], t1["Year"]),
            textposition="top center", textfont=_txt_font(7),
            line=dict(color=C2, width=3),
            marker=dict(size=7, color=C1, line=dict(color=C2, width=2)),
        ))
        fig_ct.add_trace(go.Scatter(
            x=t2["Year"], y=t2["Total_Carbon_Stock_Tonnes"] / 1e9,
            mode="lines+markers+text",
            name=neg2,
            text=edge_labels(t2["Total_Carbon_Stock_Tonnes"], t2["Year"]),
            textposition="top center", textfont=_txt_font(7),
            line=dict(color="#166534", width=3, dash="dash"),
            marker=dict(size=7, color="#22C55E", line=dict(color=C2, width=2)),
        ))
        fig_ct.update_layout(
            **{**CHART_LAYOUT, "margin": dict(l=10, r=20, t=60, b=10)},
            xaxis=AX_STYLE,
            yaxis={**AX_STYLE, "title": "Gigaton"},
            legend=LEGEND_STYLE,
        )
        st.plotly_chart(fig_ct, use_container_width=True)

    # ── LINE: DEFORESTATION RATE TREND ────────────
    with st.container(border=True):
        st.markdown("<div class='header-text'>Tren Laju Deforestasi (2000—2025)</div>", unsafe_allow_html=True)

        dr1 = d1_all.groupby("Year")["Annual_Deforestation_Rate"].mean().reset_index()
        dr2 = d2_all.groupby("Year")["Annual_Deforestation_Rate"].mean().reset_index()

        fig_dr = go.Figure()
        fig_dr.add_trace(go.Scatter(
            x=dr1["Year"], y=dr1["Annual_Deforestation_Rate"],
            mode="lines+markers", name=neg1,
            line=dict(color=C2, width=3),
            marker=dict(size=7, color=C1, line=dict(color=C2, width=2)),
            fill="tozeroy", fillcolor="rgba(74,222,128,0.12)",
        ))
        fig_dr.add_trace(go.Scatter(
            x=dr2["Year"], y=dr2["Annual_Deforestation_Rate"],
            mode="lines+markers", name=neg2,
            line=dict(color="#166534", width=3, dash="dash"),
            marker=dict(size=7, color="#22C55E", line=dict(color=C2, width=2)),
            fill="tozeroy", fillcolor="rgba(22,101,52,0.08)",
        ))
        fig_dr.update_layout(
            **{**CHART_LAYOUT, "margin": dict(l=10, r=20, t=60, b=10)},
            xaxis=AX_STYLE,
            yaxis={**AX_STYLE, "title": "Deforestasi (%)"},
            legend=LEGEND_STYLE,
        )
        st.plotly_chart(fig_dr, use_container_width=True)

    # ── SCATTER: FOREST AREA vs CARBON ────────────
    with st.container(border=True):
        st.markdown("<div class='header-text'>Luas Hutan vs Stok Karbon (Scatter)</div>", unsafe_allow_html=True)

        both = pd.concat([
            d1_all.assign(Negara=neg1),
            d2_all.assign(Negara=neg2),
        ])
        fig_sc = px.scatter(
            both,
            x="Forest_Area_km2", y="Total_Carbon_Stock_Tonnes",
            color="Negara",
            color_discrete_map={neg1: C1, neg2: "#166534"},
            size="Forest_Cover_Pct",
            hover_data=["Year"],
        )
        fig_sc.update_traces(
            marker=dict(line=dict(color=C2, width=2)),
        )
        fig_sc.update_layout(
            **{**CHART_LAYOUT, "margin": dict(l=10, r=20, t=60, b=10)},
            xaxis={**AX_STYLE, "title": "Luas Hutan (km²)"},
            yaxis={**AX_STYLE, "title": "Karbon (Ton)"},
            legend={**LEGEND_STYLE, "title": None},
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    # ── DOWNLOAD COMPARISON CSV ────────────────────
    with st.container(border=True):
        st.markdown("<div class='header-text'>Ekspor Data Komparasi</div>", unsafe_allow_html=True)

        df_exp = pd.DataFrame({
            "Metrik": ["Stok Karbon Rata (Ton)", "Luas Hutan Rata (km²)",
                       "Tutupan Hutan Rata (%)", "Laju Deforestasi Rata (%)",
                       "Laju Aforestasi Rata (%)"],
            neg1: [
                f"{d1_avg['Total_Carbon_Stock_Tonnes']:,.0f}",
                f"{d1_avg['Forest_Area_km2']:,.0f}",
                f"{d1_avg['Forest_Cover_Pct']:.2f}",
                f"{d1_avg['Annual_Deforestation_Rate']:.2f}",
                f"{d1_avg['Annual_Afforestation_Rate']:.2f}",
            ],
            neg2: [
                f"{d2_avg['Total_Carbon_Stock_Tonnes']:,.0f}",
                f"{d2_avg['Forest_Area_km2']:,.0f}",
                f"{d2_avg['Forest_Cover_Pct']:.2f}",
                f"{d2_avg['Annual_Deforestation_Rate']:.2f}",
                f"{d2_avg['Annual_Afforestation_Rate']:.2f}",
            ],
        })
        st.dataframe(df_exp, use_container_width=True, hide_index=True)
        st.write("")
        st.download_button(
            label=f"⬇️ UNDUH KOMPARASI {neg1} vs {neg2} — CSV",
            data=df_exp.to_csv(index=False).encode("utf-8"),
            file_name=f"komparasi_{neg1}_{neg2}.csv",
            mime="text/csv",
            use_container_width=True,
        )
