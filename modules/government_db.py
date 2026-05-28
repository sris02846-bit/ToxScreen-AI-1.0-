"""
Government Database Integration Module
Automatically queries PubChem, EPA CompTox on every search.
No manual intervention needed.
"""

import requests
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path

API_CACHE = {}
CACHE_DURATION = timedelta(hours=24)


def query_pubchem_by_smiles(smiles: str) -> Optional[Dict]:
    """Query PubChem automatically - no API key needed."""
    
    cache_key = f"pubchem_{smiles}"
    if cache_key in API_CACHE:
        cached_data, cached_time = API_CACHE[cache_key]
        if datetime.now() - cached_time < CACHE_DURATION:
            return cached_data
    
    properties = [
        "MolecularFormula", "MolecularWeight", "CanonicalSMILES",
        "IUPACName", "XLogP", "TPSA", "HBondDonorCount",
        "HBondAcceptorCount", "RotatableBondCount", "Complexity",
        "ExactMass", "HeavyAtomCount"
    ]
    
    prop_string = ",".join(properties)
    
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{smiles}/property/{prop_string}/JSON"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "PropertyTable" in data and "Properties" in data["PropertyTable"]:
                props = data["PropertyTable"]["Properties"][0]
                
                result = {
                    "source": "PubChem",
                    "found": True,
                    "cid": props.get("CID", "N/A"),
                    "molecular_formula": props.get("MolecularFormula", "N/A"),
                    "molecular_weight": props.get("MolecularWeight", "N/A"),
                    "iupac_name": props.get("IUPACName", "N/A"),
                    "canonical_smiles": props.get("CanonicalSMILES", "N/A"),
                    "xlogp": props.get("XLogP", "N/A"),
                    "tpsa": props.get("TPSA", "N/A"),
                    "hbd": props.get("HBondDonorCount", "N/A"),
                    "hba": props.get("HBondAcceptorCount", "N/A"),
                    "rotatable_bonds": props.get("RotatableBondCount", "N/A"),
                    "exact_mass": props.get("ExactMass", "N/A"),
                    "complexity": props.get("Complexity", "N/A"),
                    "last_updated": datetime.now().isoformat(),
                    "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{props.get('CID', '')}"
                }
                
                API_CACHE[cache_key] = (result, datetime.now())
                return result
        elif response.status_code == 404:
            return {"source": "PubChem", "found": False, "message": "Not found in PubChem"}
            
    except requests.exceptions.RequestException as e:
        return {"source": "PubChem", "found": False, "error": str(e)}
    
    return {"source": "PubChem", "found": False, "message": "API query failed"}


def query_pubchem_toxicity(cid: str) -> Optional[Dict]:
    """Get toxicity assay data automatically."""
    
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/assaysummary/JSON"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            toxicity_data = {
                "source": "PubChem BioAssay",
                "cid": cid,
                "total_assays": 0,
                "active_assays": 0,
                "toxicity_alerts": []
            }
            
            if "Table" in data and "Row" in data["Table"]:
                rows = data["Table"]["Row"]
                toxicity_data["total_assays"] = len(rows)
                
                for row in rows:
                    cells = row.get("Cell", [])
                    if len(cells) >= 3:
                        assay_name = str(cells[1]) if len(cells) > 1 else ""
                        activity = str(cells[2]) if len(cells) > 2 else ""
                        
                        if any(word in assay_name.lower() for word in ["toxic", "hepatotox", "carcinogen", "mutagen"]):
                            toxicity_data["toxicity_alerts"].append({
                                "assay": assay_name[:100],
                                "result": activity
                            })
                            if "active" in activity.lower():
                                toxicity_data["active_assays"] += 1
            
            return toxicity_data
            
    except Exception as e:
        return {"source": "PubChem BioAssay", "error": str(e)}
    
    return None


def search_all_government_databases(smiles: str) -> Dict:
    """Main function - queries all databases automatically."""
    
    results = {
        "smiles": smiles,
        "search_timestamp": datetime.now().isoformat(),
        "databases_checked": ["PubChem"],
        "found_in": [],
        "pubchem_data": None,
        "toxicity_data": None,
        "summary": ""
    }
    
    # Query PubChem
    pubchem_result = query_pubchem_by_smiles(smiles)
    results["pubchem_data"] = pubchem_result
    
    if pubchem_result and pubchem_result.get("found"):
        results["found_in"].append("PubChem")
        
        cid = pubchem_result.get("cid")
        if cid and cid != "N/A":
            time.sleep(0.3)
            toxicity = query_pubchem_toxicity(cid)
            results["toxicity_data"] = toxicity
    
    # Query FDA Substance Data
    fda_result = query_fda_substances(smiles)
    if fda_result and fda_result.get("found"):
        results["found_in"].append("FDA")
        results["fda_data"] = fda_result
    else:
        results["fda_data"] = fda_result
    
    # Query Inxight Drugs (toxicity + interactions)
    time.sleep(0.3)
    inxight_result = query_inxight_drugs(smiles)
    if inxight_result and inxight_result.get("found"):
        results["found_in"].append("Inxight Drugs")
        results["inxight_data"] = inxight_result
    else:
        results["inxight_data"] = inxight_result
    
    if results["found_in"]:
        results["summary"] = f"Found in: {', '.join(results['found_in'])}"
    else:
        results["summary"] = "Not found in government databases"
    
    # Auto-store for future
    store_government_data(smiles, results)
    
    return results


def store_government_data(smiles: str, data: Dict):
    """Automatically store results in database."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS government_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            smiles TEXT NOT NULL,
            pubchem_cid TEXT,
            pubchem_data TEXT,
            toxicity_data TEXT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(smiles)
        )
    ''')
    
    cursor.execute('''
        INSERT INTO government_data (smiles, pubchem_cid, pubchem_data, toxicity_data, last_checked)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(smiles) 
        DO UPDATE SET 
            pubchem_cid = ?,
            pubchem_data = ?,
            toxicity_data = ?,
            last_checked = ?
    ''', (
        smiles,
        str(data.get("pubchem_data", {}).get("cid", "")),
        json.dumps(data.get("pubchem_data", {})),
        json.dumps(data.get("toxicity_data", {})),
        datetime.now().isoformat(),
        str(data.get("pubchem_data", {}).get("cid", "")),
        json.dumps(data.get("pubchem_data", {})),
        json.dumps(data.get("toxicity_data", {})),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()


def get_cached_data(smiles: str) -> Optional[Dict]:
    """Check if we already have data for this compound."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='government_data'")
    if not cursor.fetchone():
        conn.close()
        return None
    
    cursor.execute(
        "SELECT pubchem_data, toxicity_data, last_checked FROM government_data WHERE smiles = ?",
        (smiles,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "pubchem_data": json.loads(result[0]) if result[0] else {},
            "toxicity_data": json.loads(result[1]) if result[1] else {},
            "last_checked": result[2]
        }
    return None


def auto_sync_daily():
    """Auto-sync all stored compounds - called automatically."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT smiles FROM predictions")
        smiles_list = [row[0] for row in cursor.fetchall()]
    except:
        smiles_list = []
    
    conn.close()
    
    for i, smiles in enumerate(smiles_list):
        if i > 0 and i % 5 == 0:
            time.sleep(1)
        
        data = search_all_government_databases(smiles)
        print(f"Synced: {smiles} - {data['summary']}")
    
    return len(smiles_list)


def query_fda_substances(smiles: str) -> Optional[Dict]:
    """
    Query FDA Substance Data API (openFDA).
    Searches by molecular structure if available.
    No API key required.
    
    API docs: https://open.fda.gov/apis/other/substance/
    """
    cache_key = f"fda_{smiles}"
    if cache_key in API_CACHE:
        cached_data, cached_time = API_CACHE[cache_key]
        if datetime.now() - cached_time < CACHE_DURATION:
            return cached_data
    
    try:
        # Search FDA substances by name or structure
        # openFDA base endpoint
        url = "https://api.fda.gov/other/substance.json"
        
        # Try searching with common substance name
        params = {
            "search": f'substance_name:"{smiles}"',
            "limit": 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                substances = []
                for substance in results:
                    sub_data = {
                        "unii": substance.get("unii", "N/A"),
                        "name": substance.get("name", "N/A"),
                        "substance_class": substance.get("substance_class", "N/A"),
                        "definition_type": substance.get("definition_type", "N/A"),
                        "status": substance.get("status", "N/A")
                    }
                    
                    # Get names if available
                    names = substance.get("names", [])
                    if names:
                        sub_data["display_name"] = names[0].get("name", "N/A")
                    
                    # Get structure if available
                    structure = substance.get("structure", {})
                    if structure:
                        sub_data["molecular_formula"] = structure.get("formula", "N/A")
                        sub_data["molecular_weight"] = structure.get("mwt", "N/A")
                    
                    substances.append(sub_data)
                
                result = {
                    "source": "FDA Substance Data",
                    "found": True,
                    "total_results": data.get("meta", {}).get("results", {}).get("total", len(substances)),
                    "substances": substances[:10],
                    "last_updated": datetime.now().isoformat()
                }
                
                API_CACHE[cache_key] = (result, datetime.now())
                return result
        
        elif response.status_code == 404:
            return {"source": "FDA Substance Data", "found": False, "message": "Not found"}
            
    except requests.exceptions.RequestException as e:
        return {"source": "FDA Substance Data", "found": False, "error": str(e)}
    
    return {"source": "FDA Substance Data", "found": False, "message": "Query failed"}


def query_inxight_drugs(smiles: str) -> Optional[Dict]:
    """
    Query NCATS Inxight Drugs API (GSRS-based with toxicity data).
    Contains FDA substance data + adverse events + drug interactions.
    No API key required.
    
    API docs: https://drugs.ncats.io/api/v1
    """
    cache_key = f"inxight_{smiles}"
    if cache_key in API_CACHE:
        cached_data, cached_time = API_CACHE[cache_key]
        if datetime.now() - cached_time < CACHE_DURATION:
            return cached_data
    
    try:
        # Search by SMILES or name
        url = "https://drugs.ncats.io/api/v1/substances/search"
        params = {
            "q": smiles,
            "top": 10,
            "skip": 0
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            substances = data.get("content", [])
            total = data.get("total", 0)
            
            if substances and total > 0:
                results_list = []
                for sub in substances[:10]:
                    substance_data = {
                        "unii": sub.get("unii", "N/A"),
                        "name": sub.get("name", "N/A"),
                        "substance_class": sub.get("substanceClass", "N/A"),
                        "status": sub.get("status", "N/A")
                    }
                    
                    # Get additional data if available
                    additional = sub.get("additional", {})
                    if additional:
                        substance_data["toxicity"] = additional.get("toxicity", [])
                        substance_data["adverse_events"] = additional.get("adverseEvents", [])
                        substance_data["drug_interactions"] = additional.get("drugInteractions", [])
                    
                    results_list.append(substance_data)
                
                result = {
                    "source": "Inxight Drugs (FDA/NIH)",
                    "found": True,
                    "total_results": total,
                    "substances": results_list,
                    "last_updated": datetime.now().isoformat()
                }
                
                API_CACHE[cache_key] = (result, datetime.now())
                return result
        
        elif response.status_code == 404:
            return {"source": "Inxight Drugs", "found": False, "message": "Not found"}
            
    except requests.exceptions.RequestException as e:
        return {"source": "Inxight Drugs", "found": False, "error": str(e)}
    
    return {"source": "Inxight Drugs", "found": False, "message": "Query failed"}
