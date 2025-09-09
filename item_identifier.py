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
        self._download_nltk_data()
        self._noise_words = {
            "men's", "women's", "boy's", "girl's", 'mens', 'womens', 'for', 
            'and', 'with', 'the', 'a', 'in', 'of', 'per', 'pack', 'set'
        }
        self._spec_pattern = re.compile(r'\b(\d+l|\d+ml|\d+mm|\d+g|\d+kg)\b')

    @st.cache_resource
    def _download_nltk_data(_self):
        """
        Downloads the necessary NLTK corpora for TextBlob's tagger.
        Uses a general LookupError to be compatible with different NLTK versions.
        """
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError: # This is the fix. LookupError is more general.
            nltk.download('averaged_perceptron_tagger')

    def identify(self, title: str) -> str:
        """
        Processes a title using grammar-based filtering to find the core item.
        """
        if not isinstance(title, str):
            return "Not Found"

        golden_zone = title[:50]
        cleaned_zone = self._spec_pattern.sub('', golden_zone.lower())
        
        blob = TextBlob(cleaned_zone)
        
        item_words = []
        for word, tag in blob.tags:
            # JJ, JJR, JJS are codes for adjectives.
            if tag not in ['JJ', 'JJR', 'JJS'] and word not in self._noise_words:
                item_words.append(word)

        if not item_words:
            return "Not Found"

        identified_phrase = " ".join(item_words)
        return identified_phrase.title()
