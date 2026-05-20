import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import joblib

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Carbon Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
defaults = {
    "page": "dashboard",
    "filters_applied": False,
    "applied_region": [],
    "applied_country": [],
    "applied_driver": [],
    "applied_year": None,
    "advanced_mode": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');

*{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

html, body, [class*="css"]{
    background-color: #FAFAF9 !important;
    color: #022C22 !important;
}

/* REMOVE STREAMLIT DEFAULT */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.block-container{
    max-width: 1350px !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
}

/* CARD */
.retro-card{
    background: white;
    border: 3px solid #022C22;
    border-radius: 24px;
    padding: 1.7rem;
    margin-bottom: 1.5rem;
    box-shadow: 6px 6px 0px #022C22;
}

/* TITLE */
.title-text{
    font-size: 2.5rem;
    font-weight: 800;
    color: #022C22;
    margin-bottom: 0.3rem;
}

.sub-text{
    font-size: 1rem;
    font-weight: 600;
    color: #064E3B;
}

.header-text{
    font-size: 1.4rem;
    font-weight: 800;
    margin-bottom: 1rem;
    color: #022C22;
}

/* BUTTON */
.stButton > button{
    width: 100%;
    border-radius: 999px;
    border: 3px solid #022C22;
    background: white;
    color: #022C22;
    font-weight: 800;
    font-size: 1rem;
    padding: 0.7rem;
    box-shadow: 4px 4px 0px #022C22;
    transition: 0.2s;
}

.stButton > button:hover{
    transform: translate(4px,4px);
    box-shadow: none;
    background: #D1FAE5;
}

/* METRIC */
[data-testid="stMetric"]{
    border: 3px solid #022C22;
    border-radius: 20px;
    padding: 1rem;
    background: white;
    box-shadow: 4px 4px 0px #022C22;
}

/* INPUT */
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div,
.stNumberInput input{
    border: 3px solid #022C22 !important;
    border-radius: 14px !important;
    background: white !important;
}

.stSlider{
    padding-top: 1rem;
}

/* TOGGLE */
[data-testid="stCheckbox"]{
    padding-top: 0.6rem;
}

/* REMOVE EMPTY SPACE */
.element-container:empty{
    display:none !important;
}

/* INSIGHT */
.insight-box{
    background: #FEF3C7;
    border: 3px dashed #022C22;
    border-radius: 18px;
    padding: 1.3rem;
    margin-top: 1rem;
    font-weight: 600;
    line-height: 1.7;
}

/* DIVIDER */
.custom-divider{
    height:2px;
    background:#022C22;
    margin-top:1rem;
    margin-bottom:1rem;
    border-radius:999px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():

    paths = [
        "global_deforestation_2000_2025 (2).csv",
        "global_deforestation_2000_2025.csv"
    ]

    def region(country):
        mapping = {
            "brazil": "Amerika Selatan",
            "indonesia": "Asia Tenggara",
            "canada": "Amerika Utara",
            "usa": "Amerika Utara",
            "congo": "Afrika",
            "india": "Asia",
            "china": "Asia",
            "australia": "Oseania",
            "russia": "Eropa & Asia"
        }

        return mapping.get(str(country).lower(), "Lainnya")

    for path in paths:
        if os.path.exists(path):
            df = pd.read_csv(path)

            if "Region" not in df.columns:
                df["Region"] = df["Country"].apply(region)

            return df

    return pd.DataFrame()

@st.cache_resource
def load_model():

    paths = [
        "model_xgboost.pkl"
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                return joblib.load(path)
            except:
                pass

    return None

df = load_data()
model = load_model()

COUNTRIES = sorted(df["Country"].dropna().unique())
REGIONS = sorted(df["Region"].dropna().unique())
DRIVERS = sorted(df["Primary_Driver_of_Change"].dropna().unique())

YEAR_MIN = int(df["Year"].min())
YEAR_MAX = int(df["Year"].max())

if st.session_state.applied_year is None:
    st.session_state.applied_year = YEAR_MAX

# ─────────────────────────────────────────────────────────────
# MODEL PREDICTION
# ─────────────────────────────────────────────────────────────
def predict_carbon(data):

    if model is not None:
        try:
            pred = model.predict(pd.DataFrame([data]))
            return float(pred[0])
        except:
            pass

    # fallback
    forest = data["Forest_Area_km2"]
    land = data["Land_Area_km2"]

    value = (
        np.log1p(forest) * 1000000
        + (forest / land) * 10000000
        - data["Annual_Deforestation_Rate"] * 100000
        + data["Annual_Afforestation_Rate"] * 50000
    )

    return max(value, 0)

# ─────────────────────────────────────────────────────────────
# FILTER FUNCTION
# ─────────────────────────────────────────────────────────────
def get_filtered_data():

    filtered = df.copy()

    if st.session_state.applied_region:
        filtered = filtered[
            filtered["Region"].isin(st.session_state.applied_region)
        ]

    if st.session_state.applied_country:
        filtered = filtered[
            filtered["Country"].isin(st.session_state.applied_country)
        ]

    if st.session_state.applied_driver:
        filtered = filtered[
            filtered["Primary_Driver_of_Change"].isin(
                st.session_state.applied_driver
            )
        ]

    yearly = filtered[
        filtered["Year"] == st.session_state.applied_year
    ]

    return filtered, yearly

# ─────────────────────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────────────────────
nav1, nav2, nav3 = st.columns(3)

with nav1:
    if st.button("PAPAN DATA"):
        st.session_state.page = "dashboard"
        st.rerun()

with nav2:
    if st.button("COBA SIMULASI"):
        st.session_state.page = "simulator"
        st.rerun()

with nav3:
    if st.button("ATURAN BARU"):
        st.session_state.page = "policy"
        st.rerun()

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CHART STYLE
# ─────────────────────────────────────────────────────────────
layout_style = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Plus Jakarta Sans",
        color="#022C22"
    ),
    margin=dict(l=10,r=10,t=40,b=10)
)

# ═════════════════════════════════════════════════════════════
# DASHBOARD
# ═════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":

    st.markdown("""
    <div class='retro-card'>
        <div class='title-text'>GLOBAL CARBON DASHBOARD</div>
        <div class='sub-text'>
            Monitor kondisi karbon dan deforestasi dunia secara interaktif.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # FILTER
    st.markdown("<div class='retro-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='header-text'>Filter Data</div>",
        unsafe_allow_html=True
    )

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        region = st.multiselect("Kawasan", REGIONS)

    with f2:
        country = st.multiselect("Negara", COUNTRIES)

    with f3:
        driver = st.multiselect("Penyebab", DRIVERS)

    with f4:
        year = st.selectbox(
            "Tahun",
            list(range(YEAR_MIN, YEAR_MAX + 1)),
            index=len(list(range(YEAR_MIN, YEAR_MAX + 1))) - 1
        )

    if st.button("TERAPKAN FILTER"):

        st.session_state.applied_region = region
        st.session_state.applied_country = country
        st.session_state.applied_driver = driver
        st.session_state.applied_year = year

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    df_filtered, df_year = get_filtered_data()

    # METRICS
    total_carbon = df_year["Total_Carbon_Stock_Tonnes"].sum()/1e12
    total_forest = df_year["Forest_Area_km2"].sum()/1e6
    avg_loss = df_year["Annual_Deforestation_Rate"].mean()
    avg_growth = df_year["Annual_Afforestation_Rate"].mean()

    k1,k2,k3,k4 = st.columns(4)

    k1.metric("TOTAL KARBON", f"{total_carbon:.2f} Tt")
    k2.metric("LUAS HUTAN", f"{total_forest:.2f} Jt km²")
    k3.metric("HUTAN HILANG", f"{avg_loss:.2f}%")
    k4.metric("HUTAN TUMBUH", f"{avg_growth:.2f}%")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # MAP
    st.markdown("<div class='retro-card'>", unsafe_allow_html=True)

    st.markdown(
        "<div class='header-text'>Peta Karbon Dunia</div>",
        unsafe_allow_html=True
    )

    fig = px.choropleth(
        df_year,
        locations="Country",
        locationmode="country names",
        color="Total_Carbon_Stock_Tonnes",
        color_continuous_scale=["#D1FAE5","#065F46"]
    )

    fig.update_layout(**layout_style)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # CHARTS
    c1, c2 = st.columns(2)

    with c1:

        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)

        st.markdown(
            "<div class='header-text'>Penyebab Deforestasi</div>",
            unsafe_allow_html=True
        )

        drv = df_filtered.groupby(
            "Primary_Driver_of_Change"
        ).size().reset_index(name="Total")

        fig_drv = px.bar(
            drv,
            x="Total",
            y="Primary_Driver_of_Change",
            orientation="h"
        )

        fig_drv.update_layout(**layout_style)

        st.plotly_chart(fig_drv, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with c2:

        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)

        st.markdown(
            "<div class='header-text'>Top Negara Karbon</div>",
            unsafe_allow_html=True
        )

        top = df_year.nlargest(5, "Total_Carbon_Stock_Tonnes")

        fig_top = px.bar(
            top,
            x="Total_Carbon_Stock_Tonnes",
            y="Country",
            orientation="h"
        )

        fig_top.update_layout(**layout_style)

        st.plotly_chart(fig_top, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# SIMULATOR
# ═════════════════════════════════════════════════════════════
elif st.session_state.page == "simulator":

    st.markdown("""
    <div class='retro-card'>
        <div class='title-text'>SIMULATOR KARBON</div>
        <div class='sub-text'>
            Prediksi masa depan karbon berdasarkan kondisi hutan.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("simulator_form"):

        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)

        with c1:
            country = st.selectbox("Negara", COUNTRIES)

        with c2:
            driver = st.selectbox("Penyebab Utama", DRIVERS)

        with c3:
            target_year = st.slider("Tahun Target", 2026, 2050, 2035)

        st.markdown(
            "<div class='custom-divider'></div>",
            unsafe_allow_html=True
        )

        s1,s2 = st.columns(2)

        with s1:
            def_rate = st.slider(
                "Laju Deforestasi (%)",
                0.0,
                5.0,
                1.2,
                0.1
            )

        with s2:
            aff_rate = st.slider(
                "Laju Reforestasi (%)",
                0.0,
                5.0,
                0.6,
                0.1
            )

        # TOGGLE ADVANCED
        advanced = st.toggle("Aktifkan Pengaturan Lanjutan")

        base = df[df["Country"] == country]

        default_land = float(base["Land_Area_km2"].iloc[0])
        default_forest = float(
            base[base["Year"] == YEAR_MAX]["Forest_Area_km2"].iloc[0]
        )

        if advanced:

            st.markdown(
                "<div class='custom-divider'></div>",
                unsafe_allow_html=True
            )

            a1,a2 = st.columns(2)

            with a1:
                forest_input = st.number_input(
                    "Luas Hutan Awal",
                    value=default_forest
                )

            with a2:
                land_input = st.number_input(
                    "Luas Daratan",
                    value=default_land
                )

        else:
            forest_input = default_forest
            land_input = default_land

        submit = st.form_submit_button(
            "JALANKAN SIMULASI",
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    if submit:

        years = []
        values = []

        for year in range(YEAR_MAX, target_year + 1):

            forest_area = forest_input * (
                1 + (aff_rate - def_rate)/100
            ) ** (year - YEAR_MAX)

            pred = predict_carbon({
                "Country": country,
                "Primary_Driver_of_Change": driver,
                "Year": year,
                "Forest_Area_km2": forest_area,
                "Land_Area_km2": land_input,
                "Forest_Cover_Pct": (
                    forest_area / land_input
                ) * 100,
                "Annual_Deforestation_Rate": def_rate,
                "Annual_Afforestation_Rate": aff_rate
            })

            years.append(year)
            values.append(pred)

        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)

        st.markdown(
            "<div class='header-text'>Hasil Simulasi</div>",
            unsafe_allow_html=True
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                mode="lines+markers"
            )
        )

        fig.update_layout(**layout_style)

        st.plotly_chart(fig, use_container_width=True)

        start = values[0]
        end = values[-1]

        diff = ((end-start)/start)*100

        if diff > 0:
            msg = f"""
            📈 Stok karbon diperkirakan meningkat sebesar
            <b>{diff:.2f}%</b> pada tahun <b>{target_year}</b>.
            """
        else:
            msg = f"""
            📉 Stok karbon diperkirakan menurun sebesar
            <b>{abs(diff):.2f}%</b> pada tahun <b>{target_year}</b>.
            """

        st.markdown(
            f"<div class='insight-box'>{msg}</div>",
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# POLICY
# ═════════════════════════════════════════════════════════════
else:

    st.markdown("""
    <div class='retro-card'>
        <div class='title-text'>SIMULATOR KEBIJAKAN</div>
        <div class='sub-text'>
            Simulasikan dampak kebijakan terhadap karbon dunia.
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:

        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)

        country = st.selectbox(
            "Pilih Negara",
            COUNTRIES
        )

        stop_logging = st.toggle("Stop Tebang Komersial")
        reforestation = st.toggle("Tambah Reforestasi")
        fire_law = st.toggle("Hukum Pembakaran Hutan")
        farmer = st.toggle("Insentif Petani")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        base = df[df["Country"] == country]

        land = float(base["Land_Area_km2"].iloc[0])

        forest = float(
            base[base["Year"] == YEAR_MAX]["Forest_Area_km2"].iloc[0]
        )

        deforestation = 2.0
        afforestation = 0.5

        if stop_logging:
            deforestation *= 0.4

        if reforestation:
            afforestation *= 2.5

        if fire_law:
            deforestation *= 0.8

        if farmer:
            afforestation *= 1.3

        pred = predict_carbon({
            "Country": country,
            "Primary_Driver_of_Change": "Policy",
            "Year": 2030,
            "Forest_Area_km2": forest,
            "Land_Area_km2": land,
            "Forest_Cover_Pct": (forest/land)*100,
            "Annual_Deforestation_Rate": deforestation,
            "Annual_Afforestation_Rate": afforestation
        })

        st.markdown("<div class='retro-card'>", unsafe_allow_html=True)

        st.markdown(
            f"<div class='header-text'>Proyeksi {country}</div>",
            unsafe_allow_html=True
        )

        m1,m2 = st.columns(2)

        m1.metric("DEFORESTASI", f"{deforestation:.2f}%")
        m2.metric("REFORESTASI", f"{afforestation:.2f}%")

        st.metric(
            "ESTIMASI KARBON 2030",
            f"{pred:,.0f} Ton"
        )

        st.markdown("</div>", unsafe_allow_html=True)
