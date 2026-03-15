# 📊 Market-Aware Price Monitoring and Optimization System

A premium retail analytics platform that uses Machine Learning to optimize pricing strategies based on competitor data and demand elasticity.

---

## 🚀 Features

- **🛡️ Smart Web Scraping:** Modular scraper with User-Agent rotation to track competitor prices responsibly.
- **📉 Demand Modeling:** Log-log regression to calculate **Price Elasticity of Demand (PED)**.
- **🤖 Optimization Engine:** Blended AI logic (Market + Elasticity + Inventory) to recommend profit-maximizing price points.
- **📄 Professional Reporting:** One-click export of data to **CSV and Excel** formats.
- **✨ Interactive Dashboard:** Beautiful Dash/Plotly interface with real-time demand curve analytics.
- **🔗 REST API:** High-performance FastAPI backend serving structured pricing data.

---

## 📁 Project Structure

The project is organized into a clean **Backend** and **Frontend** architecture for better modularity:

```text
├── backend/                  # CORE ENGINE & DATA
│   ├── api/                  # FastAPI REST endpoints
│   ├── database/             # SQLite storage & SQLAlchemy models
│   ├── ml/                   # Price Elasticity (Log-Log) modeling
│   ├── optimization/         # Blended AI pricing logic
│   ├── scraper/              # Smart scrapers with anti-detection
│   └── data_pipeline/        # CSV/Excel export utilities
├── frontend/                 # USER INTERFACE
│   └── dashboard/            # Dash/Plotly visualization app
├── reports/                  # Auto-generated CSV/Excel exports
└── PROJECT_DOCUMENTATION.md  # Detailed technical reference
```

---

## 🚦 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize & Seed Database
```bash
python backend/database/seed_data.py
```

### 3. Generate AI Recommendations
```bash
python backend/optimization/pricing_logic.py
```

### 4. Launch the System
- **Backend API (Uvicorn):**
  ```bash
  uvicorn backend.api.main:app --reload
  ```
- **Frontend Dashboard:**
  ```bash
  python run_ui.py
  ```

---

## 📊 Access Points

- **Dashboard:** [http://127.0.0.1:8050](http://127.0.0.1:8050)
- **API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📖 In-Depth Documentation
For a full breakdown of the microeconomic theories, ML algorithms, and system architecture used in this project, please refer to:
👉 **[PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md)**

---
*Capstone Project — Retail Pricing Intelligence System*
