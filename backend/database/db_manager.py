from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    base_price = Column(Float)
    current_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    competitor_prices = relationship("CompetitorPrice", back_populates="product")
    sales = relationship("SalesData", back_populates="product")

class CompetitorPrice(Base):
    __tablename__ = 'competitor_prices'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    competitor_name = Column(String)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="competitor_prices")

class SalesData(Base):
    __tablename__ = 'sales_data'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    date = Column(DateTime)
    quantity = Column(Integer)
    selling_price = Column(Float)
    
    product = relationship("Product", back_populates="sales")

class PriceRecommendation(Base):
    __tablename__ = 'price_recommendations'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    recommended_price = Column(Float)
    logic_type = Column(String) # e.g., "competitor-based", "elasticity-based"
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database Setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'pricing_system.db')
ENGINE_URL = f"sqlite:///{DB_PATH}"

from sqlalchemy import create_engine
engine = create_engine(ENGINE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
