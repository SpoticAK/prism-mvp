# File: item_identifier.py
import spacy
import streamlit as st
import re

class ItemIdentifier:
    """
    Identifies the core item from a product title using spaCy's
    grammatical dependency parsing combined with custom rules.
    """
    def __init__(self):
        self._nlp = self._load_model()
        self._noise_words = {
            'men', 'women', 'kids', 'man', 'woman', 'boys', 'girls', 'mens', 'womens',
            'home', 'gym', 'workout', 'exercise', 'training', 'gear', 'for', 'and', 'with',
            'the', 'a', 'in', 'of', 'per', 'pack', 'set', 'combo', 'kit', 'accessories'
        }
        # A regex to find and remove alphanumeric model numbers like PUK3502GS
        self._model_number_pattern = re.compile(r'\b[a-zA-Z]+\d+[a-zA-Z0-9]*\b|\b\d+[a-zA-Z]+\b')

    @st.cache_resource
    def _load_model(_self):
        """Loads the spaCy model, which was installed via requirements.txt."""
        return spacy.load("en_core_web_sm")

    def identify(self, title: str) -> str:
        """
        Processes a title to find the core item by analyzing its grammatical structure.
        """
        if not isinstance(title, str):
            return "Not Found"

        # 1. Isolate the Core Title (using only '|' as a separator)
        core_title = title.split('|')[0].strip()
        
        # 2. Pre-Filter: Remove serial/model numbers before grammatical analysis
        cleaned_title = self._model_number_pattern.sub('', core_title).strip()
        
        doc = self._nlp(cleaned_title)
        
        # 3. Find the Grammatical Root
        root = None
        for token in doc:
            if token.dep_ == "ROOT":
                root = token
                break
        
        if not root:
            return "Not Found"

        # 4. Reconstruct the Core Product Phrase around the root
        item_words = []
        for child in root.subtree:
            # Ignore words that are part of a prepositional phrase (the "use case")
            if child.dep_ == 'pobj' or child.head.dep_ == 'prep':
                continue
            # Keep nouns, adjectives, and compound words, but ignore noise
            if child.pos_ in ['NOUN', 'PROPN', 'ADJ'] and child.text.lower() not in self._noise_words:
                item_words.append(child.text)
        
        # 5. Post-Filter: Handle the Brand Name
        # If the first word of our result is the same as the first word of the title, it's likely the brand.
        if len(item_words) > 1 and item_words[0].lower() == core_title.split(' ')[0].lower():
            item_words = item_words[1:]

        if not item_words:
            return "Not Found"

        return " ".join(item_words).title()
