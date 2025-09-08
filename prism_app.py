import streamlit as st
import pandas as pd
import re
import math
import urllib.parse
from item_identifier import ItemIdentifier # <-- IMPORT OUR NEW ENGINE

# --- Page Configuration ---
st.set_page_config(
    page_title="PRISM MVP",
    page_icon="🚀",
    layout="wide"
)

# --- Apple-Inspired CSS Styling ---
st.markdown("""
<style>
/* (The CSS code is the same as before, so it's hidden for brevity) */
html, body, [class*="st-"] { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #FFFFFF; color: #212121; }
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
h1, h2, h3 { color: #1c1c1e; font-weight: 600; }
h1 { font-size: 2rem; } h2 { font-size: 1.5rem; } h3 { font-size: 1.15rem; }
.stButton>button, .stLinkButton>a { border-radius: 10px; border: 1px solid #d0d0d5; background-color: #f0f0f5; color: #1c1c1e !important; padding: 10px 24px; font-weight: 500; text-decoration: none; transition: all 0.2s ease-in-out; }
.stButton>button:hover, .stLinkButton>a:hover { background-color: #e0e0e5; border-color: #c0c0c5; }
div[data-testid="stMetric"] { background-color: #F9F9F9; border-radius: 12px; padding: 20px; border: 1px solid #EAEAEA; }
div[data-testid="stMetric"] > label { font-size: 0.9rem; color: #555555; }
div[data-testid="stMetric"] > div { font-size: 1.75rem; font-weight: 600; }
.stImage img { border-radius: 12px; border: 1px solid #EAEAEA; }
hr { background-color: #EAEAEA; }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions & Engine Loading ---
@st.cache_data
def load_data(csv_path):
    """Loads and preprocesses product data from a CSV file."""
    try:
        df = pd.read_csv(csv_path)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
        df['Review'] = pd.to_numeric(df['Review'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        return df
    except FileNotFoundError:
        st.error(f"File not found: {csv_path}. Please ensure 'products.csv' is in your GitHub repository.")
        st.stop()

# NEW: A function to load our identifier engine, cached for performance.
@st.cache_resource
def load_identifier_engine():
    return ItemIdentifier()

# (Other helper functions are the same)
def get_rating_stars(rating_text: str) -> str:
    if not isinstance(rating_text, str): return "N/A"
    match = re.search(r'(\d\.\d)', rating_text)
    if not match: return "N/A"
    rating_num = float(match.group(1))
    full_stars = int(rating_num)
    half_star = "★" if (rating_num - full_stars) >= 0.8 else ("✫" if (rating_num - full_stars) > 0.2 else "")
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    stars = "★" * full_stars + half_star + "☆" * empty_stars
    return f"{rating_num} {stars}"

def clean_sales_text(sales_text: str) -> str:
    if not isinstance(sales_text, str): return "N/A"
    return sales_text.split(" ")[0]

def generate_amazon_link(title: str) -> str:
    base_url = "https://www.amazon.in/s?k="
    search_query = urllib.parse.quote_plus(title)
    return f"{base_url}{search_query}"

# --- Session State Initialization ---
if 'product_index' not in st.session_state:
    st.session_state.product_index = 0

# --- App Header ---
st.title("PRISM")
st.markdown("Product Research & Insight System")

df = load_data('products.csv')
identifier = load_identifier_engine() # <-- LOAD THE ENGINE

st.caption(f"Loaded {len(df)} products for analysis.")
st.divider()

# --- Dashboard Layout ---
current_product = df.iloc[st.session_state.product_index]
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.image(current_product.get('Image', ''), use_container_width=True)
    if st.button("Discover Next Product →", use_container_width=True):
        st.session_state.product_index = (st.session_state.product_index + 1) % len(df)
        st.rerun()

with col2:
    title = current_product.get('Title', 'No Title Available')
    st.markdown(f"### {title}")
    amazon_url = generate_amazon_link(title)
    st.link_button("View on Amazon ↗", url=amazon_url, use_container_width=True)
    st.markdown("---")
    
    price = current_product.get('Price', 0)
    sales = clean_sales_text(current_product.get('Monthly Sales', 'N/A'))
    rating_str = get_rating_stars(current_product.get('Ratings', 'N/A'))
    reviews = current_product.get('Review', 0)

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric(label="Price", value=f"₹{price:,.0f}")
    metric_col2.metric(label="Monthly Sales", value=sales)
    
    st.markdown("### Rating")
    st.markdown(f"<h2 style='color: #212121; font-weight: 600;'>{rating_str}</h2>", unsafe_allow_html=True)
    st.markdown(f"Based on **{int(reviews):,}** reviews.")

    st.divider()

    # --- PLUG IN THE ENGINE'S OUTPUT ---
    st.subheader("PRISM Analysis")
    # Use the engine to analyze the title
    identified_item = identifier.identify(title)
    # Display the result in a metric box
    st.metric(label="Identified Item", value=identified_item)
    st.info("The 'PRISM Score' will appear here once the next tool is built.")
    
