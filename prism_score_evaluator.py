# File: prism_score_evaluator.py
import pandas as pd

class PrismScoreEvaluator:
    def get_score(self, product_data: pd.Series) -> (int, str, bool):
        points_earned, points_available, missing_data = 0, 15, False
        
        # --- Price Scoring (Max 4 points) ---
        price = product_data.get('Price')
        if pd.notna(price):
            if 200 <= price <= 350: points_earned += 4
            elif 175 <= price <= 199 or 351 <= price <= 400: points_earned += 2
        else: points_available -= 4; missing_data = True

        # --- Review Count Scoring (Max 3 points) ---
        reviews = product_data.get('Review')
        if pd.notna(reviews):
            if reviews >= 100: points_earned += 3
            elif 50 <= reviews <= 99: points_earned += 2
            else: points_earned += 1
        else: points_available -= 3; missing_data = True
            
        # --- UPDATED: New Rating Scoring (Max 3 points) ---
        rating = product_data.get('Ratings_Num')
        if pd.notna(rating):
            if rating >= 4.2: points_earned += 3
            elif 3.6 <= rating <= 4.19: points_earned += 2
            elif 3.0 <= rating <= 3.59: points_earned += 1
            # else: 0 points for below 3.0
        else: points_available -= 3; missing_data = True

        # --- UPDATED: New Listing Quality Scoring (Max 2 points) ---
        quality = product_data.get('Listing Quality')
        if pd.notna(quality) and quality != "Error":
            if quality == 'Poor': points_earned += 2
            elif quality == 'Average': points_earned += 1 # Average gets +1
            elif quality == 'Good': points_earned += 1    # Good also gets +1
        else: points_available -= 2; missing_data = True
            
        # --- Monthly Sales Scoring (Max 3 points) ---
        sales = product_data.get('Cleaned Sales')
        if pd.notna(sales):
            if sales >= 500: points_earned += 3
            elif 100 <= sales <= 499: points_earned += 2
            else: # Below 100
                points_earned += 1
        else: points_available -= 3; missing_data = True

        final_score = int((points_earned / points_available) * 100) if points_available > 0 else 0
            
        # --- Potential Thresholds ---
        if final_score > 80: potential_label = "High Potential"
        elif final_score >= 66: potential_label = "Moderate Potential"
        else: potential_label = "Low Potential"
            
        return final_score, potential_label, missing_data
