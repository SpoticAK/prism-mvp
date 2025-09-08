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
if 'corrections' not in st.session_state:
    st.session_state.corrections = []

# --- Data Loading ---
@st.cache_data
def load_data():
    """Loads the product data from the GitHub repository."""
    # Construct the raw GitHub URL for the CSV file
    # IMPORTANT: Replace 'your-github-username' with your actual GitHub username
    github_user = "spoticak"
    repo_name = "prism-mvp"
    file_path = "products.csv"
    
    url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/main/{file_path}"
    
    df = pd.read_csv(url)
    return df

# --- Main App Logic ---
st.title("PRISM: Product Intelligence & Sales Monitoring")

try:
    # Load the data when the app starts
    df = load_data()

    # --- Data Validation ---
    required_columns = ['Title', 'Price', 'Monthly Sales']
    if not all(col in df.columns for col in required_columns):
        st.error(f"Error: CSV must contain the following columns: {', '.join(required_columns)}")
    else:
        # --- Data Processing (run only if not already processed) ---
        if st.session_state.product_data is None:
            df['Cleaned Sales'] = df['Monthly Sales'].str.replace(r'\D', '', regex=True).astype(int)
            
            identifier = ItemIdentifier()
            df['Identified Item'] = df['Title'].apply(identifier.identify)
            
            df['Correct?'] = pd.Series([None]*len(df), dtype='boolean')
            df['Corrected Label'] = pd.Series([""]*len(df), dtype='str')

            st.session_state.product_data = df

        # --- Main Dashboard Display ---
        st.success("Dashboard generated from `products.csv` in your repository.")

        # --- Key Metrics ---
        total_sales = st.session_state.product_data['Cleaned Sales'].sum()
        average_price = st.session_state.product_data['Price'].mean()
        unique_items = st.session_state.product_data['Identified Item'].nunique()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Monthly Sales", f"{total_sales:,}")
        col2.metric("Average Product Price", f"₹{average_price:,.2f}")
        col3.metric("Unique Items Identified", f"{unique_items}")

        st.markdown("---")

        # --- Charts ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 10 Products by Sales")
            top_10_sales = st.session_state.product_data.nlargest(10, 'Cleaned Sales')
            st.bar_chart(top_10_sales, x='Title', y='Cleaned Sales')

        with col2:
            st.subheader("Top 10 Identified Items by Sales")
            top_items = st.session_state.product_data.groupby('Identified Item')['Cleaned Sales'].sum().nlargest(10)
            st.bar_chart(top_items)
        
        st.markdown("---")

        # --- Feedback Section ---
        st.subheader("Review and Correct Identifications")
        st.markdown("Use this table to correct any misidentified items. Your feedback will help improve the engine.")
        
        edited_df = st.data_editor(
            st.session_state.product_data[['Title', 'Identified Item', 'Correct?', 'Corrected Label']],
            column_config={
                "Correct?": st.column_config.CheckboxColumn("Correct?", default=False)
            },
            use_container_width=True,
            num_rows="dynamic",
            key="data_editor"
        )

        if st.button("Save Corrections", type="primary"):
            corrections_to_save = edited_df[edited_df['Correct?'].notna()]
            st.session_state.corrections.extend(corrections_to_save.to_dict('records'))
            st.success(f"{len(corrections_to_save)} corrections have been staged.")
            st.info("In a full application, this data would be written to `corrections.csv` on GitHub.")

except Exception as e:
    st.error(
        f"An error occurred while loading data from GitHub: {e}\n\n"
        "**Please check the following:**\n"
        "1. You have updated the `github_user` variable in the code with your GitHub username.\n"
        "2. The `products.csv` file exists in the root of your `prism-mvp` repository."
    )
