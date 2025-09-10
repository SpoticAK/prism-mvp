# File: prism_app.py
import streamlit as st
import pandas as pd
import re
import math
import urllib.parse
import random
import requests
import cv2
import numpy as np

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
    background-color: #FFFFFF;
    color: #212121;
}
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
h1, h2, h3 { color: #1c1c1e; font-weight: 600; }
h1 { font-size: 2rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.15rem; }
.stButton>button, .stLinkButton>a {
    border-radius: 10px; border: 1px solid #d0d0d5; background-color: #f0f0f5;
    color: #1c1c1e !important; padding: 10px 24px; font-weight: 500;
    text-decoration: none; transition: all 0.2s ease-in-out;
}
.stButton>button:hover, .stLinkButton>a:hover { background-color: #e0e0e5; border-color: #c0c0c5; }
div[data-testid="stMetric"] {
    background-color: #F9F9F9; border-radius: 12px; padding: 20px; border: 1px solid #EAEAEA;
}
div[data-testid="stMetric"] > label { font-size: 0.9rem; color: #555555; }
div[data-testid="stMetric"] > div { font-size: 1.75rem; font-weight: 600; }
.stImage img { border-radius: 12px; border: 1px solid #EAEAEA; }
hr { background-color: #EAEAEA; }
.potential-label {
    padding: 4px 12px; border-radius: 8px; font-weight: 600; font-size: 1rem; display: inline-block;
}
.high-potential { background-color: #d4edda; color: #155724; }
.moderate-potential { background-color: #fff3cd; color: #856404; }
.low-potential { background-color: #f8d7da; color: #721c24; }
.missing-data-flag { font-size: 0.8rem; color: #6c757d; padding-top: 5px; }
</style>
""", unsafe_allow_html=True)

# --- Engine #1: Item Identifier ---
class ItemIdentifier:
    def __init__(self):
        self._noise_words = {
            'stylish', 'comfortable', 'premium', 'high', 'quality', 'heavy', 'duty',
            'waterproof', 'convertible', 'streachable', 'full', 'loose', 'relaxed',
            'retractable', 'handheld', 'rechargeable', 'portable', 'soft', 'stretchy',
            'cushioned', 'breathable', 'sturdy', 'micronized', 'new', 'complete',
            "men's", "women's", "boy's", "girl's", 'mens', 'womens', 'men',
            'women', 'kids', 'man', 'woman', 'boys', 'girls', 'unisex', 'adult',
            'home', 'gym', 'workout', 'exercise', 'training', 'gear', 'for',
            'accessories', 'powerlifting', 'solid', 'combo', 'kit', 'pack', 'set',
            'pcs', 'of', 'gram', 'serves', 'piece', 'pieces', 'anti', 'slip', 'multi',
            'with', 'and', 'the', 'a', 'in', 'per', 'ideal', 'everyday', 'use',
            'black', 'white', 'red', 'blue', 'green', 'multicolor',
            'large', 'medium', 'small', 'size', 'fit',
            'fitness', 'toning', 'band', 'bands', 'cover', 'support'
        }
        self._spec_pattern = re.compile(r'\b(\d+l|\d+ml|\d+mm|\d+g|\d+kg)\b', re.IGNORECASE)

    def identify(self, title: str) -> str:
        if not isinstance(title, str): return "Not Found"
        limit = 50
        if len(title) > limit:
            next_space = title.find(' ', limit)
            golden_zone = title[:next_space] if next_space != -1 else title[:limit]
        else:
            golden_zone = title
        
        sanitized_zone = golden_zone.lower().replace("'s", "")
        cleaned_zone = self._spec_pattern.sub('', sanitized_zone)
        words = re.findall(r'\b[a-zA-Z-]+\b', cleaned_zone)
        
        if not words: return "Not Found"
            
        candidate_words = words[1:] if len(words) > 1 else words
        item_words = [w for w in candidate_words if w not in self._noise_words]

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
            elif 175 <= price <= 199 or 351 <= price <= 400: points_earned += 2
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
            elif 4.0 <= rating < 4.2: points_earned += 2
            elif 3.7 <= rating < 4.0: points_earned += 1
        else: points_available -= 3; missing_data = True

        quality = product_data.get('Listing Quality')
        if pd.notna(quality):
            if quality == 'Good': points_earned += 2
            elif quality == 'Average': points_earned += 1
        else: points_available -= 2; missing_data = True
            
        sales = product_data.get('Cleaned Sales')
        if pd.notna(sales):
            if sales >= 1000: points_earned += 3
            elif 300 <= sales < 1000: points_earned += 2
            elif 100 <= sales < 300: points_earned += 1
        else: points_available -= 3; missing_data = True

        final_score = int((points_earned / points_available) * 100) if points_available > 0 else 0
            
        if final_score > 80: potential_label = "High Potential"
        elif final_score >= 70: potential_label = "Moderate Potential"
        else: potential_label = "Low Potential"
            
        return final_score, potential_label, missing_data

# --- Data Loading and Processing ---
@st.cache_data
def load_and_process_data(csv_path):
    df = pd.read_csv(csv_path, dtype={'Monthly Sales': str})
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Review'] = pd.to_numeric(df['Review'].astype(str).str.replace(',', ''), errors='coerce')
    df['Ratings_Num'] = df['Ratings'].str.extract(r'(\d\.\d)').astype(float)
    
    # Correctly handle and clean the 'Monthly Sales' column
    df['Cleaned Sales'] = df['Monthly Sales'].apply(lambda s: int(re.sub(r'\D', '', s.replace('K+', '000'))) if isinstance(s, str) and s else 0)
    
    item_engine = ItemIdentifier()
    quality_engine = ListingQualityEvaluator()
    score_engine = PrismScoreEvaluator()
    
    df['Identified Item'] = df['Title'].apply(item_engine.identify)
    df['Listing Quality'] = df['Image'].apply(quality_engine.get_score)
    
    scores = df.apply(score_engine.get_score, axis=1)
    df[['PRISM Score', 'Potential', 'Missing Data']] = pd.DataFrame(scores.tolist(), index=df.index)
    return df

# --- UI Helper Functions ---
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

# --- Main App Execution ---
st.title("PRISM")
st.markdown("Product Research & Insight System")
df = load_and_process_data('products.csv')
st.caption(f"Loaded and shuffled {len(df)} products for discovery.")
st.divider()

if 'shuffled_indices' not in st.session_state:
    indices = list(df.index)
    random.shuffle(indices)
    st.session_state.shuffled_indices = indices
    st.session_state.product_pointer = 0

current_index = st.session_state.shuffled_indices[st.session_state.product_pointer]
current_product = df.iloc[current_index]

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.image(current_product.get('Image', ''), use_container_width=True)
    if st.button("Discover Next Product →", use_container_width=True):
        st.session_state.product_pointer = (st.session_state.product_pointer + 1) % len(df)
        st.rerun()

with col2:
    st.markdown(f"### {current_product.get('Title', 'No Title Available')}")
    st.link_button("View on Amazon ↗", url=generate_amazon_link(current_product.get('Title', '')), use_container_width=True)
    st.markdown("---")
    
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
    
    st.metric(label="PRISM Score", value=f"{current_product.get('PRISM Score', 0)}/100")
    st.markdown(f"<div class='potential-label {potential_class}'>{potential}</div>", unsafe_allow_html=True)
    if current_product.get('Missing Data', False):
        st.markdown("<div class='missing-data-flag'>*Score calculated with some data unavailable.</div>", unsafe_allow_html=True)
