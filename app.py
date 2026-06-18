import os
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Comic Book Insights",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "page" not in st.session_state:
    st.session_state.page = "intro"

# Cấu hình đường dẫn dữ liệu
DATASET_FILENAME = "comic_books_10000_dataset.csv"
DATA_PATH_CANDIDATES = [
    Path(__file__).resolve().parent / DATASET_FILENAME,
    Path(__file__).resolve().parent.parent / DATASET_FILENAME,
    Path.cwd() / DATASET_FILENAME,
]
DATA_PATH = next((path for path in DATA_PATH_CANDIDATES if path.exists()), None)

# CSS giao diện nền và Tab vuông đen chữ trắng
main_bg = """
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, rgba(255,244,229,0.95), rgba(255,236,210,0.95)),
                    url('https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1200') center/cover;
        background-attachment: fixed;
    }
    .main-content {
        background-color: rgba(255, 244, 229, 0.92);
        color: #000000;
        padding: 20px;
        border-radius: 10px;
    }
    div.stTabs [data-baseweb="tab"] {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 0px !important;
        padding: 8px 16px !important;
        margin-right: 6px;
        font-weight: bold;
        border: none !important;
        text-transform: uppercase;
        font-size: 13px;
    }
    div.stTabs [data-baseweb="tab"]:hover {
        background-color: #ff4b4b !important;
    }
    div.stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #111111 !important;
        color: #ff4b4b !important;
        border-bottom: 3px solid #ff4b4b !important;
    }
</style>
"""

intro_bg = """
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, rgba(25, 25, 112, 0.7), rgba(220, 20, 60, 0.7)), 
                    url('https://images.unsplash.com/photo-1604307417808-af0bcb8a90f5?w=1200') center/cover;
        background-attachment: fixed;
    }
</style>
"""

@st.cache_data
def read_comic_dataset(path: Path) -> pd.DataFrame:
    if path is None or not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu {DATASET_FILENAME}")
    df = pd.read_csv(path)
    df = df.fillna("Unknown")
    
    # SỬA LỖI TRÙNG LẶP: Loại bỏ khoảng trắng thừa ở đầu/cuối của text để gom nhóm chính xác
    if "Country of Origin" in df.columns:
        df["Country of Origin"] = df["Country of Origin"].astype(str).str.strip()
    if "Genre" in df.columns:
        df["Genre"] = df["Genre"].astype(str).str.strip()
        
    return df

def show_intro_page():
    st.markdown(intro_bg, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: white; font-size: 60px; margin-top: 100px;'>📚 Comic Book Insights</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #FFD700; font-size: 24px; margin-top: 30px;'>Explore the World of Comics</h2>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: white; font-size: 18px; margin-top: 40px; line-height: 1.8;'>
        <p>Discover insights from a comprehensive dataset of 10,000 comic books.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Let's Start", key="start_btn", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

def get_top_value(series: pd.Series) -> str:
    return "Unknown" if series.empty else series.value_counts().idxmax()

def show_dashboard_page(df: pd.DataFrame):
    st.markdown(main_bg, unsafe_allow_html=True)
    
    if "reset_count" not in st.session_state:
        st.session_state.reset_count = 0
        
    # --- THANH SIDEBAR: CATEGORIES ---
    with st.sidebar:
        st.markdown("<div style='margin:6px 0 12px 0;'><h2 style='font-size:22px; font-weight:800; text-transform:uppercase; margin:0;'>📂 CATEGORIES</h2></div>", unsafe_allow_html=True)
        
        available_years = sorted([int(x) for x in df["Release Year"].unique() if str(x).isdigit()])
        
        # Lấy danh sách nước sau khi đã làm sạch và chuẩn hóa (Không còn bị lặp)
        top_countries = df["Country of Origin"].value_counts().head(10).index.tolist()
        
        selected_years = st.multiselect("Release Year(s)", options=available_years, default=available_years, key=f"years_{st.session_state.reset_count}")
        selected_countries = st.multiselect("Country of Origin", options=top_countries, default=top_countries, key=f"countries_{st.session_state.reset_count}")
        
        selected_rating = st.slider(
            "Rating range",
            float(df["Rating (out of 10)"].min()),
            float(df["Rating (out of 10)"].max()),
            (float(df["Rating (out of 10)"].min()), float(df["Rating (out of 10)"].max())),
            key=f"rating_{st.session_state.reset_count}",
        )
        
        st.markdown("---")
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.session_state.reset_count += 1
            st.rerun()

    # Lọc dữ liệu dựa trên Categories đầu vào
    filtered_df = df.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df["Release Year"].isin(selected_years)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df["Country of Origin"].isin(selected_countries)]
    filtered_df = filtered_df[filtered_df["Rating (out of 10)"].between(*selected_rating)]

    st.title("Comic Book Insights Dashboard")
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)

    # --- MỤC KEY FINDINGS: ĐOẠN VĂN MIÊU TẢ DATASET ---
    st.subheader("📰 Key Findings & Dataset Overview")
    total_records = len(filtered_df)
    avg_rating = filtered_df['Rating (out of 10)'].mean() if not filtered_df.empty else 0.0
    most_prolific_writer = get_top_value(filtered_df["Writer"])
    dominant_format = get_top_value(filtered_df["Format"])
    avg_pages = int(filtered_df["Page Count"].mean()) if not filtered_df.empty else 0
    unique_langs = filtered_df['Language'].nunique()

    st.write(
        f"This comprehensive dataset encompasses a rigorous compilation of comic books, providing an analytical window into global sequential art trends. "
        f"Currently, under the active filter configuration, the dataset contains **{total_records:,} distinct titles** spanning **{filtered_df['Release Year'].nunique()} individual publication years**. "
        f"The registered entries exhibit a commendable critical standard with an **average user rating of {avg_rating:.2f} out of 10**. "
        f"Structurally, the marketplace demonstrates a heavy reliance on the **{dominant_format}** format, while the technical composition shows an average volume size of **{avg_pages} pages** per book. "
        f"Linguistically and creatively, production exhibits vast diversity across **{unique_langs} distinct languages**, driven heavily by prolific creators such as **{most_prolific_writer}**, who emerges as a highly prominent figurehead within this cultural dataset."
    )

    st.markdown("---")
    st.subheader("📈 Visual Analysis & Statistical Breakdowns")

    # --- TÁCH BIỆT 4 CHART THÀNH CÁC TABS RIÊNG ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Comics by Release Year", 
        "🌍 Country of Origin Distribution", 
        "🧬 Top Genres", 
        "📋 Data Frame"
    ])

    if not filtered_df.empty:
        
        # --- TAB 1: COMICS BY RELEASE YEAR ---
        with tab1:
            col_chart, col_desc = st.columns([1.3, 1])
            with col_chart:
                year_counts = filtered_df["Release Year"].value_counts().sort_index().reset_index()
                year_counts.columns = ['Release Year', 'Comics Count']
                year_counts['Release Year'] = year_counts['Release Year'].astype(str)
                
                is_single_year = len(year_counts) <= 3
                fig_line = px.line(
                    year_counts, x='Release Year', y='Comics Count',
                    markers=True, title="Chronological Publication Volumes"
                )
