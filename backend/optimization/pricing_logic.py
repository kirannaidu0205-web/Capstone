import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import SessionLocal, Product, CompetitorPrice, PriceRecommendation
from ml.elasticity import calculate_elasticity
import numpy as np
import random

def generate_recommendations():
    db = SessionLocal()
    products = db.query(Product).all()
    
    for p in products:
        # 1. Competitor-based logic
        comp_prices = [cp.price for cp in db.query(CompetitorPrice).filter(CompetitorPrice.product_id == p.id).all()]
        avg_comp_price = np.mean(comp_prices) if comp_prices else p.current_price
        min_comp_price = min(comp_prices) if comp_prices else p.current_price
        
        # 2. Elasticity-based logic
        elasticity, r2 = calculate_elasticity(p.id)
        
        # Marginal cost (assumed 60% of base_price)
        mc = p.base_price * 0.6
        
        if elasticity < -1:
            # Optimal price for profit maximization
            opt_price_profit = mc * (elasticity / (1 + elasticity))
        else:
            # For inelastic goods, keep price stable or slight increase to test sensitivity
            opt_price_profit = p.current_price * 1.02
            
        # 3. Final Recommendation (Market Penetration Strategy)
        # Weighting: 60% Competitor (to be competitive), 30% Elasticity, 10% Current
        rec_price = (0.6 * avg_comp_price) + (0.3 * opt_price_profit) + (0.1 * p.current_price)
        
        # Determine Logic Type based on product behavior
        if rec_price <= p.base_price * 0.75:
            logic_name = "Market-Penetrator"
        elif elasticity < -1.5 and r2 > 0.6:
            logic_name = "Elasticity-Profit"
        elif p.category == "Apparel" and elasticity > -1:
            logic_name = "Stability-Focus"
        elif p.category == "Electronics":
            logic_name = "Market-Follower"
        else:
            logic_name = "Blended-AI"
 
        # Constraints: Ensure we are cheaper than EVERY competitor (Negative Market Gap for all)
        # Target 2-5% lower than the CHEAPEST competitor
        rec_price = min(rec_price, min_comp_price * random.uniform(0.95, 0.98))
        rec_price = max(p.base_price * 0.7, min(p.base_price * 1.3, rec_price))
        
        # If price was changed significantly by constraints, update logic type
        if round(rec_price, 2) == round(p.base_price * 0.7, 2) or round(rec_price, 2) == round(p.base_price * 1.3, 2):
            logic_name = "Safety-Guardrail"

        recommendation = PriceRecommendation(
            product_id=p.id,
            recommended_price=round(rec_price, 2),
            logic_type=logic_name,
            confidence_score=round(r2, 2)
        )
        db.add(recommendation)
        
        p.current_price = round(rec_price, 2)
    
    db.commit()
    db.close()
    print("Pricing recommendations generated.")

if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    generate_recommendations()
