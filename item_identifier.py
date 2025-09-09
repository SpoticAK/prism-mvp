# File: item_identifier.py
import re

class ItemIdentifier:
    """
    Identifies the core item from a product title using the "Headline" approach.
    """
    def __init__(self):
        # A curated list of adjectives, specs, and other non-essential words.
        self._noise_words = {
            'men', 'women', 'kids', 'man', 'woman', 'boys', 'girls', 'mens', 
            'womens', 'unisex', 'adult', 'home', 'gym', 'workout', 'exercise', 
            'training', 'gear', 'for', 'accessories', 'powerlifting', 'solid', 
            'combo', 'kit', 'pack', 'set', 'pcs', 'of', 'gram', 'serves', 
            'piece', 'pieces', 'anti', 'slip', 'multi', 'heavy', 'duty', 'premium', 
            'high', 'quality', 'mini', 'loop', 'with', 'and', 'the', 'a', 'in', 
            'per', 'stylish', 'comfortable', 'better', 'ideal', 'everyday', 'use', 
            'black', 'white', 'red', 'blue', 'green', 'multicolor', 'large', 
            'medium', 'small', 'size', 'fit', 'fitness', 'toning', 'band', 
            'bands', 'waterproof', 'convertible', 'streachable', 'full'
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
        # Remove specifications first (e.g., "20l")
        cleaned_zone = self._spec_pattern.sub('', golden_zone)
        
        # Tokenize (split into words)
        words = re.findall(r'\b[a-zA-Z-]+\b', cleaned_zone)
        
        if not words:
            return "Not Found"
            
        # Assume first word is brand and remove it
        candidate_words = words[1:]
        
        # Remove noise words
        item_words = [w for w in candidate_words if w not in self._noise_words]

        if not item_words:
            return "Not Found"

        # 3. Identify the first coherent noun phrase
        # We simply join the remaining clean words from left to right.
        # This works because the aggressive filtering has removed the fluff.
        identified_phrase = " ".join(item_words)

        return identified_phrase.title()
