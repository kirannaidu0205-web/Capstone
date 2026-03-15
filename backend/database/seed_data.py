from db_manager import SessionLocal, Product, SalesData, CompetitorPrice, init_db
from datetime import datetime, timedelta
import random

def seed():
    init_db()
    db = SessionLocal()
    
    # Clear existing data to avoid duplicates
    db.query(SalesData).delete()
    db.query(CompetitorPrice).delete()
    db.query(Product).delete()
    db.commit()
    
    # Create 15 Diverse Products (Prices in INR)
    products_data = [
        # Electronics
        ("Gamer Pro Laptop", "Electronics", 95000.0, 92000.0),
        ("UltraSound Headphones", "Electronics", 15000.0, 14500.0),
        ("Smart Watch X", "Electronics", 8000.0, 7500.0),
        ("4K OLED TV", "Electronics", 120000.0, 115000.0),
        ("Wireless Mouse", "Electronics", 1500.0, 1200.0),
        # Apparel
        ("Cotton T-Shirt", "Apparel", 999.0, 899.0),
        ("Denim Jeans", "Apparel", 2499.0, 2199.0),
        ("Leather Jacket", "Apparel", 8500.0, 7999.0),
        ("Running Shoes", "Apparel", 4500.0, 3999.0),
        ("Summer Dress", "Apparel", 1800.0, 1500.0),
        # Home & Kitchen
        ("Coffee Maker", "Home", 5500.0, 4999.0),
        ("Air Fryer", "Home", 8500.0, 7999.0),
        ("Vacuum Cleaner", "Home", 12000.0, 11000.0),
        ("Blender Pro", "Home", 4500.0, 3999.0),
        ("Smart Table Lamp", "Home", 2500.0, 1999.0)
    ]
    
    products = [Product(name=n, category=c, base_price=bp, current_price=cp) 
                for n, c, bp, cp in products_data]
    
    db.add_all(products)
    db.commit()

    # Refresh products to get IDs
    products = db.query(Product).all()
    
    # Create Historical Sales (last 90 days)
    for p in products:
        # Vary base quantity by category
        if p.category == "Apparel":
            base_daily_qty = random.randint(15, 30)
        elif p.category == "Electronics":
            base_daily_qty = random.randint(3, 8)
        else: # Home
            base_daily_qty = random.randint(8, 15)
            
        for i in range(180):
            date = datetime.utcnow() - timedelta(days=i)
            # Random price variation around current_price to simulate historical changes
            price_var = random.uniform(0.9, 1.1)
            selling_price = p.current_price * price_var
            
            # Simple elasticity logic: quantity = base * (base_price / selling_price)^elasticity_factor
            elasticity_factor = random.uniform(1.2, 2.5)
            qty = int(base_daily_qty * (p.base_price / selling_price)**elasticity_factor + random.randint(0, 3))
            
            sale = SalesData(
                product_id=p.id,
                date=date,
                quantity=max(1, qty), # Ensure at least 1 sale
                selling_price=round(selling_price, 2)
            )
            db.add(sale)

    # Create Competitor Prices (Specifically categorized Indian Retailers)
    # E-Commerce (Overall): Amazon India, Flipkart
    # Fashion & Lifestyle (Online): Myntra, Ajio, Tata CLiQ
    # Physical Retail (General): Reliance Retail, Croma
    
    overall_retailers = ["Amazon India", "Flipkart"]
    fashion_retailers = ["Myntra", "Ajio", "Tata CLiQ"]
    physical_retailers = ["Reliance Retail", "Croma"]

    for p in products:
        # Determine relevant competitors based on category
        available_competitors = overall_retailers.copy()
        
        if p.category == "Electronics":
            available_competitors.extend(["Croma", "Reliance Retail"])
        elif p.category == "Apparel":
            available_competitors.extend(fashion_retailers)
            available_competitors.extend(["Reliance Retail"]) # Reliance Trends
        elif p.category == "Home":
            available_competitors.extend(["Reliance Retail", "Croma"])

        # Pick 3-4 random competitors from the relevant list
        num_comps = min(len(available_competitors), random.randint(3, 4))
        selected_comps = random.sample(available_competitors, num_comps)
        
        for comp in selected_comps:
            # Competitors are more expensive than our store (Market Gap will be negative)
            comp_price = p.current_price * random.uniform(1.05, 1.25)
            cp = CompetitorPrice(
                product_id=p.id,
                competitor_name=comp,
                price=round(comp_price, 2),
                timestamp=datetime.utcnow()
            )
            db.add(cp)
            
    db.commit()
    db.close()
    print(f"Database seeded successfully with 15 unique products (Indian context) and 180 days (6 months) of varied history.")

if __name__ == "__main__":
    seed()
