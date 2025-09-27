\# File: prism_app.py
import streamlit as st
import pandas as pd
import re
import math
import urllib.parse
import random
import requests
import cv2
import numpy as np

# --- Page Configuration and CSS ---
st.set_page_config(page_title="PRISM", page_icon="🚀", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Base Styles & Typography */
    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #F0F2F6; 
        color: #1a1a1a;
    }
    /* --- FIX: Reduce top padding --- */
    .main .block-container { 
        padding-top: 2rem; 
        padding-bottom: 2rem; 
    }
    
    /* Centered Logo and Subtitle */
    .logo-container { 
        text-align: center; 
        margin-bottom: 2rem; 
    }
    .logo-container img { 
        max-width: 250px; 
        margin-bottom: 0.5rem; 
    }
    .logo-container p { 
        font-size: 1.1rem; 
        color: #555; 
        margin-top: -10px; 
    }

    /* (Other styles are unchanged) */
    h1, h2, h3 { color: #1c1c1e; font-weight: 700; }
    .stButton>button, .stLinkButton>a {
        border-radius: 8px; border: none; background-color: #E65C5F; 
        color: #FFFFFF !important; padding: 12px 28px; font-weight: 600;
        font-size: 1.1rem; font-family: 'Inter', sans-serif;
        text-decoration: none; transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover, .stLinkButton>a:hover { 
        background-color: #D92B2F;
        color: #FFFFFF !important;
    }
    .stButton>button div, .stLinkButton>a div {
        background-color: transparent;
    }
    .content-card {
        background-color: #FFFFFF; border-radius: 12px; padding: 25px;
        border: 1px solid #EAEAEA; box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    div[data-testid="stMetric"] {
        background-color: #F9F9F9; border-radius: 12px; padding: 20px; 
        border: 1px solid #EAEAEA; transition: box-shadow 0.2s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# --- Engine #1: Item Identifier ---
class ItemIdentifier:
    def __init__(self):
        self._noise_words = {
            'stylish', 'comfortable', 'premium', 'high', 'quality', 'heavy', 'duty', 'waterproof', 'convertible', 
            'streachable', 'full', 'loose', 'relaxed', 'retractable', 'handheld', 'rechargeable', 'portable', 
            'soft', 'stretchy', 'cushioned', 'breathable', 'sturdy', 'micronized', 'new', 'complete', 
            "men's", "women's", "boy's", "girl's", 'mens', 'womens', 'men', 'women', 'kids', 'man', 'woman', 
            'boys', 'girls', 'unisex', 'adult', 'home', 'gym', 'workout', 'exercise', 'training', 'gear', 'for', 
            'accessories', 'powerlifting', 'solid', 'combo', 'kit', 'pack', 'set', 'pcs', 'of', 'gram', 'serves', 
            'piece', 'pieces', 'anti', 'slip', 'multi', 'with', 'and', 'the', 'a', 'in', 'per', 'ideal', 
            'everyday', 'use', 'black', 'white', 'red', 'blue', 'green', 'multicolor', 'large', 'medium', 
            'small', 'size', 'fit', 'fitness', 'toning', 'band', 'bands', 'cover', 'support'
        }
        self._model_number_pattern = re.compile(r'\b[a-zA-Z]+\d+[a-zA-Z0-9]*\b|\b\d+[a-zA-Z]+\b')

    def identify(self, title: str) -> str:
        if not isinstance(title, str): return "Not Found"
        words = title.lower().split()
        golden_zone_words = words[:10]
        candidate_words = golden_zone_words[1:] if len(golden_zone_words) > 1 else golden_zone_words
        item_words = []
        for word in candidate_words:
            clean_word = re.sub(r'[^\w-]', '', word)
            if not self._model_number_pattern.search(clean_word) and clean_word not in self._noise_words:
                item_words.append(clean_word)
        if not item_words: return "Not Found"
        return " ".join(item_words).title()

# --- Engine #2: Listing Quality Evaluator ---
class ListingQualityEvaluator:
    @st.cache_data
    def get_score(_self, image_url: str) -> str:
        if not isinstance(image_url, str) or not image_url: return "Error"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(image_url, timeout=10, headers=headers)
            response.raise_for_status()
            image_array = np.frombuffer(response.content, np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if img is None: return "Error"
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
            object_pixels = cv2.countNonZero(thresh)
            total_pixels = img.shape[0] * img.shape[1]
            coverage_percentage = (object_pixels / total_pixels) * 100
            if coverage_percentage > 70: return "Good"
            elif coverage_percentage >= 50: return "Average"
            else: return "Poor"
        except Exception:
            return "Error"

# --- Engine #3: PRISM Score Evaluator ---
class PrismScoreEvaluator:
    def get_score(self, product_data: pd.Series) -> (int, str, bool):
        points_earned, points_available, missing_data = 0, 15, False
        price = product_data.get('Price')
        if pd.notna(price):
            if 200 <= price <= 350: points_earned += 4
            elif 175 <= price <= 199 or price > 350: points_earned += 2
            elif price < 175: points_earned += 1
        else: points_available -= 4; missing_data = True
        reviews = product_data.get('Review')
        if pd.notna(reviews):
            if reviews >= 100: points_earned += 3
            elif 50 <= reviews <= 99: points_earned += 2
            else: points_earned += 1
        else: points_available -= 3; missing_data = True
        rating = product_data.get('Ratings_Num')
        if pd.notna(rating):
            if rating >= 4.2: points_earned += 3
            elif 3.6 <= rating <= 4.19: points_earned += 2
            elif 3.0 <= rating <= 3.59: points_earned += 1
        else: points_available -= 3; missing_data = True
        quality = product_data.get('Listing Quality')
        if pd.notna(quality) and quality != "Error":
            if quality == 'Poor': points_earned += 2
            elif quality == 'Average' or quality == 'Good': points_earned += 1
        else: points_available -= 2; missing_data = True
        original_sales = product_data.get('Monthly Sales')
        cleaned_sales = product_data.get('Cleaned Sales')
        if pd.isna(original_sales) or str(original_sales).strip().lower() in ['n/a', '']:
            points_available -= 3; missing_data = True
        else:
            if cleaned_sales >= 500: points_earned += 3
            elif 100 <= cleaned_sales <= 499: points_earned += 2
            else: points_earned += 1
        final_score = int((points_earned / points_available) * 100) if points_available > 0 else 0
        if final_score > 80: potential_label = "High Potential"
        elif final_score >= 66: potential_label = "Moderate Potential"
        else: potential_label = "Low Potential"
        return final_score, potential_label, missing_data

# --- Data Loading and Helper Functions ---
@st.cache_data
def load_and_process_data(csv_path):
    try:
        df = pd.read_csv(csv_path, dtype={'Monthly Sales': str})
    except FileNotFoundError: return None
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Review'] = pd.to_numeric(df['Review'].astype(str).str.replace(',', ''), errors='coerce')
    df['Ratings_Num'] = df['Ratings'].str.extract(r'(\d\.\d)').astype(float)
    df['Cleaned Sales'] = df['Monthly Sales'].str.lower().str.replace('k', '000').str.extract(r'(\d+)').astype(float).fillna(0).astype(int)
    item_engine = ItemIdentifier()
    quality_engine = ListingQualityEvaluator()
    score_engine = PrismScoreEvaluator()
    df['Identified Item'] = df['Title'].apply(item_engine.identify)
    df['Listing Quality'] = df['Image'].apply(quality_engine.get_score)
    scores = df.apply(score_engine.get_score, axis=1)
    df[['PRISM Score', 'Potential', 'Missing Data']] = pd.DataFrame(scores.tolist(), index=df.index)
    return df

def get_rating_stars(rating_text):
    if not isinstance(rating_text, str): return "N/A"
    match = re.search(r'(\d\.\d)', rating_text)
    if not match: return "N/A"
    rating_num = float(match.group(1))
    full_stars = int(rating_num)
    half_star = "★" if (rating_num - full_stars) >= 0.8 else ("✫" if (rating_num - full_stars) > 0.2 else "")
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    stars = "★" * full_stars + half_star + "☆" * empty_stars
    return f"{rating_num} {stars}"

def clean_sales_text(sales_text):
    if not isinstance(sales_text, str): return "N/A"
    return sales_text.split(" ")[0]

def generate_amazon_link(title):
    base_url = "https://www.amazon.in/s?k="
    search_query = urllib.parse.quote_plus(title)
    return f"{base_url}{search_query}"

def generate_indiamart_link(item_name):
    base_url = "https://dir.indiamart.com/search.mp?ss="
    search_query = urllib.parse.quote_plus(item_name)
    return f"{base_url}{search_query}"

# --- Main App Execution ---
def main():
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    st.image("prism_logo.png", width=250)
    st.markdown("<p>Product Research and Integrated Supply Module</p></div>", unsafe_allow_html=True)
    
    df = load_and_process_data('products.csv')
    if df is None:
        st.error("File not found: 'products.csv'. Please ensure it's in your GitHub repository.")
        st.stop()

    if 'product_index' not in st.session_state:
        st.session_state.product_index = 0

    st.caption(f"Loaded {len(df)} products for discovery.")
    st.divider()

    current_product = df.iloc[st.session_state.product_index]

    col1, col2 = st.columns([2, 3], gap="large")
    with col1:
        st.image(current_product.get('Image', ''), use_container_width=True)
        nav_col1, nav_col2 = st.columns(2)
        if nav_col1.button("← Previous", use_container_width=True):
            st.session_state.product_index = (st.session_state.product_index - 1 + len(df)) % len(df)
            st.rerun()
        if nav_col2.button("Next →", use_container_width=True):
            st.session_state.product_index = (st.session_state.product_index + 1) % len(df)
            st.rerun()

    with col2:
        with st.container():
            st.markdown(f"<div class='content-card'>", unsafe_allow_html=True)
            st.markdown(f"### {current_product.get('Title', 'No Title Available')}")
            st.link_button("View on Amazon ↗", url=generate_amazon_link(current_product.get('Title', '')), use_container_width=True)
            st.markdown("---")
            
            metric_col1, metric_col2 = st.columns(2)
            metric_col1.metric(label="💰 Price", value=f"₹{current_product.get('Price', 0):,.0f}")
            metric_col2.metric(label="📈 Monthly Sales", value=clean_sales_text(current_product.get('Monthly Sales', 'N/A')))
            
            st.markdown("### ⭐ Rating")
            st.markdown(f"<h2 style='color: #212121; font-weight: 600;'>{get_rating_stars(current_product.get('Ratings', 'N/A'))}</h2>", unsafe_allow_html=True)
            st.markdown(f"Based on **{int(current_product.get('Review', 0)):,}** reviews.")
            st.divider()

            st.subheader("📊 PRISM Analysis")
            potential = current_product.get('Potential', 'Low Potential')
            potential_class = potential.lower().replace(" ", "-")
            prism_score = int(current_product.get('PRISM Score', 0))
            identified_item = current_product.get('Identified Item', 'N/A')

            st.markdown("**PRISM Score**")
            st.markdown(f"""
                <div class="score-bar-container">
                    <div class="score-bar-background">
                        <div class="score-bar-foreground" style="width: {prism_score}%;"></div>
                    </div>
                    <div class="score-text">{prism_score}/100</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"<div class='potential-label {potential_class}'>{potential}</div>", unsafe_allow_html=True)
            st.markdown("---")
            
            st.markdown(f"""
            <div class='analysis-details'>
                <b>Identified Item:</b> {identified_item}<br>
                <b>Listing Quality:</b> {current_product.get('Listing Quality', 'N/A')}
            </div>
            """, unsafe_allow_html=True)

            if current_product.get('Missing Data', False):
                st.markdown("<div class='missing-data-flag'>*Score calculated with some data unavailable.</div>", unsafe_allow_html=True)
            
            st.divider()
            
            st.subheader("🔗 Supplier Gateway")
            indiamart_url = generate_indiamart_link(identified_item)
            st.link_button("Search for Suppliers on Indiamart ↗", url=indiamart_url, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
