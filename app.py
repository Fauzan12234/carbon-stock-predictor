import streamlit as st # Library utama untuk antarmuka web
import pandas as pd # Untuk pengolahan data tabular
import numpy as np # Untuk komputasi angka dan logika matematis
import plotly.express as px # Membuat grafik peta dan interaktif
import plotly.graph_objects as go # Kustomisasi detail grafik
import os # Mengecek keberadaan file dataset
import joblib # Memuat model Machine Learning

# Pengaturan dasar halaman web Streamlit
st.set_page_config(
    page_title="Global Carbon Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Menyimpan state halaman agar tidak ter-reset saat pengguna berinteraksi
if "page" not in st.session_state: st.session_state.page = "dashboard"
if "filters_applied" not in st.session_state: st.session_state.filters_applied = False
if "applied_region" not in st.session_state: st.session_state.applied_region = []
if "applied_country" not in st.session_state: st.session_state.applied_country = []
if "applied_driver" not in st.session_state: st.session_state.applied_driver = []
if "applied_year" not in st.session_state: st.session_state.applied_year = None

# Kode CSS khusus untuk mengatur warna, layout, dan menghilangkan elemen default yang mengganggu
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');

/* Mengatur font seluruh halaman */
* { font-family: 'Plus Jakarta Sans', sans-serif !important; color: #022C22 !important; }

/* Menghilangkan sidebar dan merapikan padding kontainer utama */
body, .stApp, .block-container, header[data-testid="stHeader"] { background-color: #FAFAF9 !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 2rem 2.25rem 5rem !important; max-width: 1250px !important; }

/* Gaya retro untuk komponen container dan form bawaan Streamlit */
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] {
    background-color: #FFFFFF !important;
    border: 3px solid #022C22 !important;
    border-radius: 24px !important;
    box-shadow: 5px 5px 0px #022C22 !important;
    padding: 1.5rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 1rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover, [data-testid="stForm"]:hover {
    transform: translateY(-3px);
    box-shadow: 8px 8px 0px #022C22 !important;
}

/* Desain tombol aksi */
.stButton > button, [data-testid="baseButton-secondaryFormSubmit"] {
    background-color: #FFFFFF !important;
    color: #022C22 !important;
    border: 3px solid #022C22 !important;
    border-radius: 100px !important;
    box-shadow: 4px 4px 0px #022C22 !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    padding: 0.6rem !important;
    transition: all 0.1s ease;
}
.stButton > button:hover, [data-testid="baseButton-secondaryFormSubmit"]:hover {
    background-color: #D1FAE5 !important;
    box-shadow: 0px 0px 0px #022C22 !important;
    transform: translate(4px, 4px) !important;
}

/* Desain kotak angka/metrik */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 2px solid #022C22 !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    text-align: center;
}
[data-testid="stMetricLabel"] > div { font-size: 1rem !important; font-weight: 800 !important; }
[data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; }

/* Desain form input dan memastikan dropdown background-nya putih penuh */
.stSelectbox label, .stSlider > label, .stNumberInput label, .stMultiSelect label {
    font-size: 1.05rem !important; font-weight: 800 !important; color: #022C22 !important;
}
div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
    background-color: #FFFFFF !important; 
    border: 2px solid #022C22 !important;
    border-radius: 12px !important;
}
div[role="listbox"], ul[role="listbox"], div[data-baseweb="popover"] { background-color: #FFFFFF !important; }
ul[role="listbox"] li { color: #022C22 !important; font-weight: 700 !important; }
span[data-baseweb="tag"] { background-color: #D1FAE5 !important; border: 2px solid #022C22 !important; }

/* Desain header dropdown menu advanced */
[data-testid="stExpander"] { background-color: #FFFFFF !important; border: 2px solid #022C22 !important; border-radius: 16px !important; }
[data-testid="stExpander"] summary p { font-weight: 800 !important; font-size: 1.1rem !important; }
[data-testid="stCheckbox"] label p { font-weight: 700 !important; font-size: 1.1rem !important; }

/* Format ukuran dan style teks */
.title-text { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.2rem; color: #022C22; text-transform: uppercase; }
.sub-text { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #064E3B; }
.header-text { font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem; color: #022C22; }
.insight-text { font-size: 1.15rem; font-weight: 600; line-height: 1.6; color: #022C22; background: #FDE68A; padding: 1.5rem; border-radius: 16px; border: 2px dashed #022C22; margin-top: 1rem;}
</style>
""", unsafe_allow_html=True)

# Membuat tiga kolom navigasi menu utama
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

st.write("")

# Memuat dan memproses Dataset dengan fallback data dummy jika file tidak ditemukan
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

# Memuat model ML XGBoost dari lokal
@st.cache_resource
def load_ml_model():
    paths = ["model_xgboost.pkl", "/content/drive/MyDrive/Tugas Week 12/model_xgboost.pkl"]
    for p in paths:
        if os.path.exists(p):
            try: return joblib.load(p)
            except: pass
    return None

ml_model = load_ml_model()

# Algoritma memprediksi karbon menggunakan ML atau rumus dasar sebagai cadangan
def predict_carbon(f: dict) -> float:
    if ml_model is not None:
        try:
            df_pred = pd.DataFrame([f])
            pred = ml_model.predict(df_pred)
            return float(pred[0])
        except: pass
    log_f = np.log1p(max(f.get("Forest_Area_km2", 1000), 1.0))
    ratio = f.get("Forest_Area_km2", 1000) / (f.get("Land_Area_km2", 1000) + 1e-6)
    val = (4.2 + 0.94 * log_f + 0.08 * ratio - 0.04 * f.get("Annual_Deforestation_Rate", 0) + 0.025 * f.get("Annual_Afforestation_Rate", 0))
    return max(np.expm1(val), 0)

# Parsing parameter inti dataset
df = load_data()
COUNTRIES = sorted([str(x) for x in df["Country"].dropna().unique()])
DRIVERS = sorted([str(x) for x in df["Primary_Driver_of_Change"].dropna().unique()])
REGIONS = sorted([str(x) for x in df["Region"].dropna().unique()])
YEAR_MIN = int(df["Year"].min()) if not df["Year"].isnull().all() else 2000
YEAR_MAX = int(df["Year"].max()) if not df["Year"].isnull().all() else 2025

if st.session_state.applied_year is None: st.session_state.applied_year = YEAR_MAX

# Konfigurasi gaya grafik agar seragam
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#022C22", size=14),
    margin=dict(l=10, r=10, t=30, b=10),
)
AX_STYLE = dict(
    showgrid=True, gridcolor="#E2E8F0", gridwidth=2, linecolor="#022C22", linewidth=3,
    tickfont=dict(family="Plus Jakarta Sans", color="#022C22", size=13),
    zeroline=True, zerolinecolor="#022C22", zerolinewidth=3
)
MAP_SCALE = [[0.0, "#D1FAE5"], [1.0, "#064E3B"]]

# Modul filtrasi data di dashboard
def get_filtered_data():
    if not st.session_state.filters_applied:
        return df, df[df["Year"] == st.session_state.applied_year]
    dff = df.copy()
    if st.session_state.applied_region: dff = dff[dff["Region"].astype(str).isin(st.session_state.applied_region)]
    if st.session_state.applied_country: dff = dff[dff["Country"].astype(str).isin(st.session_state.applied_country)]
    if st.session_state.applied_driver: dff = dff[dff["Primary_Driver_of_Change"].astype(str).isin(st.session_state.applied_driver)]
    df_yr = dff[dff["Year"] == st.session_state.applied_year]
    return dff, df_yr

page = st.session_state.page

# ==================== HALAMAN 1: PAPAN DATA ====================
if page == "dashboard":
    with st.container(border=True):
        st.markdown("<div class='title-text'>DATA KARBON DUNIA</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Cek ketersediaan jumlah pohon dan karbon di seluruh dunia saat ini.</div>", unsafe_allow_html=True)

    # Area filtrasi interaktif
    with st.container(border=True):
        st.markdown("<div class='header-text'>Filter Data Pilihan</div>", unsafe_allow_html=True)
        f1, f2, f3, f4 = st.columns(4)
        with f1: sel_region = st.multiselect("KAWASAN", REGIONS, default=[])
        with f2: sel_country = st.multiselect("NEGARA", COUNTRIES, default=[])
        with f3: sel_driver = st.multiselect("PENYEBAB", DRIVERS, default=[])
        year_options = ["Semua Tahun"] + list(range(YEAR_MIN, YEAR_MAX + 1))
        default_year_idx = year_options.index(st.session_state.applied_year) if st.session_state.applied_year in year_options else 0
        with f4: sel_year = st.selectbox("TAHUN", year_options, index=default_year_idx)

        if st.button("Terapkan Visualisasi", use_container_width=True):
            st.session_state.applied_region = sel_region
            st.session_state.applied_country = sel_country
            st.session_state.applied_driver = sel_driver
            st.session_state.applied_year = YEAR_MAX if sel_year == "Semua Tahun" else sel_year
            st.session_state.filters_applied = True
            st.rerun()

    df_f, df_yr = get_filtered_data()

    # Perhitungan total hasil filter
    if not df_yr.empty:
        total_c = df_yr["Total_Carbon_Stock_Tonnes"].sum() / 1e12
        total_f = df_yr["Forest_Area_km2"].sum() / 1e6
        avg_d = df_yr["Annual_Deforestation_Rate"].mean()
        avg_a = df_yr["Annual_Afforestation_Rate"].mean()
    else: total_c = total_f = avg_d = avg_a = 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("TOTAL KARBON", f"{total_c:.2f} Tt")
    k2.metric("LUAS HUTAN", f"{total_f:.2f} Jt km²")
    k3.metric("RATA-RATA HILANG", f"{avg_d:.2f}%")
    k4.metric("RATA-RATA TUMBUH", f"{avg_a:.2f}%")
    st.write("")

    # Pembuatan Peta Globe Karbon
    with st.container(border=True):
        st.markdown("<div class='header-text'>Peta Intensitas Karbon</div>", unsafe_allow_html=True)
        if not df_yr.empty:
            fig_map = px.choropleth(
                df_yr, locations="Country", locationmode="country names",
                color="Total_Carbon_Stock_Tonnes", color_continuous_scale=MAP_SCALE
            )
            fig_map.update_layout(
                **CHART_LAYOUT,
                geo=dict(
                    showframe=True, framecolor="#022C22", framewidth=3, showcoastlines=True, coastlinecolor="#022C22",
                    bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#F8FAFC", showocean=True, oceancolor="#DBEAFE"
                ), coloraxis_showscale=False
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else: st.write("Data visualisasi kosong.")

    # Kolom statistik bar chart
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("<div class='header-text'>Faktor Penyebab Hutan Hilang</div>", unsafe_allow_html=True)
            if not df_f.empty:
                drv = df_f.groupby("Primary_Driver_of_Change").size().reset_index(name="n")
                fig_drv = go.Figure(go.Bar(
                    x=drv["n"], y=drv["Primary_Driver_of_Change"], orientation="h",
                    marker=dict(color="#D1FAE5", line=dict(color="#022C22", width=3))
                ))
                fig_drv.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
                st.plotly_chart(fig_drv, use_container_width=True)
            else: st.write("Data visualisasi kosong.")

    with col_b:
        with st.container(border=True):
            st.markdown("<div class='header-text'>Negara Karbon Tertinggi</div>", unsafe_allow_html=True)
            if not df_yr.empty:
                top = df_yr.nlargest(5, "Total_Carbon_Stock_Tonnes")
                fig_top = go.Figure(go.Bar(
                    x=top["Total_Carbon_Stock_Tonnes"] / 1e9, y=top["Country"], orientation="h",
                    marker=dict(color="#34D399", line=dict(color="#022C22", width=3))
                ))
                fig_top.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
                st.plotly_chart(fig_top, use_container_width=True)
            else: st.write("Data visualisasi kosong.")

# ==================== HALAMAN 2: SIMULATOR ====================
elif page == "simulator":
    with st.container(border=True):
        st.markdown("<div class='title-text'>TEBAK MASA DEPAN</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Atur konfigurasi di bawah untuk memprediksi sisa cadangan karbon global. (Terhubung dengan XGBoost model)</div>", unsafe_allow_html=True)

    # Form simulasi untuk interaksi Machine Learning
    with st.form("form_sim", border=True):
        c1, c2, c3 = st.columns(3)
        negara = c1.selectbox("PILIH NEGARA", COUNTRIES)
        thn_target = c2.slider("TAHUN TARGET", 2026, 2050, 2035)
        pemicu = c3.selectbox("PENYEBAB UTAMA", DRIVERS)
        
        # Pengaturan lanjutan disembunyikan didalam expander
        st.write("")
        with st.expander("PENGATURAN LANJUTAN (ADVANCED)"):
            base_data = df[df["Country"] == negara]
            def_land = float(base_data["Land_Area_km2"].values[0]) if not base_data.empty else 400000.0
            def_forest = float(base_data[base_data["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) if not base_data.empty else 250000.0
            def_d = float(base_data["Annual_Deforestation_Rate"].mean()) if not base_data.empty else 1.2
            def_a = float(base_data["Annual_Afforestation_Rate"].mean()) if not base_data.empty else 0.5
            
            s1, s2 = st.columns(2)
            laju_d = s1.slider("KECEPATAN HUTAN HILANG (%)", 0.0, 5.0, def_d, 0.1)
            laju_a = s2.slider("KECEPATAN HUTAN TUMBUH (%)", 0.0, 5.0, def_a, 0.1)

            a1, a2 = st.columns(2)
            luas_h_input = a1.number_input("LUAS HUTAN AWAL (km²)", min_value=0.0, value=def_forest, step=1000.0)
            luas_l_input = a2.number_input("LUAS DARATAN (km²)", min_value=0.0, value=def_land, step=1000.0)

        st.write("")
        run_btn = st.form_submit_button("JALANKAN SIMULASI", use_container_width=True)

    # Logika proses hasil prediksi
    if run_btn:
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

        # Menampilkan grafik line chart tren target
        with st.container(border=True):
            st.markdown("<div class='header-text'>Prediksi Cadangan Karbon Visual</div>", unsafe_allow_html=True)
            fig_line = go.Figure(go.Scatter(
                x=thn_list, y=hasil_list, mode="lines+markers",
                line=dict(color="#022C22", width=4),
                marker=dict(size=12, color="#FFFFFF", line=dict(color="#022C22", width=3))
            ))
            fig_line.update_layout(**CHART_LAYOUT, xaxis=AX_STYLE, yaxis=AX_STYLE)
            st.plotly_chart(fig_line, use_container_width=True)

            # Penjelasan teks otomatis sesuai pergerakan line
            st.markdown("<div class='header-text' style='margin-top: 1rem;'>Kesimpulan Analisis Simulasi</div>", unsafe_allow_html=True)
            if persentase_perubahan > 0:
                insight_msg = f"Tren Positif: Berdasarkan laju pertumbuhan hutan sebesar {laju_a:.2f}% dan laju kehilangan sebesar {laju_d:.2f}%, stok karbon di {negara} diproyeksikan akan meningkat sebesar {persentase_perubahan:.2f}%. Pada tahun {thn_target}, estimasi total stok karbon akan mencapai {end_carbon:,.0f} Ton."
            elif persentase_perubahan < 0:
                insight_msg = f"Krisis Menurun: Berdasarkan model, laju kehilangan hutan sebesar {laju_d:.2f}% mendominasi pertumbuhan yang hanya {laju_a:.2f}%. Hal ini menyebabkan stok karbon di {negara} diproyeksikan menyusut tajam sebesar {abs(persentase_perubahan):.2f}%. Pada tahun {thn_target}, stok tersisa diperkirakan hanya {end_carbon:,.0f} Ton."
            else:
                insight_msg = f"Stagnan: Kondisi hutan di {negara} diperkirakan stabil tanpa ada perubahan signifikan pada stok karbon hingga tahun {thn_target}, bertahan di angka {end_carbon:,.0f} Ton."

            st.markdown(f"<div class='insight-text'>{insight_msg}</div>", unsafe_allow_html=True)

# ==================== HALAMAN 3: KEBIJAKAN ====================
else:
    with st.container(border=True):
        st.markdown("<div class='title-text'>SIMULATOR ATURAN</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-text'>Coba terapkan kebijakan pada suatu negara dan lihat dampaknya di tahun 2030 berdasarkan baseline data asli.</div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        # Form panel untuk submit kebijakan
        with st.form("form_kebijakan", border=True):
            st.markdown("<div class='header-text'>Panel Kebijakan</div>", unsafe_allow_html=True)
            negara_kebijakan = st.selectbox("PILIH NEGARA UNTUK DITERAPKAN", COUNTRIES)
            st.markdown("<hr style='border:1.5px solid #022C22;'>", unsafe_allow_html=True)
            
            p1 = st.toggle("STOP TEBANG POHON KOMERSIAL")
            p2 = st.toggle("TAMBAH DANA REBOISASI")
            p3 = st.toggle("HUKUM TEGAS BAKAR HUTAN")
            p4 = st.toggle("BERIKAN INSENTIF PETANI")
            
            st.write("")
            run_pol = st.form_submit_button("TERAPKAN ATURAN", use_container_width=True)

    with col_r:
        if run_pol:
            base_data_pol = df[df["Country"] == negara_kebijakan]
            pol_land = float(base_data_pol["Land_Area_km2"].values[0]) if not base_data_pol.empty else 600000.0
            pol_forest = float(base_data_pol[base_data_pol["Year"] == YEAR_MAX]["Forest_Area_km2"].values[0]) if not base_data_pol.empty else 400000.0
            
            bd = float(base_data_pol["Annual_Deforestation_Rate"].mean()) if not base_data_pol.empty else 2.0
            ba = float(base_data_pol["Annual_Afforestation_Rate"].mean()) if not base_data_pol.empty else 0.5

            # Simulasi algoritma perhitungan berdasarkan toggle yang diaktifkan
            kebijakan_diterapkan = []
            if p1: 
                bd *= 0.3
                kebijakan_diterapkan.append("Penghentian tebang komersial mengurangi angka hilangnya hutan secara masif.")
            if p2: 
                ba *= 3.0
                kebijakan_diterapkan.append("Injeksi dana reboisasi memicu peningkatan drastis pada persentase hutan tumbuh.")
            if p3: 
                bd *= 0.8
                kebijakan_diterapkan.append("Ketegasan hukum menekan aktivitas pembakaran liar secara signifikan.")
            if p4: 
                ba *= 1.4; bd *= 0.9
                kebijakan_diterapkan.append("Insentif bagi petani merubah lahan pertanian menjadi area penyangga hijau.")

            h_pol = predict_carbon({
                "Country": negara_kebijakan, "Primary_Driver_of_Change": "None", "Year": 2030, 
                "Forest_Area_km2": pol_forest, "Land_Area_km2": pol_land,
                "Forest_Cover_Pct": (pol_forest / pol_land) * 100 if pol_land > 0 else 0,
                "Annual_Deforestation_Rate": bd, "Annual_Afforestation_Rate": ba
            })
            
            # Kartu hasil dari penerapan kebijakan
            with st.container(border=True):
                st.markdown(f"<div class='header-text'>Proyeksi {negara_kebijakan} (2030)</div>", unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("HUTAN HILANG", f"{bd:.2f}%")
                m2.metric("HUTAN TUMBUH", f"{ba:.2f}%")
                st.metric("ESTIMASI STOK KARBON", f"{h_pol:,.0f} Ton")

                # Format narasi penjelas
                if not kebijakan_diterapkan:
                    penjelasan = "Tidak ada kebijakan baru yang diterapkan. Kondisi lingkungan akan bergerak sesuai rata-rata kebiasaan saat ini."
                else:
                    penjelasan = f"Dampak Kebijakan: {' '.join(kebijakan_diterapkan)} Perubahan ini memproyeksikan perbaikan iklim yang relevan di masa mendatang."
                
                st.markdown(f"<div class='insight-text'>{penjelasan}</div>", unsafe_allow_html=True)
