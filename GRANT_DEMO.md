cat > GRANT_DEMO.md << 'GRANT_EOF'
# ToxScreen-AI: Grant Demonstration Document

## Executive Summary

ToxScreen-AI is a comprehensive computational drug toxicity screening platform that combines molecular analysis, machine learning, and blockchain technology for immutable result storage. Built with Streamlit, FastAPI, and SQLite, it serves pharmaceutical researchers and academic institutions.

## Technical Architecture
Frontend: Streamlit (Python)
Backend: FastAPI REST API
Database: SQLite (toxscreen.db)
ML: RandomForest Classifier (83.3% accuracy)
Blockchain: Polygon Mumbai Testnet
Auth: streamlit-authenticator + YAML
Payments: Razorpay Integration

## Key Features

### 1. Molecular Analysis (Day 1-2)
- SMILES parsing via RDKit
- Lipinski Rule of Five evaluation
- Veber Rules for bioavailability
- 51 toxicophore structural alerts
- Drug-likeness scoring algorithm

### 2. Advanced Screening (Day 3-4)
- Morgan fingerprint similarity vs 17 known toxins
- SQLite persistence with usage tracking
- RandomForest hepatotoxicity model
- Blockchain recording on Polygon
- Professional PDF report generation

### 3. Enterprise Features (Day 5-6)
- Batch CSV processing
- FastAPI REST API with key authentication
- Rate limiting per subscription tier
- Three-tier subscription model (Free/Pro/Enterprise)
- Razorpay payment integration

## Subscription Tiers

| Feature | Free | Pro (₹499) | Enterprise (₹1,999) |
|---------|------|------------|---------------------|
| Daily Predictions | 5 | 100 | Unlimited |
| Batch Processing | No | Yes | Yes |
| API Access | 100 calls | 1000 calls | Unlimited |
| ML Predictions | No | Yes | Yes |
| PDF Reports | No | Yes | Yes |
| Blockchain | No | Yes | Yes |

## API Endpoints

- `POST /predict` - Single molecule prediction
- `POST /batch` - Batch prediction (Pro+)
- `GET /usage` - Usage statistics
- `GET /health` - Health check

## Deployment

The platform is deployable on:
- Streamlit Cloud (frontend)
- Railway/Render (FastAPI backend)
- Local development with uvicorn

## Impact Metrics

- 83.3% ML model accuracy for hepatotoxicity
- 51 toxicophore patterns detected
- 17 known toxin comparisons
- Sub-second prediction time
- Immutable blockchain verification

## Demo Credentials

- Free: demo / demo123
- Pro: devil / devil@123ch
- Enterprise: monkey / monkey@123ch

## Razorpay Payment Links

- Pro (₹499): https://rzp.io/rzp/WxjqLwMo
- Enterprise (₹1,999): https://rzp.io/rzp/JafzcGNI