"""
Pharmacokinetics Dashboard Module
Combines all ADME/PK outputs into unified dashboard with visualizations.
"""

import sys
import os
from typing import Dict, List

sys.path.insert(0, os.path.dirname(__file__))

from caco2_model import predict_caco2
from protein_binding_model import predict_protein_binding
from volume_distribution_model import predict_volume_distribution
from clearance_model import predict_clearance_and_halflife
from cyp450_model import predict_all_cyp
from glucuronidation_model import predict_glucuronidation
from metabolite_generator import assess_metabolic_activation_risk


def run_full_pk_panel(smiles: str) -> Dict:
    """
    Run complete Pharmacokinetics panel.
    Combines all ADME/PK predictions into one comprehensive result.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Complete PK dashboard dictionary
    """
    results = {
        "smiles": smiles,
        "absorption": {},
        "distribution": {},
        "metabolism": {},
        "excretion": {},
        "safety": {},
        "pk_score": 0,
        "flags": []
    }
    
    # ABSORPTION
    caco2 = predict_caco2(smiles)
    results["absorption"]["caco2"] = caco2
    if caco2.get("absorption") == "Low":
        results["flags"].append("Poor intestinal absorption")
    
    # DISTRIBUTION
    ppb = predict_protein_binding(smiles)
    results["distribution"]["protein_binding"] = ppb
    
    vd = predict_volume_distribution(smiles)
    results["distribution"]["volume_distribution"] = vd
    
    # METABOLISM
    cyp = predict_all_cyp(smiles)
    results["metabolism"]["cyp450"] = cyp
    
    gluc = predict_glucuronidation(smiles)
    results["metabolism"]["phase2"] = gluc
    
    metab_risk = assess_metabolic_activation_risk(smiles)
    results["metabolism"]["metabolic_activation"] = metab_risk
    
    if metab_risk["metabolic_activation_risk"] in ["High", "Medium"]:
        results["flags"].append(f"Metabolic activation risk: {metab_risk['metabolic_activation_risk']}")
    
    # EXCRETION
    vd_val = vd.get("vd", 0.5)
    cl_result = predict_clearance_and_halflife(smiles, vd_val)
    results["excretion"]["clearance"] = cl_result
    
    # SAFETY
    from therapeutic_index_model import predict_therapeutic_index
    ti = predict_therapeutic_index(smiles)
    results["safety"]["therapeutic_index"] = ti
    
    if ti.get("safety_class") in ["Narrow", "Critical"]:
        results["flags"].append(f"Narrow therapeutic index: {ti.get('safety_class')}")
    
    # Calculate PK Score (weighted)
    score = 100
    
    # Absorption penalty
    if caco2.get("absorption") == "Low":
        score -= 20
    elif caco2.get("absorption") == "Moderate":
        score -= 5
    
    # Distribution penalty
    if ppb.get("binding_class") == "High":
        score -= 5  # High binding can be managed
    
    # Metabolism penalty
    if cyp.get("total_inhibited", 0) >= 2:
        score -= 15
    elif cyp.get("total_inhibited", 0) == 1:
        score -= 5
    
    if metab_risk["metabolic_activation_risk"] == "High":
        score -= 20
    elif metab_risk["metabolic_activation_risk"] == "Medium":
        score -= 10
    
    # Safety penalty
    if ti.get("safety_class") == "Critical":
        score -= 25
    elif ti.get("safety_class") == "Narrow":
        score -= 10
    
    results["pk_score"] = max(0, score)
    
    return results


def get_pk_summary_table(results: Dict) -> List[Dict]:
    """
    Generate compact PK summary table for dashboard display.
    
    Args:
        results: PK dashboard results
        
    Returns:
        List of dictionaries for table display
    """
    summary = []
    
    # Absorption
    caco2 = results.get("absorption", {}).get("caco2", {})
    summary.append({
        "Parameter": "Caco-2 Permeability",
        "Value": f"{caco2.get('logPapp', 'N/A')} log cm/s",
        "Classification": caco2.get("absorption", "N/A"),
        "Status": "✅" if caco2.get("absorption") in ["High", "Moderate"] else "⚠️"
    })
    
    # Distribution
    ppb = results.get("distribution", {}).get("protein_binding", {})
    summary.append({
        "Parameter": "Protein Binding",
        "Value": f"{ppb.get('percent_bound', 'N/A')}% bound",
        "Classification": ppb.get("binding_class", "N/A"),
        "Status": "✅" if ppb.get("binding_class") != "High" else "⚠️"
    })
    
    vd = results.get("distribution", {}).get("volume_distribution", {})
    summary.append({
        "Parameter": "Volume of Distribution",
        "Value": f"{vd.get('vd', 'N/A')} L/kg",
        "Classification": vd.get("vd_class", "N/A"),
        "Status": "✅"
    })
    
    # Metabolism
    cyp = results.get("metabolism", {}).get("cyp450", {})
    summary.append({
        "Parameter": "CYP450 Inhibition",
        "Value": f"{cyp.get('total_inhibited', 0)}/3 isoforms",
        "Classification": cyp.get("overall_risk", "N/A"),
        "Status": "⚠️" if cyp.get("total_inhibited", 0) > 0 else "✅"
    })
    
    # Excretion
    cl = results.get("excretion", {}).get("clearance", {})
    t_half = cl.get("half_life", "N/A")
    summary.append({
        "Parameter": "Half-Life (t1/2)",
        "Value": f"{t_half} hours" if t_half != "N/A" else "N/A",
        "Classification": cl.get("half_life_class", "N/A") if "half_life_class" in cl else "N/A",
        "Status": "✅"
    })
    
    # Safety
    ti = results.get("safety", {}).get("therapeutic_index", {})
    ti_status = "❌" if ti.get("safety_class") == "Critical" else "⚠️" if ti.get("safety_class") == "Narrow" else "✅"
    summary.append({
        "Parameter": "Therapeutic Index",
        "Value": f"TI = {ti.get('therapeutic_index', 'N/A')}",
        "Classification": ti.get("safety_class", "N/A"),
        "Status": ti_status
    })
    
    return summary


def get_radar_chart_data(results: Dict) -> Dict:
    """
    Generate data for radar/spider chart visualization.
    Normalized values 0-100 for each PK parameter.
    
    Args:
        results: PK dashboard results
        
    Returns:
        Dictionary with radar chart data
    """
    caco2 = results.get("absorption", {}).get("caco2", {})
    ppb = results.get("distribution", {}).get("protein_binding", {})
    vd = results.get("distribution", {}).get("volume_distribution", {})
    cl = results.get("excretion", {}).get("clearance", {})
    ti = results.get("safety", {}).get("therapeutic_index", {})
    
    # Normalize each parameter to 0-100 scale
    radar = {
        "Absorption": min(100, max(0, (float(caco2.get("logPapp", -7)) + 7) * 25)),
        "Protein Binding": 100 - ppb.get("percent_bound", 50),
        "Distribution": min(100, vd.get("vd", 1) * 20),
        "Metabolism": 100 - (results.get("metabolism", {}).get("cyp450", {}).get("total_inhibited", 0) * 30),
        "Half-Life": min(100, max(0, (float(cl.get("half_life", 4)) - 0.5) * 10)),
        "Safety Margin": min(100, ti.get("therapeutic_index", 10) * 2),
    }
    
    return radar
