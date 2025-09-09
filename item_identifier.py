# File: item_identifier.py
import re

class ItemIdentifier:
    """
    Identifies the core item from a product title using a hardcoded
    "Golden Zone" and an expanded noise word list. No external NLP libraries needed.
    """
    def __init__(self):
        # A comprehensive, hardcoded list of words to ignore.
        self._noise_words = {
            # Adjectives & Descriptors
            'stylish', 'comfortable', 'premium', 'high', 'quality', 'heavy', 'duty',
            'waterproof', 'convertible', 'streachable', 'full', 'loose', 'relaxed',
            'retractable', 'handheld', 'rechargeable', 'portable', 'soft', 'stretchy',
            'cushioned', 'breathable', 'sturdy', 'micronized', 'new', 'complete',

            # Possessives & Genders
            "men's", "women's", "boy's", "girl's", 'mens', 'womens', 'men',
            'women', 'kids', 'man', 'woman', 'boys', 'girls', 'unisex', 'adult',

            # Common Filler Words
            'home', 'gym', 'workout', 'exercise', 'training', 'gear', 'for',
            'accessories', 'powerlifting', 'solid', 'combo', 'kit', 'pack', 'set',
            'pcs', 'of', 'gram', 'serves', 'piece', 'pieces', 'anti', 'slip', 'multi',
            'with', 'and', 'the', 'a', 'in', 'per', 'ideal', 'everyday', 'use',

            # Colors & Sizes
            'black', 'white', 'red', 'blue', 'green', 'multicolor',
            'large', 'medium', 'small', 'size', 'fit',

            # Vague Nouns/Verbs
            'fitness', 'toning', 'band', 'bands', 'cover', 'support'
        }
        # Regex to find and remove specifications like "20L", "500ML", "4mm"
        self._spec_pattern = re.compile(r'\b(\d+l|\d+ml|\d+mm|\d+g|\d+kg)\b')

    def identify(self, title: str) -> str:
        """
        Processes a title using the 50-character "Golden Zone" logic.
        """
        if not isinstance(title, str):
            return "Not Found"

        # 1. Isolate the 50-character "Golden Zone"
        golden_zone = title[:50].lower()

        # 2. Advanced Filtering
        cleaned_zone = self._spec_pattern.sub('', golden_zone)
        words = re.findall(r'\b[a-zA-Z-]+\b', cleaned_zone)
        
        if not words:
            return "Not Found"
            
        # Assume first word is brand and remove it
        candidate_words = words[1:]
        
        # Remove noise words from our hardcoded list
        item_words = [w for w in candidate_words if w not in self._noise_words]

        if not item_words:
            return "Not Found"

        # 3. Join the remaining words to form the item name
        identified_phrase = " ".join(item_words)

        return identified_phrase.title()
