"""
ToxScreen-AI FastAPI Backend
REST API for toxicity predictions with API key authentication.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import uvicorn
import sys
import os
import time
from datetime import datetime

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from molecular_parser import parse_smiles, calculate_basic_properties
from lipinski_rules import evaluate_lipinski
from veber_rules import evaluate_veber
from toxicophores import evaluate_toxicophores
from fingerprint import compare_toxin_similarity
from ml_model import predict_hepatotoxicity
from database import validate_api_key, track_api_usage, get_daily_usage, get_tier_limits, get_user_tier
from batch_processor import process_single_smiles

app = FastAPI(
    title="ToxScreen-AI API",
    description="Computational Drug Toxicity Screening API",
    version="1.0.0"
)

# Rate limiting cache
rate_limit_cache: Dict[str, Dict] = {}


class SmilesRequest(BaseModel):
    smiles: str = Field(..., description="SMILES string to analyze", example="CC(=O)OC1=CC=CC=C1C(=O)O")


class BatchRequest(BaseModel):
    smiles_list: List[str] = Field(..., description="List of SMILES strings", min_items=1, max_items=100)


class PredictionResponse(BaseModel):
    smiles: str
    valid: bool
    molecular_weight: Optional[float]
    molecular_formula: Optional[str]
    lipinski_violations: Optional[int]
    veber_violations: Optional[int]
    toxicity_score: Optional[float]
    risk_level: Optional[str]
    druglikeness_score: Optional[float]
    result: Optional[str]
    most_similar_toxin: Optional[str]
    toxin_similarity: Optional[float]
    ml_prediction: Optional[str]
    ml_confidence: Optional[float]
    error: Optional[str] = None


def check_api_rate_limit(username: str) -> bool:
    """Check if API key has exceeded rate limit."""
    tier = get_user_tier(username)
    limits = get_tier_limits(tier)
    daily_usage = get_daily_usage(username)
    
    return daily_usage < limits['api_calls']


async def verify_api_key(x_api_key: str = Header(..., description="API Key for authentication")):
    """Verify API key and check rate limits."""
    user_info = validate_api_key(x_api_key)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if not check_api_rate_limit(user_info['username']):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Upgrade your plan.")
    
    track_api_usage(user_info['username'])
    return user_info


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ToxScreen-AI API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "batch": "/batch",
            "health": "/health"
        },
        "authentication": "API Key required in X-API-Key header"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: SmilesRequest, user_info: Dict = Depends(verify_api_key)):
    """
    Predict toxicity for a single SMILES string.
    
    Requires valid API key in X-API-Key header.
    Rate limited based on subscription tier.
    """
    smiles = request.smiles.strip()
    
    if not smiles:
        raise HTTPException(status_code=400, detail="SMILES string is required")
    
    # Process the molecule
    result = process_single_smiles(smiles)
    
    if not result['Valid']:
        return PredictionResponse(
            smiles=smiles,
            valid=False,
            error=result.get('Error', 'Invalid SMILES')
        )
    
    # Get ML prediction
    ml_result = predict_hepatotoxicity(smiles)
    
    return PredictionResponse(
        smiles=smiles,
        valid=True,
        molecular_weight=result.get('Molecular_Weight'),
        molecular_formula=result.get('Molecular_Formula'),
        lipinski_violations=result.get('Lipinski_Violations'),
        veber_violations=result.get('Veber_Violations'),
        toxicity_score=result.get('Toxicity_Score'),
        risk_level=result.get('Risk_Level'),
        druglikeness_score=result.get('DrugLikeness_Score'),
        result=result.get('Result'),
        most_similar_toxin=result.get('Most_Similar_Toxin'),
        toxin_similarity=result.get('Toxin_Similarity'),
        ml_prediction=ml_result.get('prediction'),
        ml_confidence=ml_result.get('confidence')
    )


@app.post("/batch")
async def batch_predict(request: BatchRequest, user_info: Dict = Depends(verify_api_key)):
    """
    Batch predict toxicity for multiple SMILES strings.
    
    Requires valid API key with Pro or Enterprise tier.
    """
    tier = user_info.get('tier', 'free')
    if tier == 'free':
        raise HTTPException(status_code=403, detail="Batch processing requires Pro or Enterprise subscription")
    
    results = []
    for smiles in request.smiles_list:
        result = process_single_smiles(smiles.strip())
        results.append(result)
    
    return {
        "total": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/usage")
async def get_usage(user_info: Dict = Depends(verify_api_key)):
    """Get current usage statistics for the API key."""
    username = user_info['username']
    usage = get_daily_usage(username)
    tier = user_info.get('tier', 'free')
    limits = get_tier_limits(tier)
    
    return {
        "username": username,
        "tier": tier,
        "daily_limit": limits['api_calls'],
        "used_today": usage,
        "remaining": max(0, limits['api_calls'] - usage)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
