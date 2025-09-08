# File: item_identifier.py
import spacy
import streamlit as st
import spacy.cli

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
        """
        Loads the spaCy model. If not found, it downloads it automatically.
        """
        model_name = "en_core_web_sm"
        try:
            # Try to load the model directly
            return spacy.load(model_name)
        except OSError:
            # If the model is not found, download it and then load it.
            st.info(f"Downloading NLP model ({model_name})... This may take a moment.")
            spacy.cli.download(model_name)
            return spacy.load(model_name)

    def _get_noise_words(self):
        """Defines a set of common words to ignore for cleaner results."""
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

        doc = self._nlp(title.lower())

        potential_items = []
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()

            if chunk_text in self._noise_words:
                continue

            if any(noise_word in chunk_text.split() for noise_word in self._noise_words):
                continue

            potential_items.append(chunk_text)

        if potential_items:
            return potential_items[0].title()

        return "Not Found"
