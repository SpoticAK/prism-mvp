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
        padding: 1.5rem 2.5rem; 
    }
    
    /* Centered Logo and Subtitle */
    .logo-container { 
        text-align: center; 
        margin-bottom: 2rem; 
    }
    .logo-container img { 
        max-width: 250px; 
    }
    .logo-container p { 
        font-size: 1.1rem; 
        color: #555; 
        margin-top: -10px; 
    }

    /* Main Action Buttons */
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
    
    /* --- NEW: Sidebar / Nav Pane Styling --- */
    [data-testid="stSidebar"] {
        padding-top: 2rem;
    }
    .category-btn {
        width: 100%;
        padding: 10px 15px;
        margin-bottom: 5px;
        border-radius: 8px;
        background-color: transparent;
        color: #333 !important;
        border: 1px solid transparent;
        text-align: left;
        font-weight: 600;
        transition: all 0.2s;
    }
    .category-btn:hover {
        background-color: #f0f0f5;
        border: 1px solid #d0d0d5;
    }
    .category-btn.active {
        background-color: #E65C5F;
        color: #FFFFFF !important;
        border: 1px solid #D92B2F;
    }
    
    /* (Other styles are unchanged) */
</style>
""", unsafe_allow_html=True)

# --- (Engine classes and all helper functions are unchanged from the last correct version) ---
@st.cache_data
def load_and_process_data(csv_path):
    # ...
    pass
# ...

# --- Main App Execution ---
def main():
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    st.image("prism_logo_new.png")
    st.markdown("<p>Product Research and Integrated Supply Module</p></div>", unsafe_allow_html=True)
    
    # --- Sidebar for Category Selection ---
    with st.sidebar:
        st.subheader("Select a Category")
        
        categories = {
            "Car & Motorbike": "products_car_&_motorbike.csv",
            "Electronics": "products_electronics.csv",
            "Sports, Fitness & Outdoors": "products_sports,_fitness_&_outdoors.csv",
            "Tools & Home Improvement": "products_tools_&_home_improvement.csv"
        }
        
        if 'selected_category' not in st.session_state:
            st.session_state.selected_category = "Sports, Fitness & Outdoors"

        for category in categories.keys():
            # Use markdown to create a styled button
            is_active = (st.session_state.selected_category == category)
            button_class = "active-category" if is_active else ""
            if st.button(category, use_container_width=True, key=category, type="primary" if is_active else "secondary"):
                st.session_state.selected_category = category
                # Reset pointer when category changes to avoid index errors
                st.session_state.product_pointer = 0
                st.rerun()

    # --- Main Dashboard ---
    selected_category_name = st.session_state.selected_category
    file_name = categories[selected_category_name]
    df = load_and_process_data(file_name)
    
    if df is None:
        st.error(f"File not found: '{file_name}'. Please ensure it is in your GitHub repository.")
        st.stop()

    # Reset randomization if the category has changed
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
