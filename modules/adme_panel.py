"""
Unified ADME Panel Module
Combines CYP450, Glucuronidation, Caco-2, and Metabolic Activation results.
"""

import sys
import os
from typing import Dict, List

sys.path.insert(0, os.path.dirname(__file__))

from cyp450_model import predict_all_cyp
from glucuronidation_model import predict_glucuronidation
from caco2_model import predict_caco2
from metabolite_generator import assess_metabolic_activation_risk


def run_full_adme_panel(smiles: str) -> Dict:
    """
    Run complete ADME panel on a compound.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Comprehensive ADME results dictionary
    """
    results = {
        "smiles": smiles,
        "cyp450": None,
        "phase2": None,
        "permeability": None,
        "metabolic_activation": None,
        "adme_score": 0,
        "flags": []
    }
    
    # 1. CYP450 Inhibition
    results["cyp450"] = predict_all_cyp(smiles)
    if results["cyp450"]["total_inhibited"] > 0:
        results["flags"].append(f"CYP450 inhibition: {results['cyp450']['total_inhibited']} isoforms")
    
    # 2. Phase II Glucuronidation
    results["phase2"] = predict_glucuronidation(smiles)
    
    # 3. Caco-2 Permeability
    results["permeability"] = predict_caco2(smiles)
    if results["permeability"].get("absorption") == "Low":
        results["flags"].append("Poor intestinal absorption")
    
    # 4. Metabolic Activation Risk
    results["metabolic_activation"] = assess_metabolic_activation_risk(smiles)
    if results["metabolic_activation"]["metabolic_activation_risk"] in ["High", "Medium"]:
        results["flags"].append(f"Metabolic activation risk: {results['metabolic_activation']['metabolic_activation_risk']}")
    
    # Calculate ADME score
    score = 100
    
    # Penalties
    if results["cyp450"]["total_inhibited"] >= 2:
        score -= 25
    elif results["cyp450"]["total_inhibited"] == 1:
        score -= 10
    
    if results["permeability"].get("absorption") == "Low":
        score -= 15
    elif results["permeability"].get("absorption") == "Moderate":
        score -= 5
    
    if results["metabolic_activation"]["metabolic_activation_risk"] == "High":
        score -= 25
    elif results["metabolic_activation"]["metabolic_activation_risk"] == "Medium":
        score -= 10
    
    results["adme_score"] = max(0, score)
    
    return results


def get_adme_summary_table(results: Dict) -> List[Dict]:
    """
    Generate summary table for ADME panel display.
    
    Args:
        results: ADME panel results
        
    Returns:
        List of dictionaries for table display
    """
    summary = []
    
    # CYP450 row
    cyp = results.get("cyp450", {})
    summary.append({
        "Test": "CYP450 Inhibition",
        "Result": f"{cyp.get('total_inhibited', 0)}/3 isoforms inhibited",
        "Risk": cyp.get("overall_risk", "N/A"),
        "Status": "⚠️" if cyp.get("total_inhibited", 0) > 0 else "✅"
    })
    
    # Phase II row
    phase2 = results.get("phase2", {})
    summary.append({
        "Test": "Phase II (Glucuronidation)",
        "Result": phase2.get("prediction", "N/A"),
        "Risk": "Normal",
        "Status": "✅"
    })
    
    # Permeability row
    perm = results.get("permeability", {})
    status = "✅" if perm.get("absorption") in ["High", "Moderate"] else "⚠️"
    summary.append({
        "Test": "Caco-2 Permeability",
        "Result": f"logPapp: {perm.get('logPapp', 'N/A')} ({perm.get('absorption', 'N/A')})",
        "Risk": perm.get("absorption", "N/A"),
        "Status": status
    })
    
    # Metabolic activation row
    met = results.get("metabolic_activation", {})
    met_status = "❌" if met.get("metabolic_activation_risk") == "High" else "⚠️" if met.get("metabolic_activation_risk") == "Medium" else "✅"
    summary.append({
        "Test": "Metabolic Activation",
        "Result": f"{met.get('reactive_metabolites', 0)} reactive metabolites",
        "Risk": met.get("metabolic_activation_risk", "N/A"),
        "Status": met_status
    })
    
    return summary
