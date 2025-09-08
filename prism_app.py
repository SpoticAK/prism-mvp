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

# --- Apple-Inspired CSS Styling ---
# This CSS block is injected into the app to override default styles.
st.markdown("""
<style>
/* Base Styles */
html, body, [class*="st-"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    background-color: #1C1C1E; /* Apple's Dark Grey */
    color: #F2F2F7;
}

/* Main App Container */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Headers */
h1, h2, h3 {
    color: #FFFFFF;
    font-weight: 600;
}
h1 { font-size: 2.2rem; }
h2 { font-size: 1.6rem; }
h3 { font-size: 1.25rem; }

/* Buttons */
.stButton>button {
    border-radius: 12px;
    border: 2px solid #0A84FF;
    background-color: transparent;
    color: #0A84FF;
    padding: 10px 24px;
    font-weight: 600;
    transition: all 0.2s ease-in-out;
}
.stButton>button:hover {
    background-color: #0A84FF;
    color: #FFFFFF;
}

/* Metric Containers */
div[data-testid="stMetric"] {
    background-color: #2C2C2E; /* Slightly Lighter Grey */
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
div[data-testid="stMetric"] > label {
    font-size: 1rem;
    color: #8E8E93; /* Subtle Grey for Labels */
}
div[data-testid="stMetric"] > div {
    font-size: 2rem;
    font-weight: 700;
}

/* Image styling */
.stImage img {
    border-radius: 15px;
}

/* Divider */
hr {
    background-color: #3A3A3C;
}
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_data
def load_data(csv_path):
    """Loads product data from a CSV file."""
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError:
        st.error(f"File not found: {csv_path}. Please ensure 'products.csv' is in your GitHub repository.")
        st.stop()

def get_rating_stars(rating_text: str) -> str:
    """Converts rating text (e.g., '4.2 out of 5 stars') into a number and star emojis."""
    if not isinstance(rating_text, str):
        return "N/A"
    
    # Use regex to find the first floating-point number
    match = re.search(r'\\d+\\.\\d+', rating_text)
    if not match:
        return "N/A"
        
    rating_num = float(match.group())
    
    full_stars = math.floor(rating_num)
    # Simplified star logic for now
    half_star = "★" if (rating_num - full_stars) >= 0.5 else "☆"
    empty_stars = 5 - full_stars - 1
    
    stars_display = "★" * full_stars + half_star + "☆" * empty_stars
    return f"{rating_num} {stars_display}"

# --- Session State ---
if 'product_index' not in st.session_state:
    st.session_state.product_index = 0

# --- App Header ---
st.title("PRISM")
st.markdown("Product Research & Insight System")

df = load_data('products.csv')

# --- Main Controls ---
col_nav1, col_nav2, col_nav3 = st.columns([1,2,1])
with col_nav2:
    if st.button("Discover Next Product →", use_container_width=True):
        st.session_state.product_index = (st.session_state.product_index + 1) % len(df)

st.divider()

# --- Dashboard Layout ---
current_product = df.iloc[st.session_state.product_index]
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    # **FIXED**: Changed use_column_width to use_container_width
    st.image(current_product.get('Image', ''), use_container_width=True)

with col2:
    st.subheader("Product Details")
    st.markdown(f"### {current_product.get('Title', 'No Title Available')}")

    price = current_product.get('Price', 'N/A')
    sales = current_product.get('Monthly Sales', 'N/A')
    rating_str = get_rating_stars(current_product.get('Ratings', 'N/A'))
    reviews = current_product.get('Review', 'N/A')

    st.markdown("---")
    
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric(label="Price", value=f"₹{price}")
    metric_col2.metric(label="Monthly Sales", value=str(sales))
    
    st.markdown("### Rating")
    st.markdown(f"<h2 style='color: #F2F2F7; font-weight: 700;'>{rating_str}</h2>", unsafe_allow_html=True)
    st.markdown(f"Based on **{reviews}** reviews.")

    st.divider()

    st.subheader("PRISM Analysis (Coming Soon)")
    st.info("The 'Identified Item' and 'PRISM Score' will appear here.")
    
