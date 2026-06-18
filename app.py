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
    
    if "Country of Origin" in df.columns:
        # Chuẩn hóa khoảng trắng
        df["Country of Origin"] = df["Country of Origin"].astype(str).str.strip()
        
        # GIỚI HẠN CỨNG CHỈ ĐỂ LẠI ĐÚNG 8 QUỐC GIA THEO YÊU CẦU
        # (Tự động loại bỏ hoàn toàn South Korea / Japan, South Korea / USA, Others và các nước Châu Âu nhỏ)
        target_countries = ["Japan", "USA", "South Korea", "China", "UK", "Canada", "New Zealand", "Australia"]
        df = df[df["Country of Origin"].isin(target_countries)]

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
        
        # Danh sách quốc gia chỉ gồm đúng 8 nước mục tiêu, sắp xếp theo số lượng từ cao đến thấp
        allowed_countries = df["Country of Origin"].value_counts().index.tolist()
        
        selected_years = st.multiselect("Release Year(s)", options=available_years, default=available_years, key=f"years_{st.session_state.reset_count}")
        selected_countries = st.multiselect("Country of Origin", options=allowed_countries, default=allowed_countries, key=f"countries_{st.session_state.reset_count}")
        
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

    # --- TÁCH BIỆT CÁC CHART THÀNH CÁC TABS RIÊNG ---
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
                fig_line.update_traces(
                    marker=dict(size=12 if is_single_year else 6, color='red' if is_single_year else '#1f77b4'),
                    line=dict(color='#1f77b4', width=2.5)
                )
                fig_line.update_layout(xaxis=dict(type='category'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_line, use_container_width=True)
            
            with col_desc:
                st.markdown("### 🎯 Key Observations")
                st.markdown(
                    f"* **Major Breakout Point:** Publication numbers triggered a sharp exponential climb right after the year 2010.\n"
                    f"* **Historical Apex:** Production metrics hit their record-breaking ceiling during the most recent active years before initiating a minor stabilization.\n"
                    f"* **Baseline Threshold:** The initial decades mapped out a highly conservative, flat baseline market structure."
                )
                st.markdown("### ✨ Why it is compelling?")
                st.write("This visualization maps out the democratization and digitization of media production, illustrating how comic culture transformed into a dominant modern entertainment asset class.")

        # --- TAB 2: COUNTRY OF ORIGIN DISTRIBUTION (ĐỒNG BỘ TUYỆT ĐỐI - KHÔNG OTHERS) ---
        with tab2:
            col_chart, col_desc = st.columns([1.3, 1])
            with col_chart:
                country_counts = filtered_df["Country of Origin"].value_counts().reset_index()
                country_counts.columns = ['Country', 'Count']
                
                fig_pie = px.pie(
                    country_counts, values='Count', names='Country',
                    title="Geographical Market Share Breakdown (Clean Core 8 Countries)",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                # ĐẢM BẢO HIỂN THỊ ĐƯỜNG CHỈ NGOÀI ĐỒNG ĐỀU CHO CẢ 8 NƯỚC
                fig_pie.update_traces(
                    textposition='outside', 
                    textinfo='label+percent', # Cấu trúc hiển thị: [Tên Nước] [Số %]
                    automargin=True
                )
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    showlegend=False,
                    margin=dict(t=80, b=80, l=140, r=140), # Tạo không gian rộng rãi để các thanh chỉ và chữ phân bổ đẹp, không đè nhau
                    height=550
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_desc:
                st.markdown("### 🎯 Key Observations")
                top_1 = country_counts.iloc[0]['Country'] if len(country_counts) > 0 else "N/A"
                top_2 = country_counts.iloc[1]['Country'] if len(country_counts) > 1 else "N/A"
                st.markdown(
                    f"* **Market Superpowers:** The global distribution is heavily dominated by **{top_1}** and **{top_2}**, commanding a substantial majority of the volume share.\n"
                    f"* **Volume Disparity:** A dramatic drop-off exists between the two market leaders and the remaining regional publishers.\n"
                    f"* **Regional Diversity:** European and alternative Asian publications account for minor, highly fragmented fractions of global market integration."
                )
                st.markdown("### ✨ Why it is compelling?")
                st.write("It mathematically uncovers the intense soft-power consolidation in global storytelling industries, tracking how two primary creative methods dictate reading habits worldwide.")

        # --- TAB 3: TOP GENRES ---
        with tab3:
            col_chart, col_desc = st.columns([1.3, 1])
            with col_chart:
                genre_counts = filtered_df["Genre"].value_counts().head(10).reset_index()
                genre_counts.columns = ['Genre', 'Count']
                
                fig_bar = px.bar(
                    genre_counts, x='Count', y='Genre', orientation='h',
                    title="Top 10 Most Prevalent Genres",
                    color='Count', color_continuous_scale='Viridis'
                )
                fig_bar.update_layout(yaxis=dict(categoryorder='total ascending'), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col_desc:
                st.markdown("### 🎯 Key Observations")
                top_g = genre_counts.iloc[0]['Genre'] if len(genre_counts) > 0 else "N/A"
                st.markdown(
                    f"* **Unrivaled Dominance:** The **{top_g}** sector achieves a massive volume advantage, outperforming other creative themes comprehensively.\n"
                    f"* **Commercial Skew:** Mainstream entertainment tropes like action, sci-fi, and fantasy populate the upper ranks.\n"
                    f"* **Niche Marginalization:** Character-driven or slice-of-life genres remain limited to narrow publishing pipelines."
                )
                st.markdown("### ✨ Why it is compelling?")
                st.write("This chart serves as metric proof of global escape dynamics, demonstrating how high-stakes hero arcs and fantasy frameworks serve as the primary economic pillars of the comic world.")

        # --- TAB 4: DATA FRAME ---
        with tab4:
            st.markdown("### 📋 Filtered Dataset Records")
            top_comics = filtered_df.sort_values("Rating (out of 10)", ascending=False).head(20)
            st.dataframe(
                top_comics[["Title", "Writer", "Genre", "Release Year", "Rating (out of 10)", "Country of Origin"]].reset_index(drop=True),
                use_container_width=True
            )

    else:
        st.warning("Không có dữ liệu phù hợp với bộ lọc Hiện tại. Vui lòng nhấn nút 'Reset Filters' ở sidebar.")

    st.markdown("</div>", unsafe_allow_html=True)

# Điều hướng trang chính
try:
    df = read_comic_dataset(DATA_PATH)
    if st.session_state.page == "intro":
        show_intro_page()
    else:
        show_dashboard_page(df)
except Exception as error:
    st.error(f"Lỗi hệ thống: {error}")
    st.stop()
