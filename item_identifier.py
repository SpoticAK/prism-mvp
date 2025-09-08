# File: item_identifier.py
import streamlit as st

class ItemIdentifier:
    """
    Tool #1: A self-contained engine to identify items from product titles.
    This version uses simple text processing instead of a heavy NLP model.
    """
    def __init__(self):
        """Defines noise words when the engine starts."""
        self._noise_words = self._get_noise_words()

    def _get_noise_words(self):
        """Defines a set of common words to ignore for cleaner results."""
        return {
            'men', 'women', 'kids', 'man', 'woman', 'boys', 'girls',
            'home', 'gym', 'workout', 'exercise', 'training', 'gear',
            'combo', 'kit', 'pack', 'set', 'material', 'bands', 'anti',
            'slip', 'multi', 'mens', 'womens', 'for', 'and', 'with', 'the',
            'a', 'in', 'of', 'per', 'solid', 'pack', 'pcs'
        }

    def identify(self, title: str) -> str:
        """
        The main method. It processes a title and returns the identified item.
        """
        if not isinstance(title, str):
            return "Invalid Title"

        # Split title into words, remove noise, and find the first likely item
        words = title.lower().split()

        # Find the first word that isn't a noise word
        for word in words:
            clean_word = ''.join(e for e in word if e.isalnum())
            if clean_word and clean_word not in self._noise_words:
                return clean_word.title()

        return "Not Found"
