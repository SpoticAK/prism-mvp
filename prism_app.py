import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="PRISM MVP",
    page_icon="🚀",
    layout="wide"
)

# --- Data Loading ---
@st.cache_data
def load_data(csv_path):
    """Loads the product data from your CSV file."""
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        st.error(f"File not found: {csv_path}. Please make sure 'products.csv' is in your GitHub repository.")
        st.stop()

# --- Session State Initialization ---
if 'product_index' not in st.session_state:
    st.session_state.product_index = 0

# --- Main App ---
st.title("🚀 PRISM: Your Product Research Assistant")
st.markdown("This is the foundational dashboard. The analysis 'tools' will be plugged in later.")

# Load the data from your products.csv file.
df = load_data('products.csv')

# --- Button to Navigate Products ---
if st.button("Next Product ➡️"):
    st.session_state.product_index = (st.session_state.product_index + 1) % len(df)

st.divider()

# Get the data for the current product.
current_product = df.iloc[st.session_state.product_index]

# --- Dashboard Layout ---
col1, col2 = st.columns([1, 2])

# --- Left Column: Product Image ---
with col1:
    st.header("Product Image")
    # Using the exact column name from your file: 'Image'
    if 'Image' in current_product and pd.notna(current_product['Image']):
        st.image(current_product['Image'], use_column_width=True)
    else:
        st.warning("No image found for this product.")

# --- Right Column: Product Data & Future Analysis ---
with col2:
    st.header("Product Details")
    # Using the exact column name from your file: 'Title'
    st.subheader(current_product.get('Title', 'No Title Available'))

    # Using the exact column names from your file for all metrics.
    price = current_product.get('Price', 'N/A')
    sales = current_product.get('Monthly Sales', 'N/A')
    rating = current_product.get('Ratings', 'N/A')
    reviews = current_product.get('Review', 'N/A')

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric(label="Price (₹)", value=f"₹{price}")
    metric_col2.metric(label="Monthly Sales", value=sales)
    metric_col1.metric(label="Rating", value=rating) # The ⭐ emoji is removed as the rating is text now
    metric_col2.metric(label="Total Reviews", value=reviews)

    st.divider()

    # --- Placeholders for our future 'tools' ---
    st.header("PRISM Analysis (Coming Soon)")
    st.info("The 'Identified Item' and 'PRISM Score' will appear here once the analysis tools are built and plugged in.")
  
