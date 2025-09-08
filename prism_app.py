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
# Initialize session state to hold data and feedback
if 'product_data' not in st.session_state:
    st.session_state.product_data = None
if 'corrections' not in st.session_state:
    st.session_state.corrections = []

# --- Main App Logic ---
st.title("PRISM: Product Item Identifier")
st.markdown("Upload your `products.csv` file to begin.")

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type="csv",
    help="The CSV should contain a column named 'Title' with product names."
)

if uploaded_file is not None:
    try:
        # Load and process data only once per upload
        if st.session_state.product_data is None:
            df = pd.read_csv(uploaded_file)
            
            # Ensure 'Title' column exists
            if 'Title' not in df.columns:
                st.error("Error: The CSV file must contain a 'Title' column.")
            else:
                # Initialize the Item Identifier engine
                identifier = ItemIdentifier()
                
                # Create the 'Identified Item' column
                df['Identified Item'] = df['Title'].apply(identifier.identify)
                
                # --- Add columns for the feedback UI ---
                df['Correct?'] = pd.Series([None]*len(df), dtype='boolean')
                df['Corrected Label'] = pd.Series([""]*len(df), dtype='str')
                
                # Store the processed dataframe in the session state
                st.session_state.product_data = df

        st.success("File processed successfully!")

        # --- Display the Interactive Data Editor ---
        st.subheader("Review and Correct Identifications")
        
        edited_df = st.data_editor(
            st.session_state.product_data,
            column_config={
                "Correct?": st.column_config.CheckboxColumn(
                    "Correct?",
                    help="Check if the 'Identified Item' is correct.",
                    default=False,
                )
            },
            use_container_width=True,
            num_rows="dynamic",
            key="data_editor"
        )

        # --- Save Corrections ---
        if st.button("Save Corrections", type="primary"):
            # Find rows where feedback was given
            corrections_df = edited_df[edited_df['Correct?'].notna()]
            
            for index, row in corrections_df.iterrows():
                feedback = {
                    "Title": row["Title"],
                    "Original_Guess": row["Identified Item"],
                    "Is_Correct": row["Correct?"],
                    "User_Correction": row["Corrected Label"] if not row["Correct?"] else ""
                }
                st.session_state.corrections.append(feedback)

            st.success(f"{len(st.session_state.corrections)} corrections have been saved for this session.")
            st.info("In a full application, this data would be sent to a backend database.")
            st.write(st.session_state.corrections) # Display saved corrections for verification

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.session_state.product_data = None # Reset on error
