# File: item_identifier.py
import spacy
import streamlit as st
import re

class ItemIdentifier:
    """
    Identifies the core item from a product title using spaCy's grammatical
    analysis and a "candidate and score" logic.
    """
    def __init__(self):
        self._nlp = self._load_model()
        self._model_number_pattern = re.compile(r'\b[a-zA-Z]+\d+[a-zA-Z0-9]*\b|\b\d+[a-zA-Z]+\b')

    @st.cache_resource
    def _load_model(_self):
        """Loads the spaCy model, installed via requirements.txt."""
        return spacy.load("en_core_web_sm")

    def identify(self, title: str) -> str:
        """
        Processes a title by generating and scoring candidates to find the best item name.
        """
        if not isinstance(title, str):
            return "Not Found"

        # 1. Isolate the Core Title and pre-filter noise
        core_title = title.split('|')[0].strip()
        cleaned_title = self._model_number_pattern.sub('', core_title)
        doc = self._nlp(cleaned_title)

        # 2. Generate all possible candidates (noun chunks)
        candidates = [chunk for chunk in doc.noun_chunks]
        if not candidates:
            return "Not Found"

        # 3. Score each candidate
        scores = {}
        for i, chunk in enumerate(candidates):
            score = 0
            text = chunk.text.lower()
            
            # Rule A: Longer phrases are better
            score += len(chunk.text.split()) * 10
            
            # Rule B: Penalize the first chunk if it's likely the brand
            if i == 0 and len(candidates) > 1:
                score -= 10
            
            # Rule C: Heavily penalize "use case" phrases (e.g., "for Bicycle")
            if chunk.root.head.pos_ == 'ADP': # ADP is a preposition (for, with, on)
                score -= 50

            # Rule D: Penalize if it's just a gender or generic term
            if text in ['men', 'women', 'kids', 'unisex', 'accessories']:
                 score -= 20

            scores[chunk.text] = score

        # 4. Select the Winner
        if not scores:
            return "Not Found"
            
        best_candidate = max(scores, key=scores.get)
        
        # Final cleanup: remove brand from the start of the phrase if it's there
        first_word_of_title = title.split(' ')[0]
        if best_candidate.lower().startswith(first_word_of_title.lower()):
            best_candidate = best_candidate[len(first_word_of_title):].strip()

        return best_candidate.title() if best_candidate else "Not Found"
