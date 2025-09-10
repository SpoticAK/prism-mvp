# File: prism_score_evaluator.py
import pandas as pd

class PrismScoreEvaluator:
    def get_score(self, product_data: pd.Series) -> (int, str, bool):
        points_earned, points_available, missing_data = 0, 15, False
        
        price = product_data.get('Price')
        if pd.notna(price):
            if 200 <= price <= 350: points_earned += 4
            elif 175 <= price <= 199 or 351 <= price <= 400: points_earned += 2
        else: points_available -= 4; missing_data = True

        reviews = product_data.get('Review')
        if pd.notna(reviews):
            if reviews >= 100: points_earned += 3
            elif 50 <= reviews <= 99: points_earned += 2
            else: points_earned += 1
        else: points_available -= 3; missing_data = True
            
        rating = product_data.get('Ratings_Num')
        if pd.notna(rating):
            if rating >= 4.2: points_earned += 3
            elif 4.0 <= rating < 4.2: points_earned += 2
            elif 3.7 <= rating < 4.0: points_earned += 1
        else: points_available -= 3; missing_data = True

        quality = product_data.get('Listing Quality')
        if pd.notna(quality) and quality != "Error":
            if quality == 'Good': points_earned += 2
            elif quality == 'Average': points_earned += 1
        else: points_available -= 2; missing_data = True
            
        # --- UPDATED: New Monthly Sales Logic ---
        sales = product_data.get('Cleaned Sales')
        if pd.notna(sales):
            if sales >= 500: points_earned += 3
            elif 100 <= sales <= 499: points_earned += 2
            else: # Below 100
                points_earned += 1
        else: points_available -= 3; missing_data = True

        final_score = int((points_earned / points_available) * 100) if points_available > 0 else 0
            
        # --- UPDATED: New Potential Threshold ---
        if final_score > 80: potential_label = "High Potential"
        elif final_score >= 66: potential_label = "Moderate Potential"
        else: potential_label = "Low Potential"
            
        return final_score, potential_label, missing_data
