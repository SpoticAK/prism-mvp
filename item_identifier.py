# File: item_identifier.py
import re

class ItemIdentifier:
    """
    Tool #1: A self-contained engine to identify items from product titles.
    This version uses the user's proposed logic for item identification.
    """
    def __init__(self):
        """Defines noise words when the engine starts."""
        self._noise_words = self._get_noise_words()

    def _get_noise_words(self):
        """Defines a set of common words to ignore for cleaner results."""
        return {
            'men', 'women', 'kids', 'man', 'woman', 'boys', 'girls', 'mens', 'womens', 'unisex', 'adult',
            'home', 'gym', 'workout', 'exercise', 'training', 'gear', 'for', 'accessories', 'powerlifting',
            'solid', 'combo', 'kit', 'pack', 'set', 'pcs', 'of', 'gram', 'serves',
            'anti', 'slip', 'multi', 'heavy', 'duty', 'premium', 'high', 'quality', 'mini',
            'with', 'and', 'the', 'a', 'in', 'per', 'stylish', 'comfortable', 'better', 'loop',
            'ideal', 'everyday', 'use', 'black', 'white', 'red', 'blue', 'green', 'multicolor',
            'large', 'medium', 'small', 'size', 'fit',
        }

    def is_model_number(self, word):
        """A simple heuristic to detect model numbers or alphanumeric codes."""
        # Checks for a mix of letters and numbers, or is all caps and not a common word.
        return bool(re.search(r'\d', word)) and bool(re.search(r'[a-zA-Z]', word))

    def identify(self, title: str) -> str:
        """
        Processes a title using the user's defined logic to find the core item.
        """
        if not isinstance(title, str):
            return "Invalid Title"

        # 1. Clean and split the title into words, taking the first 6
        clean_title = re.sub(r'[^\w\s]', '', title) # Remove punctuation
        words = clean_title.lower().split()
        initial_words = words[:6]

        # 2. Assume the first word is the brand and remove it
        if len(initial_words) > 1:
            candidate_words = initial_words[1:]
        else:
            candidate_words = initial_words

        # 3. Remove serial numbers and noise words
        item_words = [
            word for word in candidate_words 
            if not self.is_model_number(word) and word not in self._noise_words
        ]

        if not item_words:
            return "Not Found"

        # 4. Join the remaining words to form the item name
        return " ".join(item_words).title()
