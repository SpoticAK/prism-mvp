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

            # Genders (now without apostrophes)
            'men', 'women', 'kids', 'man', 'woman', 'boys', 'girls', 'unisex', 'adult',

            # Common Filler Words
            'home', 'gym', 'workout', 'exercise', 'training', 'gear', 'for',
            'accessories', 'powerlifting', 'solid', 'combo', 'kit', 'pack', 'set',
            'pcs', 'of', 'gram', 'serves', 'piece', 'pieces', 'anti', 'slip', 'multi',
            'with', 'and', 'the', 'a', 'in', 'per', 'ideal', 'everyday', 'use',

            # Colors & Sizes
            'black', 'white', 'red', 'blue', 'green', 'multicolor',
            'large', 'medium', 'small', 'size', 'fit',

            # Vague Nouns/Verbs that are often noise
            'fitness', 'toning', 'band', 'bands', 'cover', 'support'
        }
        # Regex to find and remove specifications like "20L", "500ML", "4mm"
        self._spec_pattern = re.compile(r'\b(\d+l|\d+ml|\d+mm|\d+g|\d+kg)\b', re.IGNORECASE)

    def identify(self, title: str) -> str:
        """
        Processes a title using the "Smart Cut-off" logic with improved cleaning.
        """
        if not isinstance(title, str):
            return "Not Found"

        # 1. Create the "Smart Cut-off" Golden Zone
        limit = 50
        if len(title) > limit:
            next_space = title.find(' ', limit)
            golden_zone = title[:next_space] if next_space != -1 else title[:limit]
        else:
            golden_zone = title
        
        # 2. Advanced Filtering
        # CRITICAL FIX: Sanitize possessives *before* tokenizing.
        sanitized_zone = golden_zone.lower().replace("'s", "")
        
        cleaned_zone = self._spec_pattern.sub('', sanitized_zone)
        words = re.findall(r'\b[a-zA-Z-]+\b', cleaned_zone)
        
        if not words:
            return "Not Found"
            
        # Assume first word is brand and remove it
        candidate_words = words[1:] if len(words) > 1 else words
        
        # Remove noise words
        item_words = [w for w in candidate_words if w not in self._noise_words]

        if not item_words:
            return "Not Found"

        # 3. Join the remaining words
        identified_phrase = " ".join(item_words)

        return identified_phrase.title()
