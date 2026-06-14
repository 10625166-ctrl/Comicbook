import os
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Comic Book Insights",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "page" not in st.session_state:
    st.session_state.page = "intro"

# Try common dataset locations for GitHub/Streamlit deployment
DATASET_FILENAME = "comic_books_10000_dataset.csv"
DATA_PATH_CANDIDATES = []
if os.getenv("COMIC_DATASET_PATH"):
    DATA_PATH_CANDIDATES.append(Path(os.getenv("COMIC_DATASET_PATH")))

DATA_PATH_CANDIDATES.extend([
    Path(__file__).resolve().parent / DATASET_FILENAME,
    Path(__file__).resolve().parent.parent / DATASET_FILENAME,
    Path.cwd() / DATASET_FILENAME,
])

DATA_PATH = next((path for path in DATA_PATH_CANDIDATES if path.exists()), None)

# CSS for background images
intro_bg = """
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, rgba(25, 25, 112, 0.7), rgba(220, 20, 60, 0.7)), 
                    url('https://images.unsplash.com/photo-1604307417808-af0bcb8a90f5?w=1200') center/cover;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
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
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0.05);
    }
    .metric-card {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
    }
    .main-content {
        background-color: rgba(255, 244, 229, 0.92); /* light orange */
        color: #000000;
        padding: 18px;
        border-radius: 10px;
    }
</style>
"""

# Đổi tên hàm thành read_comic_dataset để làm mới cache trên Streamlit Cloud
@st.cache_data
def read_comic_dataset(path: Path) -> pd.DataFrame:
    if path is None or not path.exists():
        looked = "\n".join(str(p) for p in DATA_PATH_CANDIDATES)
        raise FileNotFoundError(
            f"Dataset not found. Searched for {DATASET_FILENAME} in:\n{looked}\n"
            "Make sure the file is included in your repo and the app root, or set COMIC_DATASET_PATH."
        )
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
        <p>Explore trends, top creators, popular genres, and ratings across decades of comic history.</p>
        <p>From classic manga to modern graphic novels, dive into the fascinating world of sequential art.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; margin-top: 60px;'>", unsafe_allow_html=True)
        if st.button("🚀 Let's Start", key="start_btn", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 150px;'></div>", unsafe_allow_html=True)


def get_top_value(series: pd.Series) -> str:
    if series.empty:
        return "Unknown"
    return series.value_counts().idxmax()


def get_top_records(data: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()
    return data.sort_values("Rating (out of 10)", ascending=False).head(n)


def show_dashboard_page(df: pd.DataFrame):
    st.markdown(main_bg, unsafe_allow_html=True)
    
    # Initialize reset counter if not present
    if "reset_count" not in st.session_state:
        st.session_state.reset_count = 0
    
    with st.sidebar:
        st.markdown(
            "<div style='margin:6px 0 12px 0;'><h2 style='font-size:22px; font-weight:800; text-transform:uppercase; margin:0;'>📂 CATEGORIES</h2></div>",
            unsafe_allow_html=True,
        )
        # compute top 10 genres for selection
        top_genres = df["Genre"].value_counts().head(10).index.tolist()
        # compute top 10 countries for selection
        top_countries = df["Country of Origin"].value_counts().head(10).index.tolist()
        # use session-state-backed widgets so Reset can restore defaults
        selected_year = st.selectbox("Release year", ["All"] + sorted(df["Release Year"].unique().tolist()), key=f"selected_year_{st.session_state.reset_count}")
        selected_genre = st.selectbox("Genre", ["All"] + top_genres, key=f"selected_genre_{st.session_state.reset_count}")
        selected_country = st.selectbox("Country", ["All"] + top_countries, key=f"selected_country_{st.session_state.reset_count}")
        selected_rating = st.slider(
            "Rating range",
            float(df["Rating (out of 10)"].min()),
            float(df["Rating (out of 10)"].max()),
            (float(df["Rating (out of 10)"].min()), float(df["Rating (out of 10)"].max())),
            key=f"selected_rating_{st.session_state.reset_count}",
        )

        st.markdown("---")
        if st.button("🔄 Reset", use_container_width=True):
            # Increment reset counter to force widget reinitialization
            st.session_state.reset_count += 1
            st.rerun()

    filtered_df = df.copy()
    if selected_year != "All":
        filtered_df = filtered_df[filtered_df["Release Year"] == selected_year]
    if selected_genre != "All":
        filtered_df = filtered_df[filtered_df["Genre"] == selected_genre]
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["Country of Origin"] == selected_country]
    filtered_df = filtered_df[filtered_df["Rating (out of 10)"].between(*selected_rating)]

    st.title("Comic Book Insights Dashboard")
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    st.markdown(
        "Discover key trends and top creators in the world of comics."
    )

    st.subheader("📊 Headline Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Comics", len(filtered_df), f"/ {len(df)}")
    
    # Check if filtered_df is empty to avoid Mean of empty series warning/error
    avg_rating = filtered_df['Rating (out of 10)'].mean() if not filtered_df.empty else 0.0
    col2.metric("Avg Rating", f"{avg_rating:.2f}")
    
    col3.metric("Top Genre", get_top_value(filtered_df["Genre"]))
    col4.metric("Top Country", get_top_value(filtered_df["Country of Origin"]))

    st.markdown("---")

    st.subheader("📰 Key Findings")
    most_active_writer = get_top_value(filtered_df["Writer"])
    most_common_format = get_top_value(filtered_df["Format"])
    average_pages = int(filtered_df["Page Count"].mean()) if not filtered_df.empty else 0

    col_text1, col_text2, col_text3 = st.columns(3)
    with col_text1:
        st.info(f"📅 **{filtered_df['Release Year'].nunique()}** years represented, avg **{average_pages}** pages")
    with col_text2:
        st.info(f"✍️ **{most_active_writer}** is the most prolific writer")
    with col_text3:
        st.info(f"📚 **{filtered_df['Language'].nunique()}** languages in database")

    st.markdown("---")

    st.subheader("📈 Visual Analysis")
    if not filtered_df.empty:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("**Comics by Release Year**")
            year_counts = filtered_df["Release Year"].value_counts().sort_index()
            if not year_counts.empty:
                st.bar_chart(year_counts)
                st.markdown("""
                *This chart shows the distribution of comics across different decades. The data reveals publication trends and 
                the evolution of the comic book industry over time.*
                """)

            st.markdown("**Top Genres**")
            genre_counts = filtered_df["Genre"].value_counts().head(10)
            if not genre_counts.empty:
                st.bar_chart(genre_counts)
                st.markdown("""
                *Genre preferences show what types of stories readers and creators favor. 
                Superhero and action genres tend to dominate, but drama and slice-of-life content is also significant.*
                """)

        with chart_col2:
            st.markdown("**Country of Origin Distribution**")
            country_counts = filtered_df["Country of Origin"].value_counts().head(10)
            if not country_counts.empty:
                st.bar_chart(country_counts)
                st.markdown("""
                *Comics originate from many countries worldwide. Japan dominates with manga, 
                while the USA produces major mainstream comics. Other countries contribute unique cultural perspectives.*
                """)

    else:
        st.warning("No data available for charts with current filters.")

    st.markdown("---")

    st.subheader("⭐ Top Comics to Highlight")
    if filtered_df.empty:
        st.write("No comics match the current filters.")
    else:
        top_comics = get_top_records(filtered_df, 10)
        st.write(top_comics[["Title", "Writer", "Genre", "Release Year", "Rating (out of 10)", "Country of Origin"]].reset_index(drop=True))

    st.markdown("</div>", unsafe_allow_html=True)


# Load data using the newly-named cached function
try:
    df = read_comic_dataset(DATA_PATH)
    if st.session_state.page == "intro":
        show_intro_page()
    else:
        show_dashboard_page(df)
except Exception as error:
    st.error(f"Error loading dataset: {error}")
    st.stop()
