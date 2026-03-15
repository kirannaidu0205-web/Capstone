import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import SessionLocal, Product, SalesData

def calculate_elasticity(product_id):
    db = SessionLocal()
    # Fetch sales data for the product
    query = db.query(SalesData).filter(SalesData.product_id == product_id).all()
    if not query:
        return 0, 0
    
    df = pd.DataFrame([{
        'price': s.selling_price,
        'quantity': s.quantity
    } for s in query])
    db.close()

    if len(df) < 5:
        return 0, 0

    # Log-log model: ln(Q) = intercept + beta * ln(P)
    # beta is the price elasticity
    df['log_price'] = np.log(df['price'])
    df['log_qty'] = np.log(df['quantity'] + 0.1) # Add small constant to avoid log(0)

    X = df[['log_price']]
    y = df['log_qty']

    model = LinearRegression()
    model.fit(X, y)
    
    elasticity = model.coef_[0]
    r_squared = model.score(X, y)
    
    return elasticity, r_squared

def get_all_elasticities():
    db = SessionLocal()
    products = db.query(Product).all()
    results = {}
    for p in products:
        e, r2 = calculate_elasticity(p.id)
        results[p.id] = {
            'name': p.name,
            'elasticity': round(e, 3),
            'r_squared': round(r2, 3),
            'interpretation': "Elastic" if e < -1 else "Inelastic"
        }
    db.close()
    return results

if __name__ == "__main__":
    import os
    import sys
    # Add parent to path to allow imports from database
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from database.db_manager import SessionLocal, Product, SalesData
    
    print("Calculating elasticities...")
    res = get_all_elasticities()
    for pid, data in res.items():
        print(f"Product: {data['name']} | Elasticity: {data['elasticity']} | R2: {data['r_squared']} ({data['interpretation']})")
