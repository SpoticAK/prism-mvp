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

# --- Import Engines ---
from item_identifier import ItemIdentifier
from listing_quality_evaluator import ListingQualityEvaluator
from prism_score_evaluator import PrismScoreEvaluator

# --- Page Configuration and CSS ---
st.set_page_config(page_title="PRISM", page_icon="🚀", layout="wide")
st.markdown("""
<style>
    /* Base Styles */
    html, body, [class*="st-"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        background-color: #F0F2F6; color: #212121;
    }
    .main .block-container { padding: 1.5rem 2.5rem; }
    h1, h2, h3 { color: #1c1c1e; font-weight: 700; }
    h1 { font-size: 2.2rem; }
    h2 { font-size: 1.6rem; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }
    h3 { font-size: 1.25rem; font-weight: 600; }

    /* Centered and Styled Title */
    .title-container { text-align: center; margin-bottom: 1.5rem; }
    .title-container h1 { font-size: 3.5rem; font-weight: 800; letter-spacing: -3px; }
    .title-container p { font-size: 1.1rem; color: #555; margin-top: -10px; }

    /* --- UPDATED: Buttons with new color scheme --- */
    .stButton>button, .stLinkButton>a {
        border-radius: 8px; border: none; background-color: #D92B2F; /* Modern Red */
        color: #FFFFFF !important; padding: 12px 28px; font-weight: 600;
        text-decoration: none; transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover, .stLinkButton>a:hover { 
        background-color: #B92428; /* Darker Red on Hover */
        color: #FFFFFF !important;
    }
    
    /* Main Content Card */
    .content-card {
        background-color: #FFFFFF; border-radius: 12px; padding: 25px;
        border: 1px solid #EAEAEA; box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    
    div[data-testid="stMetric"] {
        background-color: #F9F9F9; border-radius: 12px; padding: 20px; 
        border: 1px solid #EAEAEA; transition: box-shadow 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover { box-shadow: 0 8px 15px rgba(0,0,0,0.06); }
    div[data-testid="stMetric"] > label { font-size: 1rem; color: #555555; font-weight: 500; }
    div[data-testid="stMetric"] > div { font-size: 2rem; font-weight: 700; }

    /* (Other styles unchanged) */
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
    .score-bar-foreground { background-color: #007bff; height: 10px; border-radius: 0.5rem; }
    .score-text { font-size: 1rem; font-weight: 600; color: #555555; }
    .analysis-details { line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

# --- (Engine classes and all other functions are unchanged) ---
@st.cache_data
def load_and_process_data(csv_path):
    # ... (code is unchanged)
    pass
# ... (all other functions are unchanged)

# --- Main App Execution ---
def main():
    st.markdown("<div class='title-container'><h1>PRISM</h1><p>Product Research and Integrated Supply Module</p></div>", unsafe_allow_html=True)
    
    df = load_and_process_data('products.csv')
    if df is None:
        st.error("File not found: 'products.csv'. Please ensure it is in your GitHub repository.")
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
