import streamlit as st
import pandas as pd
import re
import math

# --- Page Configuration ---
st.set_page_config(
    page_title="PRISM MVP",
    page_icon="🚀",
    layout="wide"
)

# --- Clean, Apple-Inspired White Theme CSS ---
st.markdown("""
<style>
/* Base Styles */
html, body, [class*="st-"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    background-color: #FFFFFF; /* White Background */
    color: #212121; /* Dark Grey Text */
}

/* Main App Container */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Headers */
h1, h2, h3 {
    color: #1c1c1e;
    font-weight: 600;
}
h1 { font-size: 2rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.15rem; }

/* Buttons */
.stButton>button {
    border-radius: 10px;
    border: 1px solid #d0d0d5;
    background-color: #f0f0f5;
    color: #1c1c1e;
    padding: 10px 24px;
    font-weight: 500;
    transition: all 0.2s ease-in-out;
}
.stButton>button:hover {
    background-color: #e0e0e5;
    border-color: #c0c0c5;
}

/* Metric Containers */
div[data-testid="stMetric"] {
    background-color: #F9F9F9; /* Off-white for contrast */
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #EAEAEA;
}
div[data-testid="stMetric"] > label {
    font-size: 0.9rem;
    color: #555555;
}
div[data-testid="stMetric"] > div {
    font-size: 1.75rem;
    font-weight: 600;
}

/* Image styling */
.stImage img {
    border-radius: 12px;
    border: 1px solid #EAEAEA;
}

/* Divider */
hr {
    background-color: #EAEAEA;
}
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_data
def load_data(csv_path):
    """Loads and preprocesses product data from a CSV file."""
    try:
        df = pd.read_csv(csv_path)
        # Clean data on load
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
        df['Review'] = pd.to_numeric(df['Review'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        return df
    except FileNotFoundError:
        st.error(f"File not found: {csv_path}. Please ensure 'products.csv' is in your GitHub repository.")
        st.stop()

def get_rating_stars(rating_text: str) -> str:
    """FIXED: Converts rating text into a number and star emojis."""
    if not isinstance(rating_text, str):
        return "N/A"
    
    match = re.search(r'(\d\.\d)', rating_text)
    if not match:
        return "N/A"
        
    rating_num = float(match.group(1))
    full_stars = int(rating_num)
    half_star = "★" if (rating_num - full_stars) >= 0.8 else ("✫" if (rating_num - full_stars) > 0.2 else "")
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    stars = "★" * full_stars + half_star + "☆" * empty_stars
    return f"{rating_num} {stars}"

def clean_sales_text(sales_text: str) -> str:
    """FIXED: Cleans up the monthly sales text to be short and clear."""
    if not isinstance(sales_text, str):
        return "N/A"
    return sales_text.split(" ")[0]

# --- Session State Initialization ---
if 'product_index' not in st.session_state:
    st.session_state.product_index = 0

# --- App Header ---
st.title("PRISM")
st.markdown("Product Research & Insight System")

df = load_data('products.csv')

# --- Main Controls ---
col_nav1, col_nav2 = st.columns([3, 1])
with col_nav1:
    # VISIBLE COUNTER to track progress and debug
    st.caption(f"Showing Product {st.session_state.product_index + 1} of {len(df)}")
with col_nav2:
    if st.button("Discover Next Product →", use_container_width=True):
        st.session_state.product_index = (st.session_state.product_index + 1) % len(df)

st.divider()

# --- Dashboard Layout ---
current_product = df.iloc[st.session_state.product_index]
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.image(current_product.get('Image', ''), use_container_width=True)

with col2:
    st.markdown(f"### {current_product.get('Title', 'No Title Available')}")

    price = current_product.get('Price', 0)
    sales = clean_sales_text(current_product.get('Monthly Sales', 'N/A'))
    rating_str = get_rating_stars(current_product.get('Ratings', 'N/A'))
    reviews = current_product.get('Review', 0)

    st.markdown("---")
    
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric(label="Price", value=f"₹{price:,.0f}")
    metric_col2.metric(label="Monthly Sales", value=sales)
    
    st.markdown("### Rating")
    st.markdown(f"<h2 style='color: #212121; font-weight: 600;'>{rating_str}</h2>", unsafe_allow_html=True)
    st.markdown(f"Based on **{int(reviews):,}** reviews.")

    st.divider()

    st.subheader("PRISM Analysis (Coming Soon)")
    st.info("The 'Identified Item' and 'PRISM Score' will appear here.")
