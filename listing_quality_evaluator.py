# File: listing_quality_evaluator.py
import streamlit as st
import requests
import cv2
import numpy as np

class ListingQualityEvaluator:
    """
    Analyzes a product image to determine the area covered by the main object.
    """
    @st.cache_data
    def get_score(_self, image_url: str) -> str:
        """
        Takes an image URL and returns a quality rating: Poor, Average, or Good.
        """
        if not isinstance(image_url, str) or not image_url:
            return "Error"

        try:
            # 1. Download the image
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(image_url, timeout=10, headers=headers)
            response.raise_for_status()
            
            # 2. Load image with OpenCV
            image_array = np.frombuffer(response.content, np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            # Convert to grayscale for easier processing
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 3. Isolate the object from the white background
            # This creates a binary mask: black for background, white for the object
            _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
            
            # 4. Calculate the area
            object_pixels = cv2.countNonZero(thresh)
            total_pixels = img.shape[0] * img.shape[1]
            coverage_percentage = (object_pixels / total_pixels) * 100
            
            # 5. Assign score based on your logic
            if coverage_percentage > 70:
                return "Good"
            elif coverage_percentage >= 50:
                return "Average"
            else:
                return "Poor"

        except Exception:
            # If any step fails, return an error status
            return "Error"
