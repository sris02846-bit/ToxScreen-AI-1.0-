"""
FDA Database Integration Module
Real-time FDA API queries for drug approval status.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

FDA_CACHE = {}
CACHE_DURATION = timedelta(hours=24)


def check_approval_status(drug_name: str) -> Dict:
    """Check FDA approval status for a drug."""
    try:
        url = "https://api.fda.gov/drug/drugsfda.json"
        params = {"search": f'products.brand_name:"{drug_name}"', "limit": 3}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                drug = results[0]
                return {
                    "drug_name": drug_name,
                    "fda_approved": True,
                    "application_number": drug.get("application_number", "N/A"),
                    "sponsor": drug.get("sponsor_name", "N/A"),
                    "status": "APPROVED"
                }
        return {"drug_name": drug_name, "fda_approved": False, "status": "Not found"}
    except:
        return {"drug_name": drug_name, "fda_approved": False, "status": "API unavailable"}


def query_adverse_events(drug_name: str) -> Dict:
    """Query FDA adverse events."""
    try:
        url = "https://api.fda.gov/drug/event.json"
        params = {"search": f'patient.drug.medicinalproduct:"{drug_name}"', "limit": 5}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {"drug_name": drug_name, "total_reports": data.get("meta", {}).get("results", {}).get("total", 0)}
        return {"drug_name": drug_name, "total_reports": 0}
    except:
        return {"drug_name": drug_name, "total_reports": 0}


def get_fda_summary(drug_name: str) -> Dict:
    """Get complete FDA summary."""
    approval = check_approval_status(drug_name)
    adverse = query_adverse_events(drug_name)
    return {"drug_name": drug_name, "approval": approval, "adverse_events": adverse}
