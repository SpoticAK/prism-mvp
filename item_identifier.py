# File: item_identifier.py
import spacy
import streamlit as st

class ItemIdentifier:
    """
    Tool #1: A self-contained engine to identify items from product titles.
    """
    def __init__(self):
        """Loads the NLP model and defines noise words when the engine starts."""
        self._nlp = self._load_model()
        self._noise_words = self._get_noise_words()

    # Use Streamlit's caching to load the large NLP model only once.
    @st.cache_resource
    def _load_model(_self):
        """Loads the spaCy NLP model."""
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            # This is a fallback for local testing if the model isn't installed.
            print("Downloading 'en_core_web_sm' model...")
            spacy.cli.download("en_core_web_sm")
            return spacy.load("en_core_web_sm")

    def _get_noise_words(self):
        """Defines a set of common words to ignore for cleaner results."""
        # We can add more words to this set over time to improve accuracy.
        return {
            'men', 'women', 'kids', 'man', 'woman', 'boys', 'girls',
            'home', 'gym', 'workout', 'exercise', 'training', 'gear',
            'combo', 'kit', 'pack', 'set', 'material', 'bands',
            'anti', 'slip', 'multi', 'mens', 'womens',
            'for', 'and', 'with', 'the', 'a', 'in', 'of', 'per'
        }

    def identify(self, title: str) -> str:
        """
        The main method. It processes a title and returns the identified item.
        """
        if not isinstance(title, str):
            return "Invalid Title"

        # Process the title with the NLP model.
        doc = self._nlp(title.lower())
        
        potential_items = []
        # spaCy breaks the title into "noun chunks" (e.g., "yoga mats", "anti slip eva material").
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()
            
            # Rule 1: Skip if the entire chunk is just a noise word.
            if chunk_text in self._noise_words:
                continue
            
            # Rule 2: Skip if the chunk contains any noise words.
            if any(noise_word in chunk_text.split() for noise_word in self._noise_words):
                continue
            
            potential_items.append(chunk_text)
        
        # If we found any valid items, return the first and most likely one.
        if potential_items:
            return potential_items[0].title() # .title() capitalizes it nicely
        
        return "Not Found"
