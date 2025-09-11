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
# Your full CSS is here...
st.markdown("""<style>... (Your CSS goes here) ...</style>""", unsafe_allow_html=True) 

# --- Data Loading and Helper Functions ---
@st.cache_data
def load_and_process_data(csv_path):
    # This function remains unchanged.
    df = pd.read_csv(csv_path, dtype={'Monthly Sales': str})
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

# ... (All other helper functions like get_rating_stars are unchanged) ...

# --- Main App Execution ---
def main():
    st.title("PRISM")
    st.markdown("Product Research & Insight System")
    
    df = load_and_process_data('products.csv')
    if df is None:
        st.error("File not found: 'products.csv'. Please ensure it is in your GitHub repository.")
        st.stop()

    st.caption(f"Loaded {len(df)} products for discovery.")
    st.divider()

    # --- Session State Initialization with URL Parameters ---
    if 'shuffled_indices' not in st.session_state:
        # This block now runs only once per session
        indices = list(df.index)
        random.shuffle(indices)
        st.session_state.shuffled_indices = indices
        
        # Initialize saved_products and notes from URL
        try:
            query_params = st.query_params.to_dict()
            saved_from_url = [int(i) for i in query_params.get("saved", [])]
            # Ensure the list is unique
            st.session_state.saved_products = list(dict.fromkeys(saved_from_url))
            st.session_state.notes = {int(k.split('_')[1]): v[0] for k, v in query_params.items() if k.startswith("note_")}
        except:
             st.session_state.saved_products = []
             st.session_state.notes = {}

        # --- CRITICAL FIX ---
        # If there are saved products in the URL, start by showing the first one.
        if st.session_state.saved_products:
            first_saved_index = st.session_state.saved_products[0]
            if first_saved_index in st.session_state.shuffled_indices:
                 st.session_state.product_pointer = st.session_state.shuffled_indices.index(first_saved_index)
            else:
                 st.session_state.product_pointer = 0 # Fallback if saved index is somehow invalid
        else:
            st.session_state.product_pointer = 0

    # ... (The rest of the code, including the sidebar and dashboard layout, is unchanged) ...

if __name__ == "__main__":
    main()
