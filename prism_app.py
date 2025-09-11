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
    /* Base Styles */
    html, body, [class*="st-"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        background-color: #FFFFFF; color: #212121;
    }
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #1c1c1e; font-weight: 600; }
    h1 { font-size: 2rem; } h2 { font-size: 1.5rem; } h3 { font-size: 1.15rem; }
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

    /* Sidebar Styling */
    [data-testid="stSidebar"] [data-testid="stImage"] > img {
        width: 60px !important;
        height: 60px !important;
        border-radius: 8px;
        object-fit: cover;
    }
    .sidebar-item-container {
        padding: 10px; border-radius: 10px; margin-bottom: 10px;
        background-color: #f9f9f9;
    }
    .remove-btn {
        color: #aaa; border: none; background: none; font-size: 1.1rem; cursor: pointer;
    }
    .remove-btn:hover { color: #ff4b4b; }

    /* Potential Label & Score Bar Styling */
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

# --- Data Loading and Helper Functions ---
@st.cache_data
def load_and_process_data(csv_path):
    try:
        df = pd.read_csv(csv_path, dtype={'Monthly Sales': str})
    except FileNotFoundError:
        return None

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

# --- Main App Execution ---
def main():
    st.title("PRISM")
    st.markdown("Product Research & Insight System")
    
    df = load_and_process_data('products.csv')
    if df is None:
        st.error("File not found: 'products.csv'. Please ensure it is in your GitHub repository.")
        st.stop()

    st.caption(f"Loaded and shuffled {len(df)} products for discovery.")
    st.divider()

    if 'shuffled_indices' not in st.session_state:
        indices = list(df.index)
        random.shuffle(indices)
        st.session_state.shuffled_indices = indices
        st.session_state.product_pointer = 0
        try:
            query_params = st.query_params.to_dict()
            saved_from_url = [int(i) for i in query_params.get("saved", [])]
            st.session_state.saved_products = list(dict.fromkeys(saved_from_url))
            st.session_state.notes = {int(k.split('_')[1]): v[0] for k, v in query_params.items() if k.startswith("note_")}
        except:
             st.session_state.saved_products = []
             st.session_state.notes = {}

        if st.session_state.saved_products:
            first_saved_index = st.session_state.saved_products[0]
            if first_saved_index in st.session_state.shuffled_indices:
                 st.session_state.product_pointer = st.session_state.shuffled_indices.index(first_saved_index)
            else:
                 st.session_state.product_pointer = 0
        else:
            st.session_state.product_pointer = 0

    with st.sidebar:
        st.subheader("Your Shortlist")
        if not st.session_state.saved_products:
            st.info("Click '⭐️ Save' to add items here.")
        else:
            for saved_index in st.session_state.saved_products[:]:
                product = df.iloc[saved_index]
                with st.container():
                    st.markdown("<div class='sidebar-item-container'>", unsafe_allow_html=True)
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.image(product.get('Image'), width=60, caption=product.get('Title')[:25]+"...")
                    with col2:
                        if st.button("❌", key=f"remove_{saved_index}", help="Remove from shortlist"):
                            st.session_state.saved_products.remove(saved_index)
                            if saved_index in st.session_state.notes:
                                del st.session_state.notes[saved_index]
                            st.query_params["saved"] = [str(i) for i in st.session_state.saved_products]
                            st.query_params.pop(f"note_{saved_index}", None)
                            st.rerun()
                    
                    note_text = st.text_input("Add a note...", key=f"note_input_{saved_index}", value=st.session_state.notes.get(saved_index, ""))
                    if note_text != st.session_state.notes.get(saved_index, ""):
                        st.session_state.notes[saved_index] = note_text
                        st.query_params[f"note_{saved_index}"] = note_text
                        st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)

            if st.button("Clear All", use_container_width=True, type="secondary"):
                st.session_state.saved_products = []
                st.session_state.notes = {}
                st.query_params.clear()
                st.rerun()

    current_index = st.session_state.shuffled_indices[st.session_state.product_pointer]
    current_product = df.iloc[current_index]

    col1, col2 = st.columns([2, 3], gap="large")

    with col1:
        st.image(current_product.get('Image', ''), use_container_width=True)
        nav_col1, nav_col2 = st.columns(2)
        if nav_col1.button("← Previous", use_container_width=True):
            st.session_state.product_pointer = (st.session_state.product_pointer - 1) % len(df)
            st.rerun()
        if nav_col2.button("Next →", use_container_width=True):
            st.session_state.product_pointer = (st.session_state.product_pointer + 1) % len(df)
            st.rerun()

    with col2:
        st.markdown(f"### {current_product.get('Title', 'No Title Available')}")
        link_col, save_col = st.columns([3, 1])
        link_col.link_button("View on Amazon ↗", url=generate_amazon_link(current_product.get('Title', '')), use_container_width=True)
        if save_col.button("⭐️ Save", use_container_width=True):
            if current_index not in st.session_state.saved_products:
                st.session_state.saved_products.append(current_index)
                st.query_params["saved"] = [str(i) for i in st.session_state.saved_products]
                st.rerun()
        
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
        prism_score = int(current_product.get('PRISM Score', 0))

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
            <b>Identified Item:</b> {current_product.get('Identified Item', 'N/A')}<br>
            <b>Listing Quality:</b> {current_product.get('Listing Quality', 'N/A')}
        </div>
        """, unsafe_allow_html=True)

        if current_product.get('Missing Data', False):
            st.markdown("<div class='missing-data-flag'>*Score calculated with some data unavailable.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
