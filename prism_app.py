# File: prism_app.py
import streamlit as st
import pandas as pd
import re
import math
import urllib.parse
import random
from item_identifier import ItemIdentifier
from listing_quality_evaluator import ListingQualityEvaluator
from prism_score_evaluator import PrismScoreEvaluator

# --- Page Configuration ---
st.set_page_config(
    page_title="PRISM MVP",
    page_icon="🚀",
    layout="wide"
)

# --- Clean, Apple-Inspired White Theme CSS ---
st.markdown("""
<style>
/* (Your existing CSS styles are here) */
/* NEW: Styles for Potential Labels */
.potential-label {
    padding: 4px 12px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    display: inline-block;
}
.high-potential { background-color: #d4edda; color: #155724; }
.moderate-potential { background-color: #fff3cd; color: #856404; }
.low-potential { background-color: #f8d7da; color: #721c24; }
.missing-data-flag { font-size: 0.8rem; color: #6c757d; padding-top: 5px; }
</style>
""", unsafe_allow_html=True) # Note: For brevity, I've collapsed the full CSS block.

# --- Helper Functions ---
@st.cache_data
def load_data(csv_path):
    """Loads and preprocesses product data, now including the PRISM Score."""
    try:
        df = pd.read_csv(csv_path, dtype={'Monthly Sales': str})
        
        # Clean core data types
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Review'] = pd.to_numeric(df['Review'].astype(str).str.replace(',', ''), errors='coerce')
        
        # Extract numeric rating for scoring
        df['Ratings_Num'] = df['Ratings'].str.extract(r'(\d\.\d)').astype(float)

        # --- Run Engines ---
        item_engine = ItemIdentifier()
        quality_engine = ListingQualityEvaluator()
        score_engine = PrismScoreEvaluator()

        df['Identified Item'] = df['Title'].apply(item_engine.identify)
        df['Listing Quality'] = df['Image'].apply(quality_engine.get_score)
        
        # Apply the scoring logic row by row
        scores = df.apply(score_engine.get_score, axis=1)
        df[['PRISM Score', 'Potential', 'Missing Data']] = pd.DataFrame(scores.tolist(), index=df.index)

        return df
    except FileNotFoundError:
        st.error(f"File not found: {csv_path}. Please ensure 'products.csv' is in your GitHub repository.")
        st.stop()
        
# (Your other helper functions: get_rating_stars, clean_sales_text, etc. remain the same)
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

# --- Session State & App Header ---
# (This section remains the same)
df = load_data('products.csv')

if 'shuffled_indices' not in st.session_state:
    indices = list(df.index)
    random.shuffle(indices)
    st.session_state.shuffled_indices = indices
    st.session_state.product_pointer = 0

st.title("PRISM")
st.markdown("Product Research & Insight System")
st.caption(f"Loaded and shuffled {len(df)} products for discovery.")
st.divider()

# --- Dashboard Layout ---
current_index = st.session_state.shuffled_indices[st.session_state.product_pointer]
current_product = df.iloc[current_index]

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.image(current_product.get('Image', ''), use_container_width=True)
    if st.button("Discover Next Product →", use_container_width=True):
        st.session_state.product_pointer = (st.session_state.product_pointer + 1) % len(df)
        st.rerun()

with col2:
    # (The top part of this column remains the same)
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

    # --- FINAL: Updated PRISM Analysis Section ---
    st.subheader("PRISM Analysis")
    identified_item = current_product.get('Identified Item', 'N/A')
    prism_score = current_product.get('PRISM Score', 0)
    potential = current_product.get('Potential', 'Low Potential')
    missing_data = current_product.get('Missing Data', False)
    
    # Determine the CSS class for the potential label
    potential_class = potential.lower().replace(" ", "-")

    # Display the score, potential label, and missing data flag
    st.metric(label="PRISM Score", value=f"{prism_score}/100")
    st.markdown(f"<div class='potential-label {potential_class}'>{potential}</div>", unsafe_allow_html=True)
    if missing_data:
        st.markdown("<div class='missing-data-flag'>*Score calculated with some data unavailable.</div>", unsafe_allow_html=True)
