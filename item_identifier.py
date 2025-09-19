# File: item_identifier.py
import spacy
import streamlit as st

class ItemIdentifier:
    """
    Identifies the core item from a product title using spaCy's
    grammatical dependency parsing.
    """
    def __init__(self):
        self._nlp = self._load_model()
        self._noise_words = {'men', 'women', 'kids', 'gear', 'for'}

    @st.cache_resource
    def _load_model(_self):
        """Loads the spaCy model, installed via requirements.txt."""
        return spacy.load("en_core_web_sm")

    def identify(self, title: str) -> str:
        """
        Processes a title to find the core item by analyzing its grammatical structure.
        """
        if not isinstance(title, str):
            return "Not Found"

        # --- UPDATED LOGIC ---
        # Only split the title by the '|' character.
        core_title = title.split('|')[0]
        doc = self._nlp(core_title)

        # Find the grammatical root of the title
        root = None
        for token in doc:
            if token.dep_ == "ROOT":
                root = token
                break
        
        if not root:
            return "Not Found"

        # Find all words directly related to the root (the subject/object)
        # and ignore prepositional phrases (the "use case")
        item_words = []
        for child in root.subtree:
            # Ignore words that are part of a prepositional phrase (like "for Toilet")
            if child.dep_ == 'pobj' or child.head.dep_ == 'prep':
                continue
            # Keep nouns, adjectives, and compound words related to the root
            if child.pos_ in ['NOUN', 'PROPN', 'ADJ'] and child.text.lower() not in self._noise_words:
                item_words.append(child.text)
        
        if not item_words:
            # Fallback for very simple titles
            if root.text.lower() not in self._noise_words:
                return root.text.title()
            else:
                return "Not Found"

        return " ".join(item_words).title()
    
