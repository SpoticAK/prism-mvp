# File: item_identifier.py
import re
import streamlit as st
from textblob import TextBlob
import nltk

class ItemIdentifier:
    """
    Identifies the core item from a product title using Part-of-Speech (POS) tagging.
    """
    def __init__(self):
        # Download necessary NLTK data for TextBlob's POS tagger.
        # This is a one-time, lightweight download managed by Streamlit's cache.
        self._download_nltk_data()
        
        # A curated list for possessives and other non-adjective noise words.
        self._noise_words = {
            "men's", "women's", "boy's", "girl's", 'mens', 'womens',
            'for', 'and', 'with', 'the', 'a', 'in', 'of', 'per', 'pack', 'set'
        }
        self._spec_pattern = re.compile(r'\b(\d+l|\d+ml|\d+mm|\d+g|\d+kg)\b')

    @st.cache_resource
    def _download_nltk_data(_self):
        """Downloads the necessary corpora for TextBlob's tagger."""
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except nltk.downloader.DownloadError:
            nltk.download('averaged_perceptron_tagger')

    def identify(self, title: str) -> str:
        """
        Processes a title using grammar-based filtering to find the core item.
        """
        if not isinstance(title, str):
            return "Not Found"

        # 1. Isolate the 50-character "Golden Zone"
        golden_zone = title[:50]

        # 2. Advanced Filtering using Grammar
        # Remove specifications first (e.g., "20l")
        cleaned_zone = self._spec_pattern.sub('', golden_zone.lower())
        
        # Analyze the grammar of the zone
        blob = TextBlob(cleaned_zone)
        
        item_words = []
        for word, tag in blob.tags:
            # Check if the word is NOT an adjective (JJ, JJR, JJS) and NOT in our noise list
            if tag not in ['JJ', 'JJR', 'JJS'] and word not in self._noise_words:
                item_words.append(word)

        if not item_words:
            return "Not Found"

        # 3. Identify the first coherent noun phrase
        # We join the remaining clean words (mostly nouns) from left to right.
        identified_phrase = " ".join(item_words)

        return identified_phrase.title()
