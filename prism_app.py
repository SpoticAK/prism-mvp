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
/* (Your existing CSS is here) */
/* Sidebar Styling */
.st-emotion-cache-17lntch img {
    border-radius: 8px; border: 1px solid #EAEAEA;
    width: 60px; height: 60px; object-fit: cover;
}
.st-emotion-cache-17lntch button {
    padding: 0; margin: 0; border: none; background: none;
}
.sidebar-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 5px; border-radius: 10px; margin-bottom: 10px;
    transition: background-color 0.2s;
}
.sidebar-item:hover { background-color: #f0f0f5; }
.remove-btn {
    color: #888; border: none; background: none; font-size: 1.2rem;
    cursor: pointer; padding: 5px;
}
.remove-btn:hover { color: #ff4b4b; }

/* UPDATED: Potential Label Styling */
.potential-label {
    padding: 6px 14px; /* Increased padding */
    border-radius: 10px;
    font-weight: 700;   /* Bolder text */
    font-size: 1.1rem;  /* Increased font size */
    display: inline-block;
    text-align: center;
}
.high-potential { background-color: #d4edda; color: #155724; }
.moderate-potential { background-color: #fff3cd; color: #856404; }
.low-potential { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True) # Note: CSS is collapsed for brevity

# --- (All Engine Classes and Helper Functions are here and unchanged) ---
class ItemIdentifier:
    # ... (code is unchanged)
    pass
class ListingQualityEvaluator:
    # ... (code is unchanged)
    pass
class PrismScoreEvaluator:
    # ... (code is unchanged)
    pass
def load_and_process_data(csv_path):
    # ... (code is unchanged)
    pass
def get_rating_stars(rating_text: str):
    # ... (code is unchanged)
    pass
def clean_sales_text(sales_text: str):
    # ... (code is unchanged)
    pass
def generate_amazon_link(title: str):
    # ... (code is unchanged)
    pass


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
        st.session_state.saved_products = []

    # --- UPDATED: Sidebar with Remove Button ---
    with st.sidebar:
        st.subheader("Your Shortlist")
        if not st.session_state.saved_products:
            st.info("Click the '⭐️ Save Product' button to add items here.")
        else:
            # Create a copy to iterate over, allowing us to modify the original list
            for saved_index in st.session_state.saved_products[:]:
                product = df.iloc[saved_index]
                
                # Use columns for layout: Image/Title on left, Remove button on right
                col1, col2 = st.columns([5, 1])
                with col1:
                    # Use markdown to make the whole item clickable
                    st.markdown(f"""
                    <div class="sidebar-item">
                        <img src="{product.get('Image', '')}" width="60">
                        <span style="margin-left: 10px;">{product.get('Title', '')[:30]}...</span>
                    </div>
                    """, unsafe_allow_html=True)
                    # This part is tricky in Streamlit. A full clickable div is complex.
                    # For simplicity, we'll keep the button on the image itself.
                    
                with col2:
                    # Button to remove the specific item
                    if st.button(f"🗑️", key=f"remove_{saved_index}", help="Remove from shortlist"):
                        st.session_state.saved_products.remove(saved_index)
                        st.rerun()

            if st.button("Clear All", use_container_width=True, type="secondary"):
                st.session_state.saved_products = []
                st.rerun()

    # --- Main Dashboard ---
    # (The main dashboard layout code is here and is unchanged)
    # ...

if __name__ == "__main__":
    main()
