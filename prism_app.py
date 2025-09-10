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

# --- Page Configuration and CSS ---
st.set_page_config(page_title="PRISM MVP", page_icon="🚀", layout="wide")
st.markdown("""
<style>
/* (Your existing CSS styles are here) */
/* Sidebar Image Styling */
.st-emotion-cache-17lntch {
    display: flex;
    justify-content: center;
}
.st-emotion-cache-17lntch img {
    border-radius: 8px;
    border: 1px solid #EAEAEA;
    width: 70px;
    height: 70px;
    object-fit: cover;
}
.st-emotion-cache-17lntch button {
    padding: 5px;
    margin-bottom: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True) # Note: For brevity, I've collapsed the full CSS block.

# --- Data Loading and Helper Functions ---
@st.cache_data
def load_and_process_data(csv_path):
    df = pd.read_csv(csv_path, dtype={'Monthly Sales': str})
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Review'] = pd.to_numeric(df['Review'].astype(str).str.replace(',', ''), errors='coerce')
    df['Ratings_Num'] = df['Ratings'].str.extract(r'(\d\.\d)').astype(float)
    df['Cleaned Sales'] = df['Monthly Sales'].apply(lambda s: int(re.sub(r'\D', '', s.replace('k+', '000'))) if isinstance(s, str) and s else 0)
    
    item_engine = ItemIdentifier()
    quality_engine = ListingQualityEvaluator()
    score_engine = PrismScoreEvaluator()
    
    df['Identified Item'] = df['Title'].apply(item_engine.identify)
    df['Listing Quality'] = df['Image'].apply(quality_engine.get_score)
    
    scores = df.apply(score_engine.get_score, axis=1)
    df[['PRISM Score', 'Potential', 'Missing Data']] = pd.DataFrame(scores.tolist(), index=df.index)
    return df

# (Other helper functions like get_rating_stars, etc., remain unchanged)
def get_rating_stars(rating_text: str):
    if not isinstance(rating_text, str): return "N/A"
    match = re.search(r'(\d\.\d)', rating_text)
    if not match: return "N/A"
    rating_num = float(match.group(1))
    full_stars = int(rating_num)
    half_star = "★" if (rating_num - full_stars) >= 0.8 else ("✫" if (rating_num - full_stars) > 0.2 else "")
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    stars = "★" * full_stars + half_star + "☆" * empty_stars
    return f"{rating_num} {stars}"

def clean_sales_text(sales_text: str):
    if not isinstance(sales_text, str): return "N/A"
    return sales_text.split(" ")[0]

def generate_amazon_link(title: str):
    base_url = "https://www.amazon.in/s?k="
    search_query = urllib.parse.quote_plus(title)
    return f"{base_url}{search_query}"

# --- Main App Execution ---
def main():
    st.title("PRISM")
    st.markdown("Product Research & Insight System")
    df = load_and_process_data('products.csv')
    st.caption(f"Loaded and shuffled {len(df)} products for discovery.")
    st.divider()

    # --- Session State Initialization ---
    if 'shuffled_indices' not in st.session_state:
        indices = list(df.index)
        random.shuffle(indices)
        st.session_state.shuffled_indices = indices
        st.session_state.product_pointer = 0
        st.session_state.saved_products = [] # Initialize saved products list
    
    # --- Sidebar: Your Shortlist ---
    with st.sidebar:
        st.subheader("Your Shortlist")
        if not st.session_state.saved_products:
            st.info("Click the '⭐️ Save Product' button to add items here.")
        else:
            for saved_index in st.session_state.saved_products:
                product = df.iloc[saved_index]
                # Create a button for each saved item with its image
                if st.button(f"saved_{saved_index}", key=f"saved_{saved_index}"):
                    # Find the position of this product in the *shuffled* list
                    st.session_state.product_pointer = st.session_state.shuffled_indices.index(saved_index)
                    st.rerun()
                st.image(product.get('Image'), width=70, caption=product.get('Title')[:30]+"...")

            if st.button("Clear Shortlist", use_container_width=True):
                st.session_state.saved_products = []
                st.rerun()

    # --- Main Dashboard ---
    current_shuffled_index = st.session_state.product_pointer
    current_product_index = st.session_state.shuffled_indices[current_shuffled_index]
    current_product = df.iloc[current_product_index]

    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        st.image(current_product.get('Image', ''), use_container_width=True)
        
        # Navigation Buttons
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("← Previous Product", use_container_width=True):
                st.session_state.product_pointer = (st.session_state.product_pointer - 1) % len(df)
                st.rerun()
        with nav_col2:
            if st.button("Next Product →", use_container_width=True):
                st.session_state.product_pointer = (st.session_state.product_pointer + 1) % len(df)
                st.rerun()

    with col2:
        st.markdown(f"### {current_product.get('Title', 'No Title Available')}")
        
        link_col, save_col = st.columns([3, 1])
        with link_col:
            st.link_button("View on Amazon ↗", url=generate_amazon_link(current_product.get('Title', '')), use_container_width=True)
        with save_col:
            if st.button("⭐️ Save", use_container_width=True):
                if current_product_index not in st.session_state.saved_products:
                    st.session_state.saved_products.append(current_product_index)
                    st.rerun()
        
        st.markdown("---")
        
        # (The rest of the display logic is unchanged)
        metric_col1, metric_col2 = st.columns(2)
        metric_col1.metric(label="Price", value=f"₹{current_product.get('Price', 0):,.0f}")
        metric_col2.metric(label="Monthly Sales", value=clean_sales_text(current_product.get('Monthly Sales', 'N/A')))
        
        st.markdown("### Rating")
        st.markdown(f"<h2 style='color: #212121; font-weight: 600;'>{get_rating_stars(current_product.get('Ratings', 'N/A'))}</h2>", unsafe_allow_html=True)
        st.markdown(f"Based on **{int(current_product.get('Review', 0)):,}** reviews.")
        st.divider()

        st.subheader("PRISM Analysis")
        potential = current_product.get('Potential', 'Low Potential')
        potential_class = potential.lower().replace(" ", "-")
        prism_score = int(current_product.get('PRISM Score', 0))

        st.markdown("**PRISM Score**")
        score_bar_col, score_text_col = st.columns([4, 1])
        with score_bar_col:
            st.progress(float(prism_score) / 100.0)
        with score_text_col:
            st.markdown(f"<div class='score-text'>{prism_score}/100</div>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='analysis-details'><b>Identified Item:</b> {current_product.get('Identified Item', 'N/A')}<br><b>Listing Quality:</b> {current_product.get('Listing Quality', 'N/A')}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='potential-label {potential_class}' style='margin-top: 10px;'>{potential}</div>", unsafe_allow_html=True)
        if current_product.get('Missing Data', False):
            st.markdown("<div class='missing-data-flag'>*Score calculated with some data unavailable.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
