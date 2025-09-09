# File: listing_quality_evaluator.py
import requests
from PIL import Image
from io import BytesIO
import re

class ListingQualityEvaluator: # Renamed class
    """
    Analyzes a product listing to generate a quality score based on its properties.
    """
    def __init__(self):
        self._thumbnail_pattern = re.compile(r'._AC_UL\d+_')

    def get_score(self, image_url: str) -> int:
        """
        Takes an image URL and returns a Listing Quality Score (0-100).
        """
        if not isinstance(image_url, str) or not image_url:
            return 0

        if "no-image" in image_url or "placeholder" in image_url:
            return 0

        score = 50
        if self._thumbnail_pattern.search(image_url):
            score -= 20

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(image_url, stream=True, timeout=5, headers=headers)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content))
            width, height = image.size

            if width >= 500 and height >= 500:
                score += 30
            elif width >= 300 and height >= 300:
                score += 15
            else:
                score -= 10
        except (requests.exceptions.RequestException, IOError):
            return 10

        return max(0, min(100, score))
