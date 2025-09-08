# File: prism_app.py
import streamlit as st
import pandas as pd
import re
from item_identifier import ItemIdentifier

# --- Page Configuration ---
st.set_page_config(
    page_title="PRISM MVP",
    page_icon="🤖",
    layout="wide"
)

# --- Data Cleaning & Processing ---
def clean_sales_value(sale_entry):
    """
    A robust function to clean a single sales data entry.
    Handles formats like '500+', '3K+', '1,939', and empty/non-string values.
    """
    if pd.isna(sale_entry) or not isinstance(sale_entry, str):
        return 0
    
    s = str(sale_entry).lower().strip().split(' ')[0]
    s = s.replace(',', '').replace('+', '')
    
    value = 0
    try:
        if 'k' in s:
            value = float(s.replace('k', '')) * 1000
        else:
            numeric_part = re.sub(r'[^\d.]', '', s)
            if numeric_part:
                value = float(numeric_part)
    except (ValueError, TypeError):
        return 0 # Default to 0 if any conversion fails
            
    return int(value)

@st.cache_data
def load_and_process_data():
    """Loads data from GitHub and performs all cleaning and processing."""
    github_user = "spoticak"
    repo_name = "prism-mvp"
    file_path = "products.csv"
    url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/main/{file_path}"
    
    df = pd.read_csv(url)
    df['Cleaned Sales'] = df['Monthly Sales'].apply(clean_sales_value)
    
    identifier = ItemIdentifier()
    df['Identified Item'] = df['Title'].apply(identifier.identify)
    
    return df

# --- Main App ---
st.title("PRISM: Product Intelligence & Sales Monitoring")

try:
    with st.spinner("Loading and analyzing data from your repository..."):
        df = load_and_process_data()

    st.success("Dashboard generated from `products.csv` in your repository.")

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
        st.bar_chart(df.nlargest(10, 'Cleaned Sales'), x='Title', y='Cleaned Sales')
    with col2:
        st.subheader("Top 10 Identified Items by Sales")
        st.bar_chart(df.groupby('Identified Item')['Cleaned Sales'].sum().nlargest(10))
    
    st.markdown("---")

    # --- Data Table ---
    st.subheader("Processed Data")
    st.dataframe(df[['Title', 'Identified Item', 'Price', 'Cleaned Sales']])

except Exception as e:
    st.error(f"An error occurred: {e}")
