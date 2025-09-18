# File: item_identifier.py
import spacy
import streamlit as st

class ItemIdentifier:
    """
    Identifies the core item from a product title using the spaCy NLP library.
    """
    def __init__(self):
        self._nlp = self._load_model()
        self._noise_words = {
            'men', 'women', 'kids', 'man', 'woman', 'boys', 'girls', 'mens', 'womens',
            'home', 'gym', 'workout', 'exercise', 'training', 'gear', 'for', 'and', 'with',
            'the', 'a', 'in', 'of', 'per', 'pack', 'set', 'combo', 'kit'
        }

    @st.cache_resource
    def _load_model(_self):
        """Loads the spaCy model, which was installed via requirements.txt."""
        return spacy.load("en_core_web_sm")

    def identify(self, title: str) -> str:
        """
        Processes a title to find the most likely noun phrase representing the core item.
        """
        if not isinstance(title, str):
            return "Not Found"

        # Process the first part of the title before a separator
        core_title = title.split('|')[0].split(',')[0]
        doc = self._nlp(core_title)

        # Find all noun phrases (e.g., "Sports Shoes", "Wrist Support")
        noun_chunks = [chunk.text.strip() for chunk in doc.noun_chunks]

        if not noun_chunks:
            return "Not Found"

        # Smart Heuristic:
        # 1. Ignore the first chunk if it's likely just the brand name.
        # 2. Find the best remaining chunk that isn't just noise.
        start_index = 1 if len(noun_chunks) > 1 else 0
        for chunk in noun_chunks[start_index:]:
            if chunk.lower() not in self._noise_words:
                return chunk.title()
        
        # Fallback to the first chunk if no other good ones are found
        return noun_chunks[0].title()
