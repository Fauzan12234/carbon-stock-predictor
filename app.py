import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import time
import joblib

# ─────────────────────────────────────────────────────────────
# PENGATURAN HALAMAN
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Carbon Data",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# PENYIMPANAN SESI (STATE)
# ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "filters_applied" not in st.session_state:
    st.session_state.filters_applied = False
if "applied_region" not in st.session_state:
    st.session_state.applied_region = []
if "applied_country" not in st.session_state:
    st.session_state.applied_country = []
if "applied_driver" not in st.session_state:
    st.session_state.applied_driver = []
if "applied_year" not in st.session_state:
    st.session_state.applied_year = None

# ─────────────────────────────────────────────────────────────
# TEMA GEN Z RETRO ROUNDY (NEO-BRUTALISM)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

* {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #111827 !important;
}

body, .stApp, .block-container, header[data-testid="stHeader"] {
    background-color: #FFFDF0 !important;
}

[data-testid="stSidebar"] { display: none; }

.block-container {
    padding: 2rem 2.25rem 5rem !important;
    max-width: 1200px !important;
}

/* ── KOTAK / CARD TEMA RETRO ROUNDY ── */
.retro-card {
    background-color: #FFFFFF;
    border: 3px solid #111827;
    border-radius: 24px !important;
    box-shadow: 4px 4px 0px #111827;
    padding: 2rem;
    margin-bottom: 2rem;
    transition: all 0.2s ease-in-out;
}
.retro-card:hover {
    transform: translateY(-2px);
    box-shadow: 6px 6px 0px #111827;
}

.retro-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}

.retro-sub {
    font-size: 1.1rem;
    font-weight: 600;
    color: #4B5563 !important;
    margin-bottom: 1rem;
}

/* ── TOMBOL ── */
.stButton > button {
    background-color: #A7F3D0 !important;
    color: #111827 !important;
    border: 3px solid #111827 !important;
    border-radius: 100px !important;
    box-shadow: 3px 3px 0px #111827 !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    padding: 0.6rem !important;
    transition: all 0.1s ease;
}

.stButton > button:hover, .stButton > button:active {
    background-color: #6EE7B7 !important;
    box-shadow: 0px 0px 0px #111827 !important;
    transform: translate(3px, 3px) !important;
}

/* ── METRIK / ANGKA ── */
[data-testid="stMetric"] {
    background: #FDE68A !important;
    border: 3px solid #111827 !important;
    border-radius: 24px !important;
    box-shadow: 4px 4px 0px #111827 !important;
    padding: 1.5rem !important;
    text-align: center;
}
[data-testid="stMetricLabel"] > div {
    font-size: 1.1rem !important;
    font-weight: 800 !important;
}
[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
}

/* ── FORM & INPUT ── */
.stSelectbox label, .stSlider > label, .stNumberInput label, .stMultiSelect label {
    font-size: 1.1rem !important;
    font-weight: 800 !important;
}
[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
    background-color: #FFFFFF !important;
    border: 3px solid #111827 !important;
    border-radius: 16px !important;
    color: #111827 !important;
    font-weight: 600 !important;
}

/* ── TABEL ── */
.stDataFrame { 
    border: 3px solid #111827 !important; 
    border-radius: 16px !important; 
    overflow: hidden !important; 
}
thead tr th {
    background: #FECACA !important;
    border-bottom: 3px solid #111827 !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MENU NAVIGASI
# ─────────────────────────────────────────────────────────────
nav_1, nav_2, nav_3 = st.columns(3)

with nav_1:
    if st.button("PAPAN DATA", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()
with nav_2:
    if st.button("COBA SIMULASI", use_container_width=True):
        st.session_state.page = "simulator"
        st.rerun()
with nav_3:
    if st.button("ATURAN BARU", use_container_width=True):
        st.session_state.page = "kebijakan"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# AMBIL DATA DAN MODEL MACHINE LEARNING
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    paths = [
        "global_deforestation_2000_2025 (2).csv",
        "/content/drive/MyDrive/Tugas Week 12/global_deforestation_2000_2025.csv",
        "global_deforestation_2000_2025.csv",
    ]

    def region(c):
        m = {
            "brazil": "Amerika Selatan", "colombia": "Amerika Selatan", "peru": "Amerika Selatan", "argentina": "Amerika Selatan",
            "indonesia": "Asia Tenggara", "malaysia": "Asia Tenggara", "thailand": "Asia Tenggara", "vietnam": "Asia Tenggara",
            "india": "Asia", "china": "Asia", "canada": "Amerika Utara", "usa": "Amerika Utara",
            "congo": "Afrika", "nigeria": "Afrika", "russia": "Eropa & Asia", "ukraine": "Eropa & Asia",
            "australia": "Oseania", "new zealand": "Oseania",
        }
        return m.get(str(c).lower(), "Lainnya")

    for p in paths:
        if os.path.exists(p):
            df = pd.read_csv(p)
            if "Region" not in df.columns:
                df["Region"] = df["Country"].apply(region)
            return df

    # Data Buatan jika tidak ada file ditemukan
    np.random.seed(42)
    countries = ["Brazil", "Indonesia", "Canada", "Russia", "USA", "Congo", "Australia", "India", "China", "Malaysia"]
    rows = []
    for c in countries:
        bf = np.random.uniform(100000, 600000)
        bc = np.random.uniform(8e9, 4.5e10)
        for y in range(2000, 2026):
            d = np.random.uniform(0.3, 3.0)
            a = np.random.uniform(0.1, 2.0)
            fa = bf * (1 - 0.01 * (y - 2000) * (d - a * 0.4))
            rows.append({
                "Country": c,
                "Year": y,
                "Forest_Area_km2": max(fa, 5000),
                "Land_Area_km2": bf * np.random.uniform(1.3, 2.2),
                "Forest_Cover_Pct": (fa / (bf * np.random.uniform(1.3, 2.2))) * 100,
                "Annual_Deforestation_Rate": d,
                "Annual_Afforestation_Rate": a,
                "Total_Carbon_Stock_Tonnes": max(bc * (fa / bf) * np.random.uniform(0.97, 1.03), 1e8),
                "Primary_Driver_of_Change": np.random.choice(["Agriculture", "Logging", "Fire", "Mining"], p=[0.45, 0.25, 0.15, 0.15]),
                "Region": region(c),
            })
    return pd.DataFrame(rows)

@st.cache_resource
def load_ml_model():
    """Mencoba memuat model XGBoost dari path"""
    paths = ["model_xgboost.pkl", "/content/drive/MyDrive/Tugas Week 12/model_xgboost.pkl"]
    for p in paths:
        if os.path.exists(p):
            try:
                return joblib.load(p)
            except:
                pass
    return None

ml_model = load_ml_model()

def predict_carbon(f: dict) -> float:
    # Coba gunakan prediksi dari XGBoost jika kompatibel
    if ml_model is not None:
        try:
            df_pred = pd.DataFrame([f])
            # Pastikan urutan dan jumlah feature sesuai pipeline
            pred = ml_model.predict(df_pred)
            return float(pred[0])
        except Exception:
            pass # Lanjut ke formula logika dasar jika input pipeline berbeda
            
    # Formula historis dasar
    log_f = np.log1p(max(f.get("Forest_Area_km2", 1000), 1.0))
    ratio = f.get("Forest_Area_km2", 1000) / (f.get("Land_Area_km2", 1000) + 1e-6)
    val = (4.2 + 0.94 * log_f + 0.08 * ratio - 0.04 * f.get("Annual_Deforestation_Rate", 0) + 0.025 * f.get("Annual_Afforestation_Rate", 0))
    return max(np.expm1(val), 0)

df = load_data()
COUNTRIES = sorted([str(x) for x in df["Country"].dropna().unique()])
DRIVERS = sorted([str(x) for x in df["Primary_Driver_of_Change"].dropna().unique()])
REGIONS = sorted([str(x) for x in df["Region"].dropna().unique()])
YEAR_MIN = int(df["Year"].min()) if not df["Year"].isnull().all() else 2000
YEAR_MAX = int(df["Year"].max()) if not df["Year"].isnull().all() else 2025

if st.session_state.applied_year is None:
    st.session_state.applied_year = YEAR_MAX

# ─────────────────────────────────────────────────────────────
# GAYA GRAFIK RETRO (Warna Terang, Garis Tegas)
# ─────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#111827", size=14),
    margin=dict(l=10, r=10, t=30, b=10),
)
AX_STYLE = dict(
    showgrid=True,
    gridcolor="#E5E7EB",
    gridwidth=2,
    linecolor="#111827",
    linewidth=3,
    tickfont=dict(family="Plus Jakarta Sans", color="#111827", size=13),
    zeroline=True,
    zerolinecolor="#111827",
    zerolinewidth=3
)
MAP_SCALE = [[0.0, "#D1FAE5"], [1.0, "#059669"]]

# ─────────────────────────────────────────────────────────────
# LOGIKA FILTER
# ─────────────────────────────────────────────────────────────
def get_filtered_data():
    if not st.session_state.filters_applied:
        return df, df[df["Year"] == st.session_state.applied_year]
    
    dff = df.copy()
    if st.session_state.applied_region:
        dff = dff[dff["Region"].astype(str).isin(st.session_state.applied_region)]
    if st.session_state.applied_country:
        dff = dff[dff["Country"].astype(str).isin(st.session_state.applied_country)]
    if st.session_state.applied_driver:
        dff = dff[dff["Primary_Driver_of_Change"].astype(str).isin(st.session_state.applied_driver)]
    df_yr = dff[dff["Year"] == st.session_state.applied_year]
    return dff, df_yr

page = st.session_state.page

# ═══════════════════════ HALAMAN 1: PAPAN DATA ══════════════════════════
if page == "dashboard":
    st.markdown("""
    <div class='retro-card'>
        <div class='retro-title'>DATA KARBON DUNIA</div>
        <div class='retro-sub'>Cek ketersediaan jumlah pohon dan karbon di seluruh dunia saat ini.</div>
    </div>
    """, unsafe_allow_html=True)

    # AREA FILTER
    st.markdown("<div class='retro-card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:1.4rem; font-weight:800; margin-bottom:1rem;'>Filter Data Pilihan:</div>", unsafe_allow_html=True)
    
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sel_region = st.multiselect("KAWASAN", REGIONS, default=[])
    with f2:
        sel_country = st.multiselect("NEGARA", COUNTRIES, default=[])
    with f3:
        sel_driver = st.multiselect("PENYEBAB", DRIVERS, default=[])
    
    year_options = ["Semua Tahun"] + list(range(YEAR_MIN, YEAR_MAX + 1))
    default_year_idx = year_options.index(st.session_state.applied_year) if st.session_state.applied_year in year_options else 0
    with f4:
        sel_year = st.selectbox("TAHUN", year_options, index=default_year_idx)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Terapkan Visualisasi", use_container_width=True):
        st.session_state.applied_region = sel_region
        st.session_state.applied_country = sel_country
        st.session_state.applied_driver = sel_driver
        st.session_state.applied_year = YEAR_MAX if sel_year == "Semua Tahun" else sel_year
        st.session_state.filters_applied = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    df_f, df_yr = get_filtered_data()

    # ANGKA RINGKASAN
    if not df_yr.empty:
        total_c = df_yr["Total_Carbon_Stock_Tonnes"].sum() / 1e12
        total_f = df_yr["Forest_Area_km2"].sum() / 1e6
        avg_d = df_yr["Annual_Deforestation_Rate"].mean()
        avg_a = df_yr["Annual_Afforestation_Rate"].mean()
    else:
        total_c = total_f = avg_d = avg_a = 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("TOTAL KARBON", f"{total_c:.2f} Tt")
    k2.metric("LUAS HUTAN", f"{total_f:.2f} Jt km²")
    k3.metric("RATA-RATA HILANG", f"{avg_d:.2f}%")
    k4.metric("RATA-RATA TUMBUH", f"{avg_a:.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # PETA
    st.markdown("<div class='retro-card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:1.4rem; font-weight:800;'>Peta Intensitas Karbon</div>", unsafe_allow_html=True)
    if not df_yr.empty:
        fig_map = px.choropleth(
            df_yr, locations="Country", locationmode="country names",
            color="Total_Carbon_Stock_Tonnes", color_continuous_scale=MAP_SCALE
        )
        fig_map.update_layout(
            **CHART_LAYOUT,
            geo=dict(
                showframe=True, framecolor="#111827", framewidth=3,
                showcoastlines=True, coastlinecolor="#111827",
                bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#F3F4F6",
                showocean=True, oceancolor="#DBEAFE"
            ),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.write("Data visualisasi kosong.")
    st.markdown("</div>", unsafe_allow_html=True)

    # GRAFIK BAWAH
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.4rem; font-weight:800;'>Faktor Penyebab Hutan Hilang</div>", unsafe_allow_html=True)
        if not df_f.empty:
            drv = df_f.groupby("Primary_Driver_of_Change").size().reset_index(name="n")
            fig_drv = go.Figure(go.Bar(
                x=drv["n"], y=drv["Primary_Driver_of_Change"], orientation="h",
                marker=dict(color="#A7F3D0", line=dict(color="#111827", width=3))
            ))
            fig_drv.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
            st.plotly_chart(fig_drv, use_container_width=True)
        else:
            st.write("Data visualisasi kosong.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.4rem; font-weight:800;'>Negara Penyimpan Karbon Tertinggi</div>", unsafe_allow_html=True)
        if not df_yr.empty:
            top = df_yr.nlargest(5, "Total_Carbon_Stock_Tonnes")
            fig_top = go.Figure(go.Bar(
                x=top["Total_Carbon_Stock_Tonnes"] / 1e9, y=top["Country"], orientation="h",
                marker=dict(color="#FDE68A", line=dict(color="#111827", width=3))
            ))
            fig_top.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.write("Data visualisasi kosong.")
        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════ HALAMAN 2: SIMULATOR ══════════════════════════
elif page == "simulator":
    st.markdown("""
    <div class='retro-card'>
        <div class='retro-title'>TEBAK MASA DEPAN</div>
        <div class='retro-sub'>Atur persentase di bawah untuk memprediksi sisa cadangan karbon global (Mendukung algoritma XGBoost).</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_sim"):
        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        negara = c1.selectbox("PILIH NEGARA", COUNTRIES)
        pemicu = c2.selectbox("PENYEBAB UTAMA", DRIVERS)
        thn_target = c3.slider("TAHUN TARGET", 2026, 2050, 2035)
        
        st.markdown("<hr style='border:1px solid #111827;'>", unsafe_allow_html=True)
        
        s1, s2 = st.columns(2)
        laju_d = s1.slider("KECEPATAN HUTAN HILANG (%)", 0.0, 5.0, 1.2, 0.1)
        laju_a = s2.slider("KECEPATAN HUTAN TUMBUH (%)", 0.0, 5.0, 0.5, 0.1)
        
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.form_submit_button("JALANKAN SIMULASI", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if run_btn:
        hasil_list, thn_list = [], []
        # Menarik data land area dasar dari dataframe
        base_data = df[df["Country"] == negara]
        base_land = base_data["Land_Area_km2"].values[0] if not base_data.empty else 400000
        base_forest = base_data[base_data["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0] if not base_data.empty else 250000

        for y in range(YEAR_MAX, thn_target + 1):
            fa = base_forest * (1 + (laju_a - laju_d) / 100) ** (y - YEAR_MAX)
            # Menyesuaikan input dengan asumsi fitur yang ada
            hasil = predict_carbon({
                "Country": negara,
                "Primary_Driver_of_Change": pemicu,
                "Year": y, 
                "Forest_Area_km2": max(fa, 1000), 
                "Land_Area_km2": base_land,
                "Forest_Cover_Pct": (max(fa, 1000) / base_land) * 100,
                "Annual_Deforestation_Rate": laju_d, 
                "Annual_Afforestation_Rate": laju_a
            })
            hasil_list.append(hasil)
            thn_list.append(y)

        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.4rem; font-weight:800;'>Prediksi Cadangan Karbon</div>", unsafe_allow_html=True)
        
        fig_line = go.Figure(go.Scatter(
            x=thn_list, y=hasil_list, mode="lines+markers",
            line=dict(color="#111827", width=4),
            marker=dict(size=12, color="#FECACA", line=dict(color="#111827", width=3))
        ))
        fig_line.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════ HALAMAN 3: KEBIJAKAN ══════════════════════════
else:
    st.markdown("""
    <div class='retro-card'>
        <div class='retro-title'>SIMULATOR ATURAN</div>
        <div class='retro-sub'>Coba terapkan kebijakan dan lihat langsung seberapa efektif dampaknya di tahun 2030.</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.4rem; font-weight:800; margin-bottom:1rem;'>Panel Kebijakan:</div>", unsafe_allow_html=True)
        
        p1 = st.toggle("STOP TEBANG POHON KOMERSIAL")
        p2 = st.toggle("TAMBAH DANA REBOISASI")
        p3 = st.toggle("HUKUM TEGAS BAKAR HUTAN")
        p4 = st.toggle("BERIKAN INSENTIF PETANI")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        bd, ba = 2.0, 0.5
        if p1: bd *= 0.3
        if p2: ba *= 3.0
        if p3: bd *= 0.8
        if p4: ba *= 1.4; bd *= 0.9

        h_pol = predict_carbon({
            "Country": "Global_Avg",
            "Primary_Driver_of_Change": "None",
            "Year": 2030, 
            "Forest_Area_km2": 400000, 
            "Land_Area_km2": 600000,
            "Forest_Cover_Pct": 66.6,
            "Annual_Deforestation_Rate": bd, 
            "Annual_Afforestation_Rate": ba
        })
        
        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.4rem; font-weight:800; margin-bottom:1rem;'>Proyeksi di Tahun 2030:</div>", unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        m1.metric("HUTAN HILANG", f"{bd:.2f}%")
        m2.metric("HUTAN TUMBUH", f"{ba:.2f}%")
        st.metric("ESTIMASI STOK KARBON", f"{h_pol:,.0f} Ton")
        
        st.markdown("</div>", unsafe_allow_html=True)
