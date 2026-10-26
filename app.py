import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

# KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Dashboard Penjualan Superstore",
    layout="wide",
)


# PALET WARNA (pink pastel)
PINK = "#E75480"        
PINK_MUDA = "#F7A1C4"   
LAVENDER = "#B79CD9"    
MAUVE = "#9C6B98"       
PEACH = "#F6C1B0"       
TEKS = "#5A3A4A"        
LATAR = "#FFF7FA"       
LATAR_KARTU = "#FFFFFF"
GARIS = "#F6D5E2"

PALET_CHART = [PINK, LAVENDER, PINK_MUDA, PEACH, MAUVE]


# CSS CUSTOM
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, p, label, span, div {{
    font-family: 'Quicksand', sans-serif;
}}

/* Latar halaman & sidebar */
.stApp {{
    background-color: {LATAR};
    color: {TEKS};
}}
header[data-testid="stHeader"] {{
    background: transparent;
}}
section[data-testid="stSidebar"] {{
    background-color: #FCE4EC;
    border-right: 1px solid {GARIS};
}}

/* Judul */
h1, h2, h3 {{
    color: {TEKS} !important;
    font-family: 'Quicksand', sans-serif !important;
    font-weight: 700 !important;
}}
h1 {{ color: {PINK} !important; }}

/* Kartu KPI */
.kpi-card {{
    background: {LATAR_KARTU};
    border: 1px solid {GARIS};
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(231, 84, 128, 0.08);
}}
.kpi-label {{
    font-size: 0.85rem;
    color: #A0758A;
    font-weight: 600;
    margin-bottom: 4px;
}}
.kpi-value {{
    font-size: 1.6rem;
    color: {PINK};
    font-weight: 700;
}}

/* Bungkus chart */
div[data-testid="stPlotlyChart"] {{
    background: {LATAR_KARTU};
    border: 1px solid {GARIS};
    border-radius: 18px;
    padding: 10px;
    box-shadow: 0 4px 14px rgba(231, 84, 128, 0.06);
}}

/* Tag di multiselect */
span[data-baseweb="tag"] {{
    background-color: {PINK_MUDA} !important;
    color: {TEKS} !important;
    border-radius: 10px !important;
}}

/* Garis pemisah */
hr {{
    border-color: {GARIS} !important;
}}

/* Expander */
details {{
    background: {LATAR_KARTU};
    border: 1px solid {GARIS} !important;
    border-radius: 14px !important;
}}
</style>
""",
    unsafe_allow_html=True,
)

# Template plotly untuk semua chart
pio.templates["girlie"] = pio.templates["plotly_white"]
pio.templates["girlie"].layout.update(
    font=dict(family="Quicksand, sans-serif", color=TEKS),
    colorway=PALET_CHART,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="#F9E1EA", zerolinecolor=GARIS),
    yaxis=dict(gridcolor="#F9E1EA", zerolinecolor=GARIS),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        title_text="",
    ),
    margin=dict(l=10, r=10, t=40, b=10),
)
pio.templates.default = "girlie"



# LOAD & PERSIAPAN DATA
@st.cache_data
def load_data():
    df = pd.read_csv("SuperStore_Cleaned.csv")

    # Rapikan nama kolom pertama yang rusak (sisa formula Excel)
    df = df.rename(columns={df.columns[0]: "Row ID"})

    # Ubah kolom tanggal (format dd-mm-yyyy) ke datetime
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y", errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y", errors="coerce")

    # Kolom bantu
    df["Bulan"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Diretur"] = (df["Returns"] == "Yes").astype(int)
    return df


df = load_data()



# JUDUL & DESKRIPSI
st.title("Dashboard Penjualan Superstore 2019–2020")
st.markdown(
    """
Dashboard ini menampilkan performa penjualan sebuah superstore di Amerika Serikat
selama **2019–2020**. Gunakan filter di sidebar untuk melihat penjualan, profit,
dan retur berdasarkan periode, wilayah, kategori produk, dan segmen pelanggan.

*Sumber data: Kaggle – Superstore Sales Dataset.*
"""
)



# FILTER INTERAKTIF (SIDEBAR)
st.sidebar.header("Filter Data")

tgl_min = df["Order Date"].min().date()
tgl_max = df["Order Date"].max().date()
rentang = st.sidebar.date_input(
    "Rentang Tanggal Order",
    value=(tgl_min, tgl_max),
    min_value=tgl_min,
    max_value=tgl_max,
)

region = st.sidebar.multiselect(
    "Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique())
)
kategori = st.sidebar.multiselect(
    "Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique())
)
segmen = st.sidebar.multiselect(
    "Segment", sorted(df["Segment"].unique()), default=sorted(df["Segment"].unique())
)

# date_input bisa mengembalikan 1 tanggal saat user baru memilih tanggal awal
if isinstance(rentang, (list, tuple)) and len(rentang) == 2:
    tgl_awal, tgl_akhir = rentang
else:
    tgl_awal, tgl_akhir = tgl_min, tgl_max

dff = df[
    (df["Order Date"].dt.date >= tgl_awal)
    & (df["Order Date"].dt.date <= tgl_akhir)
    & (df["Region"].isin(region))
    & (df["Category"].isin(kategori))
    & (df["Segment"].isin(segmen))
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Menampilkan **{len(dff):,}** dari {len(df):,} baris data")

if dff.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Silakan ubah filter.")
    st.stop()



# KPI
total_sales = dff["Sales"].sum()
total_profit = dff["Profit"].sum()
profit_margin = total_profit / total_sales * 100 if total_sales else 0
total_order = dff["Order ID"].nunique()
return_rate = dff["Diretur"].mean() * 100


def kartu_kpi(kolom, label, nilai):
    kolom.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{nilai}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


k1, k2, k3, k4, k5 = st.columns(5)
kartu_kpi(k1, "Total Sales", f"${total_sales:,.0f}")
kartu_kpi(k2, "Total Profit", f"${total_profit:,.0f}")
kartu_kpi(k3, "Profit Margin", f"{profit_margin:.1f}%")
kartu_kpi(k4, "Jumlah Order", f"{total_order:,}")
kartu_kpi(k5, "Return Rate", f"{return_rate:.1f}%")

st.markdown("---")



# VISUALISASI

# 1. LINE CHART – Tren Sales & Profit per Bulan
st.subheader("Tren Sales & Profit per Bulan")
tren = dff.groupby("Bulan")[["Sales", "Profit"]].sum().reset_index()
fig_line = px.line(
    tren,
    x="Bulan",
    y=["Sales", "Profit"],
    markers=True,
    color_discrete_map={"Sales": PINK, "Profit": LAVENDER},
    labels={"value": "Jumlah (USD)", "Bulan": "Bulan", "variable": "Metrik"},
)
fig_line.update_traces(line=dict(width=3), marker=dict(size=7))
fig_line.update_layout(hovermode="x unified")
st.plotly_chart(fig_line, width="stretch")

col1, col2 = st.columns(2)

# 2. BAR CHART – Profit per Sub-Category
with col1:
    st.subheader("Profit per Sub-Category")
    sub = dff.groupby("Sub-Category")["Profit"].sum().sort_values().reset_index()
    sub["Status"] = sub["Profit"].apply(lambda x: "Rugi" if x < 0 else "Untung")
    fig_bar = px.bar(
        sub,
        x="Profit",
        y="Sub-Category",
        orientation="h",
        color="Status",
        color_discrete_map={"Untung": PINK, "Rugi": MAUVE},
        labels={"Profit": "Total Profit (USD)", "Sub-Category": ""},
    )
    fig_bar.update_traces(marker_line_width=0)
    fig_bar.update_layout(height=500)
    st.plotly_chart(fig_bar, width="stretch")

# 3. PIE CHART – Porsi Sales per Payment Mode
with col2:
    st.subheader("Porsi Sales per Metode Pembayaran")
    pay = dff.groupby("Payment Mode")["Sales"].sum().reset_index()
    fig_pie = px.pie(
        pay,
        names="Payment Mode",
        values="Sales",
        hole=0.45,
        color_discrete_sequence=[PINK, LAVENDER, PINK_MUDA],
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        marker=dict(line=dict(color="#FFFFFF", width=3)),
    )
    fig_pie.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_pie, width="stretch")

col3, col4 = st.columns(2)

# 4. SCATTER PLOT – Sales vs Profit
with col3:
    st.subheader("Hubungan Sales vs Profit")
    fig_scatter = px.scatter(
        dff,
        x="Sales",
        y="Profit",
        color="Category",
        color_discrete_sequence=[PINK, LAVENDER, PEACH],
        hover_data=["Sub-Category", "Product Name"],
        opacity=0.7,
        labels={"Sales": "Sales (USD)", "Profit": "Profit (USD)"},
    )
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="#C9A3B5")
    st.plotly_chart(fig_scatter, width="stretch")

# 5. HEATMAP – Profit per Region x Category
with col4:
    st.subheader("Heatmap Profit: Region × Category")
    pivot = dff.pivot_table(
        index="Region", columns="Category", values="Profit", aggfunc="sum", fill_value=0
    )
    fig_heat = px.imshow(
        pivot,
        text_auto=",.0f",
        # ungu = rugi, putih = impas, pink = untung
        color_continuous_scale=[[0, MAUVE], [0.5, "#FFFFFF"], [1, PINK]],
        color_continuous_midpoint=0,
        aspect="auto",
        labels={"color": "Profit (USD)"},
    )
    st.plotly_chart(fig_heat, width="stretch")



# TABEL DATA
with st.expander("Lihat data hasil filter"):
    st.dataframe(dff.drop(columns=["Bulan", "Diretur"]), width="stretch")

st.caption("Tugas Metode Visualisasi Data – Dashboard Streamlit")