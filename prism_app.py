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
import os

# --- Import Engines ---
from item_identifier import ItemIdentifier
from listing_quality_evaluator import ListingQualityEvaluator
from prism_score_evaluator import PrismScoreEvaluator

# --- Page Configuration and CSS ---
st.set_page_config(page_title="PRISM", page_icon="🚀", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Base Styles */
    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #F0F2F6; 
        color: #1a1a1a;
    }
    .main .block-container { 
        padding-top: 1.5rem; 
        padding-bottom: 2rem;
    }
    
    /* Centered Logo and Subtitle */
    .logo-container { 
        text-align: center; 
        margin-bottom: 2rem; 
    }
    .logo-container img { max-width: 250px; }
    .logo-container p { font-size: 1.1rem; color: #555; margin-top: -10px; }

    h1, h2, h3 { color: #1c1c1e; font-weight: 700; }
    h2 { font-size: 1.6rem; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }
    h3 { font-size: 1.25rem; font-weight: 600; }
    
    /* Main Action Buttons (Red) */
    .stButton>button, .stLinkButton>a {
        border-radius: 8px; border: none; background-color: #E65C5F;
        color: #FFFFFF !important; padding: 12px 28px; font-weight: 600;
        font-size: 1.1rem; 
        text-decoration: none; transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover, .stLinkButton>a:hover { 
        background-color: #D92B2F;
    }
    .stButton>button div, .stLinkButton>a div {
        background-color: transparent;
        color: #FFFFFF;
    }

    /* --- Custom Navigation Pane --- */
    .nav-pane {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    }
    .nav-pane .stButton>button {
        background-color: #fff3cd; /* Faint Yellow */
        color: #856404 !important;
        border: 1px solid #ffeeba;
        text-align: left;
        font-weight: 600;
        margin-bottom: 5px;
        padding: 10px 15px;
    }
    .nav-pane .stButton>button:hover {
        background-color: rgba(230, 92, 95, 0.1);
        color: #E65C5F !important;
    }
    /* Active Category Button */
    .nav-pane .stButton>button.active {
        background-color: #E65C5F;
        color: #FFFFFF !important;
        border: 1px solid #D92B2F;
    }
    .nav-pane .stButton>button.active div {
        color: #FFFFFF !important;
    }
    /* Collapse Button */
    .collapse-button button {
        background: transparent !important;
        color: #555 !important;
        font-size: 1.2rem;
        padding: 5px !important;
        border: none !important;
    }
    
    /* (Other styles unchanged) */
    .content-card {
        background-color: #FFFFFF; border-radius: 12px; padding: 25px;
        border: 1px solid #EAEAEA; box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    div[data-testid="stMetric"] {
        background-color: #F9F9F9; border-radius: 12px; padding: 20px; 
        border: 1px solid #EAEAEA; transition: box-shadow 0.2s ease-in-out;
    }
    .potential-label {
        padding: 6px 14px; border-radius: 10px; font-weight: 700;
        font-size: 1.1rem; display: inline-block; text-align: center;
    }
    .high-potential { background-color: #d4edda; color: #155724; }
    .moderate-potential { background-color: #fff3cd; color: #856404; }
    .low-potential { background-color: #f8d7da; color: #721c24; }
    .missing-data-flag { font-size: 0.8rem; color: #6c757d; padding-top: 5px; }
    .score-bar-container { display: flex; align-items: center; gap: 10px; margin-bottom: 1rem; }
    .score-bar-background { background-color: #e9ecef; border-radius: 0.5rem; height: 10px; flex-grow: 1; }
    .score-bar-foreground { background-color: #E65C5F; height: 10px; border-radius: 0.5rem; }
    .score-text { font-size: 1rem; font-weight: 600; color: #555555; }
    .analysis-details { line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

# --- Data Loading and Helper Functions ---
@st.cache_data
def load_and_process_data(csv_path):
    try:
        df = pd.read_csv(csv_path, dtype={'Monthly Sales': str})
    except FileNotFoundError: return None
    df['Price'] = pd.to_numeric(df['Price'].astype(str).str.replace(',', ''), errors='coerce')
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

def generate_indiamart_link(item_name: str):
    base_url = "https://dir.indiamart.com/search.mp?ss="
    search_query = urllib.parse.quote_plus(item_name)
    return f"{base_url}{search_query}"

# --- Main App Execution ---
def main():
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    st.image("prism_logo_new.png")
    st.markdown("<p>Product Research and Integrated Supply Module</p></div>", unsafe_allow_html=True)
    
    # --- Session State Initialization ---
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = 'expanded'
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "Sports, Fitness & Outdoors"

    # --- Layout with Custom Navigation Pane ---
    if st.session_state.sidebar_state == 'expanded':
        nav_pane, main_content = st.columns([2, 5], gap="large")
    else:
        nav_pane, main_content = st.columns([1, 10], gap="small")

    with nav_pane:
        st.markdown("<div class='nav-pane'>", unsafe_allow_html=True)
        if st.session_state.sidebar_state == 'expanded':
            st.subheader("Categories")
            if st.button("◀ Collapse", use_container_width=True, key="collapse"):
                st.session_state.sidebar_state = 'collapsed'
                st.rerun()
            
            categories = {
                "Car & Motorbike": "products_car_&_motorbike.csv",
                "Electronics": "products_electronics.csv",
                "Sports, Fitness & Outdoors": "products_sports,_fitness_&_outdoors.csv",
                "Tools & Home Improvement": "products_tools_&_home_improvement.csv"
            }
            for category in categories.keys():
                is_active = (st.session_state.selected_category == category)
                if st.button(category, use_container_width=True, key=category, type="primary" if is_active else "secondary"):
                    st.session_state.selected_category = category
                    st.session_state.product_pointer = 0
                    st.rerun()
        else:
            if st.button("▶", use_container_width=True, key="expand"):
                st.session_state.sidebar_state = 'expanded'
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with main_content:
        selected_category_name = st.session_state.selected_category
        file_name = f"products_{selected_category_name.replace(', ', '_').replace(' & ', '_').lower()}.csv"
        df = load_and_process_data(file_name)
        
        if df is None:
            st.error(f"File not found: '{file_name}'. Please ensure it is in your GitHub repository.")
            st.stop()

        if 'current_category' not in st.session_state or st.session_state.current_category != selected_category_name:
            st.session_state.current_category = selected_category_name
            indices = list(df.index)
            random.shuffle(indices)
            st.session_state.shuffled_indices = indices
            st.session_state.product_pointer = 0

        st.caption(f"Loaded {len(df)} products for {selected_category_name}.")
        st.divider()
        
        current_shuffled_index = st.session_state.product_pointer
        current_product_index = st.session_state.shuffled_indices[current_shuffled_index]
        current_product = df.iloc[current_product_index]

        col1, col2 = st.columns([2, 3], gap="large")
        with col1:
            st.image(current_product.get('Image', ''), use_container_width=True)
            nav_col1, nav_col2 = st.columns(2)
            if nav_col1.button("← Previous", use_container_width=True):
                st.session_state.product_pointer = (st.session_state.product_pointer - 1 + len(df)) % len(df)
                st.rerun()
            if nav_col2.button("Next →", use_container_width=True):
                st.session_state.product_pointer = (st.session_state.product_pointer + 1) % len(df)
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
