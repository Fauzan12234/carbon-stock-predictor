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
if "compare_mode" not in st.session_state: st.session_state.compare_mode = False

# ============================================================
# CSS — PIXEL ART DARK THEME (SOLID BACKGROUNDS & WHITE TEXT)
# Latar belakang gelap pekat, teks putih, aksen hijau
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

/* ── GLOBAL RESET ─────────────────────────────────────────── */
* {
    font-family: 'Press Start 2P', cursive !important;
    color: #FFFFFF !important;
    box-sizing: border-box !important;
}

/* ── APP BACKGROUND — GELAP PEKAT ─────────────────────────── */
html, body {
    background-color: #121212 !important;
    background-image: none !important;
}
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background-color: #121212 !important;
    background-image: none !important;
}
[data-testid="stHeader"] {
    background-color: #121212 !important;
    border-bottom: 3px solid #22C55E !important;
    box-shadow: none !important;
}
[data-testid="stBottomBlockContainer"],
[data-testid="stStatusWidget"],
footer {
    background-color: #121212 !important;
}
[data-testid="stSidebar"] { display: none !important; }

/* Block container — Spacing diperlebar agar tidak nabrak */
.block-container {
    padding: 3rem 4rem 8rem !important;
    max-width: 1300px !important;
    background-color: #121212 !important;
}

/* ── KARTU CONTAINER (SOLID DARK) ────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #1E1E1E !important;
    border: 4px solid #22C55E !important;
    border-radius: 0px !important;
    box-shadow: 6px 6px 0px #064E3B !important;
    padding: 2.5rem 2rem !important;
    margin-bottom: 2.5rem !important;
}

/* ── TOMBOL ────────────────────────────────────────────────── */
.stButton > button, .stDownloadButton > button {
    background-color: #22C55E !important;
    color: #FFFFFF !important;
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    box-shadow: 4px 4px 0px #064E3B !important;
    font-size: 0.7rem !important;
    padding: 0.8rem 1rem !important;
    line-height: 1.6 !important;
    transition: none !important;
    cursor: pointer !important;
    width: 100% !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0px #064E3B !important;
    background-color: #4ADE80 !important;
    color: #121212 !important;
}

/* ── METRIK (SOLID BOX) ────────────────────────────────────── */
[data-testid="stMetric"] {
    background-color: #2D2D2D !important;
    border: 4px solid #22C55E !important;
    border-radius: 0px !important;
    padding: 1.5rem 1rem !important;
    text-align: center !important;
    box-shadow: 4px 4px 0px #064E3B !important;
    margin-bottom: 1rem !important;
}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] p {
    font-size: 0.6rem !important;
    color: #4ADE80 !important;
    line-height: 1.7 !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 1.2rem !important;
    color: #FFFFFF !important;
}
[data-testid="stMetricDelta"] { display: none !important; }

/* ── LABEL FORM ────────────────────────────────────────────── */
[data-testid="stWidgetLabel"] p,
.stSelectbox label,
.stMultiSelect label,
.stSlider > label,
.stNumberInput label,
.stTextInput label {
    font-size: 0.7rem !important;
    color: #FFFFFF !important;
    margin-bottom: 0.6rem !important;
    display: block !important;
    line-height: 1.7 !important;
}

/* ── INPUT FIELDS (SELECT/TEXT/NUMBER) ─────────────────────── */
div[data-baseweb="select"], div[data-baseweb="base-input"] {
    background-color: #121212 !important;
}
div[data-baseweb="select"] > div:first-child, div[data-baseweb="base-input"] > input {
    background-color: #121212 !important;
    border: 3px solid #22C55E !important;
    border-radius: 0px !important;
    color: #FFFFFF !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] input {
    color: #FFFFFF !important;
    font-size: 0.65rem !important;
}
div[data-baseweb="popover"] > div {
    background-color: #1E1E1E !important;
    border: 3px solid #22C55E !important;
}
li[data-baseweb="option"] {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
    font-size: 0.65rem !important;
}
li[data-baseweb="option"]:hover {
    background-color: #2D2D2D !important;
}

/* ── MULTISELECT TAGS ──────────────────────────────────────── */
span[data-baseweb="tag"] {
    background-color: #2D2D2D !important;
    border: 2px solid #22C55E !important;
}
span[data-baseweb="tag"] span {
    color: #FFFFFF !important;
}

/* ── PLOTLY CHART (NO TRANSPARENCY) ────────────────────────── */
.js-plotly-plot, .plotly, .stPlotlyChart {
    background-color: #1E1E1E !important;
}

/* ── COLUMNS SPACING ───────────────────────────────────────── */
[data-testid="stColumns"] {
    gap: 1.5rem !important;
}

/* ── TEKS CUSTOM ───────────────────────────────────────────── */
.title-text {
    font-size: 1.5rem !important;
    margin-bottom: 1rem !important;
    color: #4ADE80 !important;
    text-transform: uppercase;
    line-height: 1.8;
}
.sub-text {
    font-size: 0.75rem !important;
    margin-bottom: 0.5rem !important;
    color: #FFFFFF !important;
    line-height: 2;
}
.header-text {
    font-size: 1rem !important;
    margin-bottom: 1.5rem !important;
    color: #4ADE80 !important;
    padding-bottom: 0.75rem !important;
    border-bottom: 3px solid #2D2D2D !important;
    display: block !important;
}
.insight-text {
    font-size: 0.75rem !important;
    line-height: 2.1 !important;
    color: #FFFFFF !important;
    background-color: #2D2D2D !important;
    padding: 1.5rem !important;
    border: 3px dashed #22C55E !important;
    margin-top: 1.5rem !important;
}

</style>
""", unsafe_allow_html=True)

# Navigasi Menu
nav_1, nav_2, nav_3 = st.columns(3)
with nav_1:
    if st.button("DASHBOARD"):
        st.session_state.page = "dashboard"
        st.rerun()
with nav_2:
    if st.button("SIMULATOR"):
        st.session_state.page = "simulator"
        st.rerun()
with nav_3:
    if st.button("KEBIJAKAN"):
        st.session_state.page = "kebijakan"
        st.rerun()

st.write("")

# Fungsi Load Dataset
@st.cache_data
def load_data():
    paths = ["global_deforestation_2000_2025 (2).csv", "global_deforestation_2000_2025.csv"]
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

@st.cache_resource
def load_ml_model():
    paths = ["model_xgboost.pkl"]
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

# Styling Chart Plotly — Background Solid Gelap & Teks Putih
CHART_LAYOUT = dict(
    paper_bgcolor="#1E1E1E", plot_bgcolor="#1E1E1E",
    font=dict(family="Press Start 2P", color="#FFFFFF", size=10),
    margin=dict(l=20, r=20, t=40, b=20),
)
AX_STYLE = dict(
    showgrid=True, gridcolor="#2D2D2D", gridwidth=1,
    linecolor="#4ADE80", linewidth=2,
    tickfont=dict(family="Press Start 2P", color="#FFFFFF", size=8),
    zeroline=True, zerolinecolor="#4ADE80", zerolinewidth=2,
)
MAP_SCALE = [[0.0, "#2D2D2D"], [1.0, "#4ADE80"]]

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
        st.markdown("<div class='title-text'>DASHBOARD KARBON GLOBAL</div>", unsafe_allow_html=True)
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
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("TERAPKAN VISUALISASI"):
                st.session_state.applied_region = sel_region
                st.session_state.applied_country = sel_country
                st.session_state.applied_driver = sel_driver
                st.session_state.applied_year = sel_year
                st.session_state.filters_applied = True
                st.rerun()
        
        df_f, df_yr = get_filtered_data()
        csv_data = df_yr.to_csv(index=False).encode('utf-8')
        with btn2:
            st.download_button(
                label="DOWNLOAD DATA (CSV)",
                data=csv_data,
                file_name="filtered_carbon_data.csv",
                mime="text/csv",
                use_container_width=True
            )

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
    k1.metric("TOT KARBON", f"{total_c:.2f} TeraTon")
    k2.metric("LUAS HUTAN", f"{total_f:.2f} Juta KM²")
    k3.metric("RATA HILANG", f"{avg_d:.2f}%")
    k4.metric("RATA TUMBUH", f"{avg_a:.2f}%")

    with st.container(border=True):
        st.markdown("<div class='header-text'>Peta Intensitas Karbon (Solid Background)</div>", unsafe_allow_html=True)
        if not df_agg.empty:
            fig_map = px.choropleth(
                df_agg, locations="Country", locationmode="country names",
                color="Total_Carbon_Stock_Tonnes", color_continuous_scale=MAP_SCALE
            )
            fig_map.update_layout(
                **CHART_LAYOUT,
                geo=dict(
                    showframe=True, framecolor="#22C55E", framewidth=2, 
                    showcoastlines=True, coastlinecolor="#4ADE80",
                    bgcolor="#1E1E1E", showland=True, landcolor="#2D2D2D", 
                    showocean=True, oceancolor="#121212"
                ), coloraxis_showscale=True
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
                    text=drv["n"], textposition="auto", textfont=dict(color="#121212", size=12),
                    marker=dict(color="#4ADE80", line=dict(color="#22C55E", width=2))
                ))
                fig_drv.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
                st.plotly_chart(fig_drv, use_container_width=True)
            else:
                st.markdown("Data kosong.")

    with col_b:
        with st.container(border=True):
            st.markdown("<div class='header-text'>Top 5 Stok Karbon</div>", unsafe_allow_html=True)
            if not df_agg.empty:
                top = df_agg.nlargest(5, "Total_Carbon_Stock_Tonnes")
                top["Val_Billion"] = top["Total_Carbon_Stock_Tonnes"] / 1e9
                text_labels = [f"{v:.1f} Milyar" for v in top["Val_Billion"]]
                fig_top = go.Figure(go.Bar(
                    x=top["Val_Billion"], y=top["Country"], orientation="h",
                    text=text_labels, textposition="auto", textfont=dict(color="#121212", size=10),
                    marker=dict(color="#22C55E", line=dict(color="#4ADE80", width=2))
                ))
                fig_top.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.markdown("Data kosong.")

# ==================== HALAMAN 2: SIMULATOR ====================
elif page == "simulator":
    with st.container(border=True):
        st.markdown("<div class='title-text'>SIMULATOR MASA DEPAN</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Atur konfigurasi dan bandingkan prediksi sisa karbon di masa depan.</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.session_state.compare_mode = st.toggle("MODE KOMPARASI (Bandingkan 2 Negara)", value=st.session_state.compare_mode)
        
        c1, c2, c3 = st.columns(3)
        negara1 = c1.selectbox("NEGARA UTAMA", COUNTRIES, index=0)
        
        if st.session_state.compare_mode:
            negara2 = c2.selectbox("NEGARA PEMBANDING", COUNTRIES, index=1 if len(COUNTRIES)>1 else 0)
            thn_target = c3.slider("TAHUN TARGET", 2026, 2050, 2035)
        else:
            negara2 = None
            thn_target = c2.slider("TAHUN TARGET", 2026, 2050, 2035)
            pemicu = c3.selectbox("PENYEBAB UTAMA", DRIVERS)

        # Base Data Negara 1
        b1 = df[df["Country"] == negara1]
        def_land1 = float(b1["Land_Area_km2"].values[0]) if not b1.empty else 400000.0
        def_forest1 = float(b1[b1["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) if not b1.empty else 250000.0
        def_d1 = float(b1["Annual_Deforestation_Rate"].mean()) if not b1.empty else 1.2
        def_a1 = float(b1["Annual_Afforestation_Rate"].mean()) if not b1.empty else 0.5
        
        # Base Data Negara 2 (Jika Komparasi)
        if st.session_state.compare_mode:
            b2 = df[df["Country"] == negara2]
            def_land2 = float(b2["Land_Area_km2"].values[0]) if not b2.empty else 400000.0
            def_forest2 = float(b2[b2["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) if not b2.empty else 250000.0
            def_d2 = float(b2["Annual_Deforestation_Rate"].mean()) if not b2.empty else 1.2
            def_a2 = float(b2["Annual_Afforestation_Rate"].mean()) if not b2.empty else 0.5

        st.write("")
        if st.button("JALANKAN SIMULASI"):
            st.session_state.sim_run = True

    if st.session_state.sim_run:
        hasil_list1, thn_list = [], []
        hasil_list2 = []

        for y in range(YEAR_MAX, thn_target + 1):
            thn_list.append(y)
            # Prediksi Negara 1
            fa1 = def_forest1 * (1 + (def_a1 - def_d1) / 100) ** (y - YEAR_MAX)
            hasil1 = predict_carbon({
                "Country": negara1, "Primary_Driver_of_Change": "Mixed", "Year": y,
                "Forest_Area_km2": max(fa1, 1000), "Land_Area_km2": def_land1,
                "Forest_Cover_Pct": (max(fa1, 1000) / def_land1) * 100 if def_land1 > 0 else 0,
                "Annual_Deforestation_Rate": def_d1, "Annual_Afforestation_Rate": def_a1
            })
            hasil_list1.append(hasil1)

            # Prediksi Negara 2
            if st.session_state.compare_mode:
                fa2 = def_forest2 * (1 + (def_a2 - def_d2) / 100) ** (y - YEAR_MAX)
                hasil2 = predict_carbon({
                    "Country": negara2, "Primary_Driver_of_Change": "Mixed", "Year": y,
                    "Forest_Area_km2": max(fa2, 1000), "Land_Area_km2": def_land2,
                    "Forest_Cover_Pct": (max(fa2, 1000) / def_land2) * 100 if def_land2 > 0 else 0,
                    "Annual_Deforestation_Rate": def_d2, "Annual_Afforestation_Rate": def_a2
                })
                hasil_list2.append(hasil2)

        with st.container(border=True):
            st.markdown("<div class='header-text'>Prediksi Tren Karbon</div>", unsafe_allow_html=True)
            
            fig_line = go.Figure()
            # Garis Negara 1
            fig_line.add_trace(go.Scatter(
                x=thn_list, y=hasil_list1, mode="lines+markers+text", name=negara1,
                text=[f"{v/1e9:.1f}B" for v in hasil_list1], textposition="top center",
                line=dict(color="#4ADE80", width=4),
                marker=dict(size=10, color="#1E1E1E", line=dict(color="#4ADE80", width=3))
            ))
            
            # Garis Negara 2
            if st.session_state.compare_mode:
                fig_line.add_trace(go.Scatter(
                    x=thn_list, y=hasil_list2, mode="lines+markers+text", name=negara2,
                    text=[f"{v/1e9:.1f}B" for v in hasil_list2], textposition="bottom center",
                    line=dict(color="#F87171", width=4), # Warna merah kontras untuk pembanding
                    marker=dict(size=10, color="#1E1E1E", line=dict(color="#F87171", width=3))
                ))

            fig_line.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE, showlegend=True)
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Export Data Simulasi
            df_sim = pd.DataFrame({"Tahun": thn_list, f"Karbon_{negara1}": hasil_list1})
            if st.session_state.compare_mode: df_sim[f"Karbon_{negara2}"] = hasil_list2
            csv_sim = df_sim.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="DOWNLOAD HASIL SIMULASI (CSV)",
                data=csv_sim,
                file_name="hasil_simulasi_karbon.csv",
                mime="text/csv",
                use_container_width=True
            )

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
            if st.button("TERAPKAN ATURAN"):
                st.session_state.pol_run = True

    with col_r:
        if st.session_state.pol_run:
            base_data_pol = df[df["Country"] == negara_kebijakan]
            pol_land = float(base_data_pol["Land_Area_km2"].values[0]) if not base_data_pol.empty else 600000.0
            pol_forest = float(base_data_pol[base_data_pol["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) if not base_data_pol.empty else 400000.0

            bd = float(base_data_pol["Annual_Deforestation_Rate"].mean()) if not base_data_pol.empty else 2.0
            ba = float(base_data_pol["Annual_Afforestation_Rate"].mean()) if not base_data_pol.empty else 0.5

            kebijakan_diterapkan = []

            if p1:
                bd *= 0.65
                kebijakan_diterapkan.append("[WRI/CIFOR] Moratorium menurunkan laju tebang hingga 35%.")
            if p2:
                ba *= 1.5
                kebijakan_diterapkan.append("[REDD+] Injeksi dana mem-boost laju aforestasi sebesar 50%.")
            if p3:
                bd *= 0.75
                kebijakan_diterapkan.append("[Bank Dunia] Hukum karhutla memangkas hilangnya hutan sebesar 25%.")
            if p4:
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
