# File: prism_app.py
import streamlit as st
import pandas as pd
import re
import math

# --- 1. Page & Style Configuration ---
st.set_page_config(page_title="PRISM Product View", layout="centered")

# Inject custom CSS for Apple-inspired aesthetics
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main app container */
    .main .block-container {
        padding: 2rem;
        border-radius: 1rem;
    }
    
    /* Product Title */
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }

    /* Price */
    .stMetric .st-ae {
        font-size: 2rem !important;
        font-weight: 600 !important;
    }

    /* "Next Item" Button */
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 0.75rem;
        font-weight: 600;
    }

    /* PRISM ANALYSIS Section */
    .prism-analysis-section {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e6e6e6;
    }
    </style>
""", unsafe_allow_html=True)
