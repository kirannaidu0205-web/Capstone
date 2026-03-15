from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette import status
from sqlalchemy.orm import Session
import sys
import os
from dotenv import load_dotenv

# Load secret config
load_dotenv()
API_KEY = os.getenv("API_KEY", "pricing-secret-key-2026")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(header_value: str = Security(api_key_header)):
    if header_value == API_KEY:
        return header_value
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

# Adjust path to import from database
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db_manager import SessionLocal, Product, CompetitorPrice, PriceRecommendation, SalesData

app = FastAPI(title="Retail Pricing Analytics API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pricing Analytics API"}

@app.get("/products", dependencies=[Depends(get_api_key)])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

@app.get("/analytics/{product_id}", dependencies=[Depends(get_api_key)])
def get_product_analytics(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    sales = db.query(SalesData).filter(SalesData.product_id == product_id).all()
    competitors = db.query(CompetitorPrice).filter(CompetitorPrice.product_id == product_id).all()
    recommendation = db.query(PriceRecommendation).filter(PriceRecommendation.product_id == product_id).order_by(PriceRecommendation.created_at.desc()).first()
    
    return {
        "product": product,
        "sales_history": sales,
        "competitor_prices": competitors,
        "latest_recommendation": recommendation
    }

@app.get("/market-trend", dependencies=[Depends(get_api_key)])
def get_market_trend(db: Session = Depends(get_db)):
    # Summary of all products
    products = db.query(Product).all()
    summary = []
    for p in products:
        comp_avg = db.query(CompetitorPrice).filter(CompetitorPrice.product_id == p.id).all()
        avg_price = sum(c.price for c in comp_avg) / len(comp_avg) if comp_avg else p.current_price
        summary.append({
            "name": p.name,
            "our_price": p.current_price,
            "market_avg": round(avg_price, 2),
            "gap": round(((p.current_price - avg_price) / avg_price) * 100, 2) if avg_price else 0
        })
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
