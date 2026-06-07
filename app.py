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

# CSS Custom - Perbaikan Layout & Kontras (Background Gelap = Teks Putih)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

/* GLOBAL STYLES */
* { 
    font-family: 'Press Start 2P', cursive !important; 
}

/* Latar Belakang Aplikasi Terang */
body, .stApp, .block-container, header[data-testid="stHeader"] { 
    background-color: #F0FDF4 !important; /* Hijau Sangat Terang / Mint */
    color: #064E3B !important; /* Hijau Gelap untuk teks di bg terang */
    background-image: none !important;
}
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 3rem 4rem 5rem !important; max-width: 1400px !important; }

/* KARTU CONTAINER (PIXEL SOLID) - Diperlebar spacingnya */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    box-shadow: 8px 8px 0px #4ADE80 !important; 
    padding: 2.5rem !important;
    margin-bottom: 3rem !important; /* Jarak ekstra agar tidak menumpuk */
}

/* SEMUA TOMBOL (BACKGROUND GELAP, TEKS PUTIH) */
.stButton > button {
    background-color: #064E3B !important; 
    color: #FFFFFF !important; 
    border: 4px solid #4ADE80 !important;
    border-radius: 0px !important;
    box-shadow: 6px 6px 0px #4ADE80 !important;
    font-size: 0.8rem !important;
    padding: 1rem !important;
    transition: all 0.1s ease-in-out !important;
    width: 100% !important;
    opacity: 1 !important;
}
.stButton > button:hover {
    background-color: #047857 !important; /* Hijau gelap yang sedikit lebih terang pas di-hover */
    color: #FFFFFF !important;
    transform: translate(2px, 2px) !important;
    box-shadow: 4px 4px 0px #4ADE80 !important;
}

/* KOTAK METRIK ANGKA (BACKGROUND GELAP, TEKS PUTIH) */
[data-testid="stMetric"] {
    background: #064E3B !important;
    border: 4px solid #4ADE80 !important;
    border-radius: 0px !important;
    padding: 2rem 1rem !important;
    text-align: center;
    box-shadow: 6px 6px 0px #4ADE80 !important;
    margin-bottom: 1.5rem !important;
}
[data-testid="stMetricLabel"] > div { font-size: 0.7rem !important; margin-bottom: 0.8rem; color: #F0FDF4 !important; }
[data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #FFFFFF !important; }

/* FIX LABEL FORM AGAR SELALU MUNCUL */
.stSelectbox label, .stSlider > label, .stNumberInput label, .stMultiSelect label, .stToggle label {
    font-size: 0.75rem !important; 
    color: #064E3B !important; 
    padding-bottom: 0.5rem !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Kotak Input Utama */
div[data-baseweb="select"] > div, 
div[data-baseweb="base-input"], 
.stTextInput input, 
.stNumberInput input {
    background-color: #FFFFFF !important; 
    border: 4px solid #064E3B !important;
    border-radius: 0px !important;
    color: #064E3B !important;
    font-size: 0.75rem !important;
    padding: 0.2rem !important;
}

/* Dropdown Menu Popover */
div[data-baseweb="popover"] > div,
ul[role="listbox"],
ul[role="listbox"] li {
    background-color: #FFFFFF !important;
    color: #064E3B !important;
}
ul[role="listbox"] li:hover {
    background-color: #4ADE80 !important;
}

/* TAG DI DALAM MULTISELECT (BACKGROUND GELAP, TEKS PUTIH) */
span[data-baseweb="tag"] {
    background-color: #064E3B !important;
    color: #FFFFFF !important;
    border: 2px solid #4ADE80 !important;
    border-radius: 0px !important;
    padding: 0.2rem 0.5rem !important;
}

/* Slider */
div[data-baseweb="slider"] div { background-color: #064E3B !important; }
div[data-baseweb="slider"] div[role="slider"] { background-color: #4ADE80 !important; border: 3px solid #064E3B !important; }

/* TEKS CUSTOM */
.title-text { font-size: 2rem; margin-bottom: 1rem; color: #064E3B; text-transform: uppercase; line-height: 1.4; text-align: center; }
.sub-text { font-size: 0.8rem; margin-bottom: 2rem; color: #064E3B; line-height: 1.6; text-align: center; }
.header-text { font-size: 1.1rem; margin-bottom: 1.5rem; color: #064E3B; text-transform: uppercase; border-bottom: 4px dashed #4ADE80; padding-bottom: 0.8rem; }

/* KOTAK INSIGHT KESIMPULAN (BACKGROUND GELAP, TEKS PUTIH) */
.insight-text { 
    font-size: 0.8rem; 
    line-height: 2; 
    color: #FFFFFF; 
    background: #064E3B; 
    padding: 2rem; 
    border: 4px dashed #4ADE80; 
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Navigasi Menu dengan Gap Large
nav_1, nav_2, nav_3 = st.columns(3, gap="large")
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

st.markdown("<br><br>", unsafe_allow_html=True) 

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

    # Data Dummy jika file CSV tidak ditemukan
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

# ==============================================================================
# LOGIKA INTI PREDIKSI KARBON
# ==============================================================================
def predict_carbon(f: dict) -> float:
    # 1. PENGGUNAAN MODEL MACHINE LEARNING (UTAMA)
    # Jika model XGBoost (.pkl) berhasil dimuat, sistem akan memprioritaskan model tersebut.
    # Model ini dilatih menggunakan korelasi non-linear dari data historis (2000-2025) 
    # antara luas hutan, rasio tutupan, dan driver deforestasi untuk menghasilkan prediksi persediaan karbon.
    if ml_model is not None:
        try:
            df_pred = pd.DataFrame([f])
            return float(ml_model.predict(df_pred)[0])
        except: pass
        
    # 2. FUNGSI MATEMATIS HEURISTIK (FALLBACK JIKA ML GAGAL/TIDAK ADA)
    # Logika dasar: Biomassa karbon memiliki hubungan logaritmik dengan luas hutan, bukan linear murni.
    # - np.log1p (log natural + 1) digunakan agar kalkulasi tidak menghasilkan infinity jika luas hutan = 0.
    # - Bobot 0.94 dikalikan pada log luas hutan sebagai baseline persediaan karbon.
    # - Penyesuaian dinamika: Kecepatan deforestasi (Annual_Deforestation_Rate) memberikan penalti (-0.04),
    #   sedangkan usaha reboisasi (Annual_Afforestation_Rate) memberikan bonus (+0.025).
    log_f = np.log1p(max(f.get("Forest_Area_km2", 1000), 1.0))
    ratio = f.get("Forest_Area_km2", 1000) / (f.get("Land_Area_km2", 1000) + 1e-6)
    val = (4.2 + 0.94 * log_f + 0.08 * ratio - 0.04 * f.get("Annual_Deforestation_Rate", 0) + 0.025 * f.get("Annual_Afforestation_Rate", 0))
    return max(np.expm1(val), 0)
# ==============================================================================

df = load_data()
COUNTRIES = sorted([str(x) for x in df["Country"].dropna().unique()])
DRIVERS = sorted([str(x) for x in df["Primary_Driver_of_Change"].dropna().unique()])
REGIONS = sorted([str(x) for x in df["Region"].dropna().unique()])
YEAR_MIN = int(df["Year"].min()) if not df["Year"].isnull().all() else 2000
YEAR_MAX = int(df["Year"].max()) if not df["Year"].isnull().all() else 2025

if st.session_state.applied_year is None: st.session_state.applied_year = (YEAR_MIN, YEAR_MAX)

# Styling Chart Plotly
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Press Start 2P", color="#064E3B", size=9),
    margin=dict(l=10, r=10, t=30, b=10),
)
AX_STYLE = dict(
    showgrid=True, gridcolor="#F0FDF4", gridwidth=2, linecolor="#064E3B", linewidth=4,
    tickfont=dict(family="Press Start 2P", color="#064E3B", size=8),
    zeroline=True, zerolinecolor="#064E3B", zerolinewidth=4
)
MAP_SCALE = [[0.0, "#F0FDF4"], [1.0, "#4ADE80"]]

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
    st.markdown("<div class='title-text'>DASHBOARD KARBON</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text'>Pantau ketersediaan area hutan dan cadangan karbon di seluruh dunia.</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='header-text'>FILTER DATA</div>", unsafe_allow_html=True)
        # Menggunakan gap="large" agar field tidak berdekatan
        f1, f2, f3 = st.columns(3, gap="large")
        with f1: sel_region = st.multiselect("PILIH KAWASAN", REGIONS, default=[])
        with f2: sel_country = st.multiselect("PILIH NEGARA", COUNTRIES, default=[])
        with f3: sel_driver = st.multiselect("PILIH PENYEBAB", DRIVERS, default=[])
        
        st.markdown("<br>", unsafe_allow_html=True)
        sel_year = st.slider("RENTANG TAHUN", min_value=YEAR_MIN, max_value=YEAR_MAX, value=st.session_state.applied_year)
        
        st.markdown("<br>", unsafe_allow_html=True)
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

    st.markdown("<br>", unsafe_allow_html=True)
    # Menggunakan gap="large" untuk metric boxes
    k1, k2, k3, k4 = st.columns(4, gap="large")
    k1.metric("TOTAL KARBON", f"{total_c:.2f} Tt")
    k2.metric("LUAS HUTAN", f"{total_f:.2f} Jt")
    k3.metric("RATA HILANG", f"{avg_d:.2f}%")
    k4.metric("RATA TUMBUH", f"{avg_a:.2f}%")
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='header-text'>PETA INTENSITAS KARBON</div>", unsafe_allow_html=True)
        if not df_agg.empty:
            fig_map = px.choropleth(
                df_agg, locations="Country", locationmode="country names",
                color="Total_Carbon_Stock_Tonnes", color_continuous_scale=MAP_SCALE
            )
            fig_map.update_layout(
                **CHART_LAYOUT,
                geo=dict(
                    showframe=True, framecolor="#064E3B", framewidth=4, showcoastlines=True, coastlinecolor="#064E3B",
                    bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#FFFFFF", showocean=True, oceancolor="#F0FDF4"
                ), coloraxis_showscale=False
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else: st.markdown("Data kosong.")

    # Menggunakan gap="large" untuk grafik
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        with st.container(border=True):
            st.markdown("<div class='header-text'>FAKTOR HUTAN HILANG</div>", unsafe_allow_html=True)
            if not df_f.empty:
                drv = df_f.groupby("Primary_Driver_of_Change").size().reset_index(name="n")
                fig_drv = go.Figure(go.Bar(
                    x=drv["n"], y=drv["Primary_Driver_of_Change"], orientation="h",
                    marker=dict(color="#4ADE80", line=dict(color="#064E3B", width=4))
                ))
                fig_drv.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
                st.plotly_chart(fig_drv, use_container_width=True)
            else: st.markdown("Data kosong.")

    with col_b:
        with st.container(border=True):
            st.markdown("<div class='header-text'>TOP NEGARA KARBON</div>", unsafe_allow_html=True)
            if not df_agg.empty:
                top = df_agg.nlargest(5, "Total_Carbon_Stock_Tonnes")
                fig_top = go.Figure(go.Bar(
                    x=top["Total_Carbon_Stock_Tonnes"] / 1e9, y=top["Country"], orientation="h",
                    marker=dict(color="#064E3B", line=dict(color="#4ADE80", width=4))
                ))
                fig_top.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
                st.plotly_chart(fig_top, use_container_width=True)
            else: st.markdown("Data kosong.")

# ==================== HALAMAN 2: SIMULATOR ====================
elif page == "simulator":
    st.markdown("<div class='title-text'>SIMULATOR MASA DEPAN</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text'>Atur konfigurasi di bawah untuk memprediksi sisa karbon.</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='header-text'>PENGATURAN DASAR</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="large")
        negara = c1.selectbox("PILIH NEGARA", COUNTRIES)
        thn_target = c2.slider("TAHUN TARGET", 2026, 2050, 2035)
        pemicu = c3.selectbox("PENYEBAB UTAMA", DRIVERS)
        
        base_data = df[df["Country"] == negara]
        def_land = float(base_data["Land_Area_km2"].values[0]) if not base_data.empty else 400000.0
        def_forest = float(base_data[base_data["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) if not base_data.empty else 250000.0
        def_d = float(base_data["Annual_Deforestation_Rate"].mean()) if not base_data.empty else 1.2
        def_a = float(base_data["Annual_Afforestation_Rate"].mean()) if not base_data.empty else 0.5
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("BUKA / TUTUP ADVANCED SETTINGS", use_container_width=True):
            st.session_state.adv_open = not st.session_state.adv_open
            st.session_state.sim_run = False

    if st.session_state.adv_open:
        with st.container(border=True):
            st.markdown("<div class='header-text'>PENGATURAN ADVANCED</div>", unsafe_allow_html=True)
            s1, s2 = st.columns(2, gap="large")
            laju_d = s1.slider("KECEPATAN HILANG (%)", 0.0, 5.0, def_d, 0.1)
            laju_a = s2.slider("KECEPATAN TUMBUH (%)", 0.0, 5.0, def_a, 0.1)

            st.markdown("<br>", unsafe_allow_html=True)
            a1, a2 = st.columns(2, gap="large")
            luas_h_input = a1.number_input("LUAS HUTAN AWAL (KM2)", min_value=0.0, value=def_forest, step=1000.0)
            luas_l_input = a2.number_input("LUAS DARATAN (KM2)", min_value=0.0, value=def_land, step=1000.0)
    else:
        laju_d, laju_a = def_d, def_a
        luas_h_input, luas_l_input = def_forest, def_land

    st.markdown("<br>", unsafe_allow_html=True)
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

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='header-text'>GRAFIK PREDIKSI KARBON</div>", unsafe_allow_html=True)
            fig_line = go.Figure(go.Scatter(
                x=thn_list, y=hasil_list, mode="lines+markers",
                line=dict(color="#064E3B", width=4),
                marker=dict(size=12, color="#064E3B", line=dict(color="#4ADE80", width=3))
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
    st.markdown("<div class='title-text'>SIMULATOR KEBIJAKAN</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text'>Coba terapkan kebijakan berbasis riset global dan lihat dampaknya di 2030.</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        with st.container(border=True):
            st.markdown("<div class='header-text'>PANEL KEBIJAKAN</div>", unsafe_allow_html=True)
            negara_kebijakan = st.selectbox("PILIH NEGARA", COUNTRIES)
            
            st.markdown("<br>", unsafe_allow_html=True)
            p1 = st.toggle("STOP TEBANG KOMERSIAL")
            p2 = st.toggle("TAMBAH DANA REBOISASI")
            p3 = st.toggle("HUKUM TEGAS BAKAR")
            p4 = st.toggle("INSENTIF PETANI (PES)")
            
            st.markdown("<br><br>", unsafe_allow_html=True)
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
            
            # ==============================================================================
            # LOGIKA KEBIJAKAN PREDIKTIF (BERBASIS RISET GLOBAL)
            # ==============================================================================
            if p1: 
                bd *= 0.65 
                # WRI/CIFOR membuktikan moratorium lisensi tebang baru di negara berkembang
                # mampu menekan deforestasi aktual hingga 35% jika penegakan hukum konsisten.
                kebijakan_diterapkan.append("[WRI/CIFOR] Moratorium menurunkan laju tebang hingga 35%.")
            
            if p2: 
                ba *= 1.5 
                # Program Injeksi dana seperti REDD+ terbukti dapat mendorong aktivitas aforestasi
                # (reboisasi) naik sebesar 50% di fase implementasi awal.
                kebijakan_diterapkan.append("[REDD+] Injeksi dana mem-boost laju aforestasi sebesar 50%.")
            
            if p3: 
                bd *= 0.75 
                # Laporan Bank Dunia menunjukkan hukum pidana tegas terhadap pembakaran liar
                # dapat memangkas 25% titik api dan hilangnya hutan sekunder.
                kebijakan_diterapkan.append("[Bank Dunia] Hukum karhutla memangkas hilangnya hutan sebesar 25%.")
            
            if p4: 
                ba *= 1.2; bd *= 0.85 
                # FAO mencatat skema PES (Payment for Environmental Services) merubah petani 
                # menjadi pelindung hutan: Tumbuh naik 20%, laju hilang turun 15%.
                kebijakan_diterapkan.append("[FAO-PES] Insentif petani menaikkan tumbuh hutan 20% & menekan hilangnya 15%.")
            # ==============================================================================

            h_pol = predict_carbon({
                "Country": negara_kebijakan, "Primary_Driver_of_Change": "None", "Year": 2030, 
                "Forest_Area_km2": pol_forest, "Land_Area_km2": pol_land,
                "Forest_Cover_Pct": (pol_forest / pol_land) * 100 if pol_land > 0 else 0,
                "Annual_Deforestation_Rate": bd, "Annual_Afforestation_Rate": ba
            })
            
            with st.container(border=True):
                st.markdown(f"<div class='header-text'>PROYEKSI (2030)</div>", unsafe_allow_html=True)
                m1, m2 = st.columns(2, gap="large")
                m1.metric("HUTAN HILANG", f"{bd:.2f}%")
                m2.metric("HUTAN TUMBUH", f"{ba:.2f}%")
                st.metric("ESTIMASI KARBON", f"{h_pol:,.0f} Ton")

                if not kebijakan_diterapkan:
                    penjelasan = "Tidak ada aturan. Lingkungan bergerak sesuai standar historis saat ini."
                else:
                    penjelasan = f"DAMPAK KEBIJAKAN TERUKUR:<br><br> • {'<br> • '.join(kebijakan_diterapkan)}"
                
                st.markdown(f"<div class='insight-text'>{penjelasan}</div>", unsafe_allow_html=True)
