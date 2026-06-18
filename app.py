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

# CSS giao diện nền
intro_bg = """
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, rgba(25, 25, 112, 0.7), rgba(220, 20, 60, 0.7)), 
                    url('https://images.unsplash.com/photo-1604307417808-af0bcb8a90f5?w=1200') center/cover;
        background-attachment: fixed;
    }
</style>
"""

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
    /* Định dạng Tab vuông đen chữ trắng chuẩn theo Hình số 2 */
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

@st.cache_data
def read_comic_dataset(path: Path) -> pd.DataFrame:
    if path is None or not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu {DATASET_FILENAME}")
    df = pd.read_csv(path)
    df = df.fillna("Unknown")
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
        
    # --- THANH SIDEBAR: CATEGORIES (XÓA GENRE, DÙNG MULTISELECT ĐỂ CHỌN NHIỀU NĂM/NƯỚC) ---
    with st.sidebar:
        st.markdown("<div style='margin:6px 0 12px 0;'><h2 style='font-size:22px; font-weight:800; text-transform:uppercase; margin:0;'>📂 CATEGORIES</h2></div>", unsafe_allow_html=True)
        
        available_years = sorted([int(x) for x in df["Release Year"].unique() if str(x).isdigit()])
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

    # Lọc dữ liệu dựa trên bộ lọc
    filtered_df = df.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df["Release Year"].isin(selected_years)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df["Country of Origin"].isin(selected_countries)]
    filtered_df = filtered_df[filtered_df["Rating (out of 10)"].between(*selected_rating)]

    st.title("Comic Book Insights Dashboard")
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)

    # --- MỤC KEY FINDINGS: ĐOẠN VĂN MIÊU TẢ DATASET RÕ RÀNG NHẤT ---
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

    # --- TÁCH BIỆT 4 CHART THÀNH CÁC TABS RIÊNG (HÌNH SỐ 2) ---
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
                    f"* **Sự thay đổi lớn nhất:** Số lượng truyện xuất bản tăng vọt đột biến bắt đầu từ sau năm 2010.\n"
                    f"* **Điểm cao nhất:** Đạt đỉnh kỷ lục vào giai đoạn gần đây trước khi có dấu hiệu đi ngang nhẹ.\n"
                    f"* **Giai đoạn thấp nhất:** Các năm đầu thập niên 2000 duy trì lượng xuất bản ở mức thấp và ổn định."
                )
                st.markdown("### ✨ Why it is compelling?")
                st.write("Biểu đồ phản ánh rõ nét sự bùng nổ của văn hóa đại chúng kết hợp với sự phát triển mạnh mẽ của các nền tảng phân phối số hóa toàn cầu.")

        # --- TAB 2: COUNTRY OF ORIGIN DISTRIBUTION (HIỂN THỊ ĐỦ NƯỚC + FIX LỖI CHE CHỮ) ---
        with tab2:
            col_chart, col_desc = st.columns([1.3, 1])
            with col_chart:
                country_all = filtered_df["Country of Origin"].value_counts().reset_index()
                country_all.columns = ['Country', 'Count']
                
                # Giữ lại đúng 9 nước lớn nhất, gom các nước còn lại thành "Others" để biểu đồ tròn hiển thị chuẩn xác 10 phần
                if len(country_all) > 9:
                    top_9 = country_all.head(9)
                    others_count = country_all.iloc[9:]['Count'].sum()
                    others_df = pd.DataFrame([['Others', others_count]], columns=['Country', 'Count'])
                    country_counts = pd.concat([top_9, others_df], ignore_index=True)
                else:
                    country_counts = country_all
                
                fig_pie = px.pie(
                    country_counts, values='Count', names='Country',
                    title="Geographical Market Share Breakdown (Top Countries)",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                # Đẩy chữ ra ngoài rìa, hiển thị rõ ràng Tên nước + Phần trăm theo đường chỉ dẫn
                fig_pie.update_traces(
                    textposition='outside', 
                    textinfo='label+percent',
                    automargin=True
                )
                # Tăng biên rộng (margin) và chiều cao (height) để đường chỉ có khoảng không gian bung ra, không bị che mất chữ
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    showlegend=False,
                    margin=dict(t=80, b=80, l=120, r=120),
                    height=520
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_desc:
                st.markdown("### 🎯 Key Observations")
                top_1 = country_counts.iloc[0]['Country'] if len(country_counts) > 0 else "N/A"
                top_2 = country_counts.iloc[1]['Country'] if len(country_counts) > 1 else "N/A"
                st.markdown(
                    f"* **Thị phần lớn nhất:** Đứng đầu bảng xếp hạng hoàn toàn thuộc về **{top_1}** và **{top_2}**.\n"
                    f"* **Sự chênh lệch:** Hai quốc gia dẫn đầu chiếm phần lớn miếng bánh thị trường, tạo khoảng cách cực lớn với nhóm còn lại.\n"
                    f"* **Phân khúc thấp nhất:** Các nước châu Âu và khu vực khác giữ tỷ trọng rất nhỏ, phân bố rải rác."
                )
                st.markdown("### ✨ Why it is compelling?")
                st.write("Biểu đồ này vạch rõ thế độc quyền văn hóa độc đáo trong ngành truyện tranh toàn cầu: nơi độc giả bị chi phối chủ yếu bởi hai phong cách sáng tác lớn.")

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
                    f"* **Thể loại phổ biến nhất:** Thể loại **{top_g}** chiếm vị trí áp đảo tuyệt đối về số lượng tác phẩm.\n"
                    f"* **Xu hướng thị trường:** Nhóm nội dung mang tính giải trí cao (Action/Sci-Fi/Fantasy) đứng vững ở nhóm trên cùng.\n"
                    f"* **Điểm thấp nhất trong Top 10:** Các thể loại kén người đọc như đời thường hay chính kịch có thị phần khiêm tốn hơn hẳn."
                )
                st.markdown("### ✨ Why it is compelling?")
                st.write("Chứng minh bằng số liệu thực tế về thị hiếu của độc giả: Các yếu tố giả tưởng kỳ ảo luôn là thỏi nam châm giữ chân người xem trung thành nhất.")

        # --- TAB 4: DATA FRAME (CHO TOP COMICS TO HIGHLIGHT - KHÔNG CÓ MIÊU TẢ) ---
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
