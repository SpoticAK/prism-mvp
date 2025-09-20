# File: item_identifier.py
import re

class ItemIdentifier:
    """
    Identifies the core item from a product title using the "Top 10 Words"
    rule-based logic. No external NLP libraries are needed.
    """
    def __init__(self):
        self._noise_words = {
            'stylish', 'comfortable', 'premium', 'high', 'quality', 'heavy', 'duty',
            'waterproof', 'convertible', 'streachable', 'full', 'loose', 'relaxed',
            'retractable', 'handheld', 'rechargeable', 'portable', 'soft', 'stretchy',
            'cushioned', 'breathable', 'sturdy', 'micronized', 'new', 'complete',
            "men's", "women's", "boy's", "girl's", 'mens', 'womens', 'men',
            'women', 'kids', 'man', 'woman', 'boys', 'girls', 'unisex', 'adult',
            'home', 'gym', 'workout', 'exercise', 'training', 'gear', 'for',
            'accessories', 'powerlifting', 'solid', 'combo', 'kit', 'pack', 'set',
            'pcs', 'of', 'gram', 'serves', 'piece', 'pieces', 'anti', 'slip', 'multi',
            'with', 'and', 'the', 'a', 'in', 'per', 'ideal', 'everyday', 'use',
            'black', 'white', 'red', 'blue', 'green', 'multicolor',
            'large', 'medium', 'small', 'size', 'fit',
            'fitness', 'toning', 'band', 'bands', 'cover', 'support'
        }
        self._model_number_pattern = re.compile(r'\b[a-zA-Z]+\d+[a-zA-Z0-9]*\b|\b\d+[a-zA-Z]+\b')

    def identify(self, title: str) -> str:
        """
        Processes a title using the "Top 10 Words" logic.
        """
        if not isinstance(title, str):
            return "Not Found"

        # 1. Isolate the "Golden Zone" (first 10 words)
        words = title.lower().split()
        golden_zone_words = words[:10]
        
        # 2. Filter Noise
        # Ignore the first word (brand)
        candidate_words = golden_zone_words[1:] if len(golden_zone_words) > 1 else golden_zone_words
            
        # Remove model numbers and noise words
        item_words = []
        for word in candidate_words:
            clean_word = re.sub(r'[^\w-]', '', word) # Clean punctuation
            if not self._model_number_pattern.search(clean_word) and clean_word not in self._noise_words:
                item_words.append(clean_word)

        if not item_words:
            return "Not Found"

        # 3. Join the remaining words
        return " ".join(item_words).title()
