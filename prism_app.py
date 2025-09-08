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

# --- State Management ---
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

# --- Data Cleaning & Processing ---
def clean_sales_value(sale_entry):
    """
    A robust function to clean a single sales data entry.
    Handles formats like '500+', '3K+', '1,939', and empty values.
    """
    # If the entry is missing or not a string, treat as 0
    if pd.isna(sale_entry) or not isinstance(sale_entry, str):
        return 0
    
    # Standardize the string
    s = str(sale_entry).lower().strip()
    
    # Isolate the first part of the string (e.g., "500+" from "500+ bought...")
    s = s.split(' ')[0]

    # Remove commas and '+' signs
    s = s.replace(',', '').replace('+', '')
    
    value = 0
    try:
        # Handle 'k' for thousands
        if 'k' in s:
            s = s.replace('k', '')
            value = float(s) * 1000
        else:
            # Handle regular numbers
            numeric_part = re.sub(r'[^\d.]', '', s)
            if numeric_part:
                value = float(numeric_part)
    except (ValueError, TypeError):
        # If any conversion fails, default to 0
        return 0
            
    return int(value)

@st.cache_data
def load_and_process_data():
    """Loads data from GitHub and performs all cleaning and processing."""
    github_user = "spoticak"
    repo_name = "prism-mvp"
    file_path = "products.csv"
    url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/main/{file_path}"
    
    df = pd.read_csv(url)
    
    # Apply the robust cleaning function to the 'Monthly Sales' column
    df['Cleaned Sales'] = df['Monthly Sales'].apply(clean_sales_value)
    
    # Initialize and run the Item Identifier
    identifier = ItemIdentifier()
    df['Identified Item'] = df['Title'].apply(identifier.identify)
    
    # Add feedback columns for the UI
    df['Correct?'] = pd.Series([None]*len(df), dtype='boolean')
    df['Corrected Label'] = pd.Series([""]*len(df), dtype='str')
    
    return df

# --- Main App ---
st.title("PRISM: Product Intelligence & Sales Monitoring")

try:
    # Load and process data once and store in session state
    if st.session_state.processed_data is None:
        with st.spinner("Loading and analyzing data from your repository..."):
            st.session_state.processed_data = load_and_process_data()

    df = st.session_state.processed_data

    # --- Main Dashboard Display ---
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

    # --- Feedback Section ---
    st.subheader("Review and Correct Identifications")
    st.data_editor(
        df[['Title', 'Identified Item', 'Correct?', 'Corrected Label']],
        column_config={"Correct?": st.column_config.CheckboxColumn("Correct?", default=False)},
        use_container_width=True,
        num_rows="dynamic"
    )
    
    if st.button("Save Corrections", type="primary"):
        st.success("Feedback functionality is ready.")

except Exception as e:
    st.error(f"An error occurred: {e}")
