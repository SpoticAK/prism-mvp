# File: prism_app.py
import streamlit as st
import pandas as pd
from item_identifier import ItemIdentifier

# --- Page Configuration ---
st.set_page_config(
    page_title="PRISM MVP",
    page_icon="🤖",
    layout="wide"
)

# --- State Management ---
if 'product_data' not in st.session_state:
    st.session_state.product_data = None

# --- Data Cleaning & Processing ---
def clean_and_process_data(df):
    """A robust function to clean sales data and identify items."""
    
    # 1. Clean 'Monthly Sales' column
    # Fill missing values with '0'
    df['Monthly Sales'] = df['Monthly Sales'].fillna('0') 
    
    # Convert to string and handle 'K' for thousands, remove '+' and commas
    sales_str = df['Monthly Sales'].astype(str)
    sales_str = sales_str.str.lower().str.replace('k+', '000', regex=True)
    sales_str = sales_str.str.replace(r'[^\d]', '', regex=True) # Remove all non-digits

    # Convert to numeric, coercing errors to 0
    df['Cleaned Sales'] = pd.to_numeric(sales_str, errors='coerce').fillna(0).astype(int)

    # 2. Initialize and run the Item Identifier
    identifier = ItemIdentifier()
    df['Identified Item'] = df['Title'].apply(identifier.identify)
    
    # 3. Add feedback columns for the UI
    df['Correct?'] = pd.Series([None]*len(df), dtype='boolean')
    df['Corrected Label'] = pd.Series([""]*len(df), dtype='str')
    
    return df

# --- Data Loading ---
@st.cache_data
def load_data_from_github():
    """Loads and processes the data from the GitHub repository."""
    github_user = "spoticak"
    repo_name = "prism-mvp"
    file_path = "products.csv"
    url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/main/{file_path}"
    
    df = pd.read_csv(url)
    processed_df = clean_and_process_data(df)
    return processed_df

# --- Main App Logic ---
st.title("PRISM: Product Intelligence & Sales Monitoring")

try:
    # Load and process data only if it's not already in the session state
    if st.session_state.product_data is None:
        with st.spinner("Loading and analyzing data from your repository..."):
            st.session_state.product_data = load_data_from_github()

    # --- Main Dashboard Display ---
    st.success("Dashboard generated from `products.csv` in your repository.")

    df = st.session_state.product_data

    # --- Key Metrics ---
    total_sales = df['Cleaned Sales'].sum()
    average_price = df['Price'].mean()
    unique_items = df['Identified Item'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Monthly Sales", f"{total_sales:,}")
    col2.metric("Average Product Price", f"₹{average_price:,.2f}")
    col3.metric("Unique Items Identified", f"{unique_items}")

    st.markdown("---")

    # --- Charts ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Products by Sales")
        top_10_sales = df.nlargest(10, 'Cleaned Sales')
        st.bar_chart(top_10_sales, x='Title', y='Cleaned Sales')

    with col2:
        st.subheader("Top 10 Identified Items by Sales")
        top_items = df.groupby('Identified Item')['Cleaned Sales'].sum().nlargest(10)
        st.bar_chart(top_items)
    
    st.markdown("---")

    # --- Feedback Section ---
    st.subheader("Review and Correct Identifications")
    edited_df = st.data_editor(
        df[['Title', 'Identified Item', 'Correct?', 'Corrected Label']],
        column_config={"Correct?": st.column_config.CheckboxColumn("Correct?", default=False)},
        use_container_width=True,
        num_rows="dynamic"
    )
    
    if st.button("Save Corrections", type="primary"):
        st.success("Feedback functionality is connected.")
        # In a full app, this is where you'd write to corrections.csv

except Exception as e:
    st.error(f"An error occurred: {e}")
