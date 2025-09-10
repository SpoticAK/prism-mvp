# File: prism_score_evaluator.py
import pandas as pd

class PrismScoreEvaluator:
    """
    Calculates a comprehensive PRISM Score for a product based on a defined rubric.
    """
    def get_score(self, product_data: pd.Series) -> (int, str, bool):
        """
        Takes a row of product data and returns the PRISM Score, Potential Label,
        and a flag indicating if data was missing.
        """
        points_earned = 0
        points_available = 15 # Total possible points if all data is present
        missing_data = False

        # --- Price Scoring (Max 4 points) ---
        price = product_data.get('Price', None)
        if pd.notna(price):
            if 200 <= price <= 350:
                points_earned += 4
            elif (175 <= price <= 199) or (351 <= price <= 400):
                points_earned += 2
        else:
            points_available -= 4
            missing_data = True

        # --- Review Count Scoring (Max 3 points) ---
        reviews = product_data.get('Review', None)
        if pd.notna(reviews):
            if reviews >= 100:
                points_earned += 3
            elif 50 <= reviews <= 99:
                points_earned += 2
            else: # Below 50
                points_earned += 1
        else:
            points_available -= 3
            missing_data = True
            
        # --- Rating Scoring (Max 3 points) ---
        rating = product_data.get('Ratings', None) # Assuming 'Ratings' is the column name for the numeric rating
        if pd.notna(rating):
            if rating >= 4.2:
                points_earned += 3
            elif 4.0 <= rating < 4.2:
                points_earned += 2
            elif 3.7 <= rating < 4.0:
                points_earned += 1
            # else: 0 points
        else:
            points_available -= 3
            missing_data = True

        # --- Listing Quality Scoring (Max 2 points) ---
        quality = product_data.get('Listing Quality', None)
        if pd.notna(quality):
            if quality == 'Good':
                points_earned += 2
            elif quality == 'Average':
                points_earned += 1
            # else: 0 points for 'Poor'
        else:
            points_available -= 2
            missing_data = True
            
        # --- Monthly Sales Scoring (Max 3 points) ---
        sales = product_data.get('Cleaned Sales', None)
        if pd.notna(sales):
            if sales >= 1000:
                points_earned += 3
            elif 300 <= sales < 1000:
                points_earned += 2
            elif 100 <= sales < 300:
                points_earned += 1
            # else: 0 points
        else:
            points_available -= 3
            missing_data = True

        # --- Final Score Calculation ---
        if points_available == 0:
            final_score = 0
        else:
            final_score = int((points_earned / points_available) * 100)
            
        # Determine Potential Label
        if final_score > 80:
            potential_label = "High Potential"
        elif final_score >= 70:
            potential_label = "Moderate Potential"
        else:
            potential_label = "Low Potential"
            
        return final_score, potential_label, missing_data
