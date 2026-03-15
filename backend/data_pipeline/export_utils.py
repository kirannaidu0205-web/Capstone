import pandas as pd
import os
from datetime import datetime
import sys

# Ensure database access
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import SessionLocal, Product, SalesData, CompetitorPrice

def get_product_report_data(product_id):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    sales = db.query(SalesData).filter(SalesData.product_id == product_id).all()
    competitors = db.query(CompetitorPrice).filter(CompetitorPrice.product_id == product_id).all()
    db.close()
    
    if not product:
        return None
        
    sales_df = pd.DataFrame([{
        'Date': s.date,
        'Quantity': s.quantity,
        'Price_Sold': s.selling_price
    } for s in sales])
    
    comp_df = pd.DataFrame([{
        'Competitor': c.competitor_name,
        'Price': c.price,
        'Timestamp': c.timestamp
    } for c in competitors])
    
    return {
        'product_name': product.name,
        'sales': sales_df,
        'competitors': comp_df
    }

def export_to_csv(product_id, output_dir="reports"):
    data = get_product_report_data(product_id)
    if not data:
        return None
        
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{data['product_name'].replace(' ', '_')}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Combine sales and some product info for a simple CSV
    df = data['sales']
    df['Product'] = data['product_name']
    df.to_csv(filepath, index=False)
    print(f"Report exported to CSV: {filepath}")
    return filepath

def export_to_excel(product_id, output_dir="reports"):
    data = get_product_report_data(product_id)
    if not data:
        return None
        
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{data['product_name'].replace(' ', '_')}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        data['sales'].to_excel(writer, sheet_name='Sales History', index=False)
        data['competitors'].to_excel(writer, sheet_name='Competitor Prices', index=False)
        
    print(f"Report exported to Excel: {filepath}")
    return filepath

if __name__ == "__main__":
    # Test
    # export_to_csv(1)
    # export_to_excel(1)
    print("Export utilities initialized.")
