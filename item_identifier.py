# File: item_identifier.py
import re

class ItemIdentifier:
    """
    Tool #1: A self-contained engine to identify items from product titles.
    This version uses a robust phrase-finding logic.
    """
    def __init__(self):
        self._noise_words = self._get_noise_words()

    def _get_noise_words(self):
        """A comprehensive set of words to ignore for cleaner results."""
        return {
            'men', 'women', 'kids', 'man', 'woman', 'boys', 'girls', 'mens', 'womens', 'unisex', 'adult',
            'home', 'gym', 'workout', 'exercise', 'training', 'gear', 'for', 'accessories', 'powerlifting',
            'solid', 'combo', 'kit', 'pack', 'set', 'pcs', 'of', 'gram', 'serves', 'piece', 'pieces',
            'anti', 'slip', 'multi', 'heavy', 'duty', 'premium', 'high', 'quality', 'mini', 'loop',
            'with', 'and', 'the', 'a', 'in', 'per', 'stylish', 'comfortable', 'better',
            'ideal', 'everyday', 'use', 'black', 'white', 'red', 'blue', 'green', 'multicolor',
            'large', 'medium', 'small', 'size', 'fit', 'fitness', 'toning', 'band', 'bands'
        }

    def is_model_number(self, word):
        """Heuristic to detect model numbers (e.g., PUK3502GS)."""
        return (len(word) > 4 and any(char.isdigit() for char in word) and
                any(char.isalpha() for char in word))

    def identify(self, title: str) -> str:
        """
        Processes a title using phrase-finding logic to identify the core item.
        """
        if not isinstance(title, str):
            return "Invalid Title"

        # 1. Isolate the core part of the title before major separators.
        core_title = re.split(r'\||,', title)[0]

        # 2. Tokenize, preserving hyphenated words.
        words = re.findall(r'\b[a-zA-Z0-9-]+\b', core_title.lower())

        if not words:
            return "Not Found"

        # 3. Assume first word is brand and remove it.
        candidate_words = words[1:]

        # 4. Find the longest sequence of non-noise, non-model-number words.
        longest_sequence = []
        current_sequence = []
        for word in candidate_words:
            if word not in self._noise_words and not self.is_model_number(word):
                current_sequence.append(word)
            else:
                if len(current_sequence) > len(longest_sequence):
                    longest_sequence = current_sequence
                current_sequence = []
        
        # Check one last time in case the title ends with the item.
        if len(current_sequence) > len(longest_sequence):
            longest_sequence = current_sequence

        if not longest_sequence:
            return "Not Found"

        # 5. Return the longest coherent phrase.
        return " ".join(longest_sequence).title()
