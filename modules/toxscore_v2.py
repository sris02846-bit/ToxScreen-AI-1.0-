"""
ToxScore v2 - Composite Toxicity Scoring Module
Combines Tier1 score, organ ML predictions, ADME alerts, and metabolic risk.
Features user-adjustable weights for customizable scoring.
"""

import sys
import os
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(__file__))

# Default weights for ToxScore v2
DEFAULT_WEIGHTS = {
    "tier1_druglikeness": 0.15,
    "tier1_toxicophores": 0.10,
    "organ_toxicity": 0.30,
    "adme_panel": 0.20,
    "metabolic_activation": 0.10,
    "pk_parameters": 0.15,
}


def calculate_tier1_score(lipinski_violations: int, veber_violations: int, 
                          toxicophore_score: float) -> float:
    """
    Calculate Tier 1 (Rule-based) score.
    
    Args:
        lipinski_violations: Number of Lipinski violations
        veber_violations: Number of Veber violations
        toxicophore_score: Toxicophore risk score (0-100)
        
    Returns:
        Tier 1 score (0-100)
    """
    score = 100.0
    
    # Lipinski penalty
    score -= lipinski_violations * 15
    
    # Veber penalty
    score -= veber_violations * 10
    
    # Toxicophore penalty
    score -= toxicophore_score * 0.3
    
    return max(0, min(100, score))


def calculate_organ_toxicity_score(organ_results: Dict) -> Dict:
    """
    Calculate organ toxicity sub-score from ML predictions.
    
    Args:
        organ_results: Results from run_all_toxicity_tests
        
    Returns:
        Dictionary with organ score and details
    """
    total_organs = len(organ_results.get("models", {}))
    toxic_hits = organ_results.get("toxic_hits", 0)
    
    if total_organs == 0:
        return {"score": 100, "hits": 0, "details": []}
    
    # Base score
    score = 100.0
    
    # Penalty per toxic organ
    for organ_name, data in organ_results.get("models", {}).items():
        if data.get("is_toxic", False):
            risk = data.get("risk_level", "Low")
            if risk == "High":
                score -= 20
            elif risk == "Medium":
                score -= 10
            else:
                score -= 5
    
    return {
        "score": max(0, score),
        "hits": toxic_hits,
        "total_organs": total_organs,
        "details": organ_results.get("models", {})
    }


def calculate_adme_score(adme_results: Dict) -> float:
    """
    Calculate ADME sub-score.
    
    Args:
        adme_results: Results from run_full_adme_panel
        
    Returns:
        ADME score (0-100)
    """
    return adme_results.get("adme_score", 100)


def calculate_metabolic_risk_score(metabolic_results: Dict) -> float:
    """
    Calculate metabolic activation risk score.
    
    Args:
        metabolic_results: Results from assess_metabolic_activation_risk
        
    Returns:
        Metabolic risk score (0-100, higher = safer)
    """
    risk = metabolic_results.get("metabolic_activation_risk", "Low")
    reactive = metabolic_results.get("reactive_metabolites", 0)
    
    if risk == "High":
        return max(0, 100 - reactive * 25)
    elif risk == "Medium":
        return max(0, 100 - reactive * 15)
    else:
        return 100


def calculate_pk_score(pk_results: Dict) -> float:
    """
    Calculate PK parameter score.
    
    Args:
        pk_results: Results from run_full_pk_panel
        
    Returns:
        PK score (0-100)
    """
    return pk_results.get("pk_score", 100)


def compute_toxscore_v2(
    lipinski_violations: int = 0,
    veber_violations: int = 0,
    toxicophore_score: float = 0,
    organ_results: Optional[Dict] = None,
    adme_results: Optional[Dict] = None,
    metabolic_results: Optional[Dict] = None,
    pk_results: Optional[Dict] = None,
    weights: Optional[Dict] = None
) -> Dict:
    """
    Compute composite ToxScore v2.
    
    Args:
        lipinski_violations: Lipinski rule violations
        veber_violations: Veber rule violations
        toxicophore_score: Toxicophore risk score
        organ_results: Organ toxicity results
        adme_results: ADME panel results
        metabolic_results: Metabolic activation results
        pk_results: PK dashboard results
        weights: Optional custom weights
        
    Returns:
        Complete ToxScore v2 dictionary
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()
    
    # Calculate sub-scores
    tier1 = calculate_tier1_score(lipinski_violations, veber_violations, toxicophore_score)
    
    organ_sub = calculate_organ_toxicity_score(organ_results) if organ_results else {"score": 100, "hits": 0}
    
    adme_sub = calculate_adme_score(adme_results) if adme_results else 100
    
    metabolic_sub = calculate_metabolic_risk_score(metabolic_results) if metabolic_results else 100
    
    pk_sub = calculate_pk_score(pk_results) if pk_results else 100
    
    # Weighted composite score
    composite = (
        tier1 * weights["tier1_druglikeness"] +
        organ_sub["score"] * weights["organ_toxicity"] +
        adme_sub * weights["adme_panel"] +
        metabolic_sub * weights["metabolic_activation"] +
        pk_sub * weights["pk_parameters"]
    )
    
    # Add toxicophore weight
    if toxicophore_score > 0:
        composite -= toxicophore_score * weights["tier1_toxicophores"]
    
    composite = max(0, min(100, round(composite, 1)))
    
    # Determine grade
    if composite >= 80:
        grade = "A"
        grade_color = "#00ff66"
        interpretation = "Excellent safety profile. Suitable for development."
    elif composite >= 65:
        grade = "B"
        grade_color = "#00ffff"
        interpretation = "Good safety profile. Minor concerns to address."
    elif composite >= 50:
        grade = "C"
        grade_color = "#ffaa00"
        interpretation = "Moderate concerns. Further optimization recommended."
    elif composite >= 35:
        grade = "D"
        grade_color = "#ff6600"
        interpretation = "Significant safety concerns. Major optimization needed."
    else:
        grade = "F"
        grade_color = "#ff3355"
        interpretation = "Critical safety issues. Not recommended for development."
    
    return {
        "composite_score": composite,
        "grade": grade,
        "grade_color": grade_color,
        "interpretation": interpretation,
        "sub_scores": {
            "tier1_rules": round(tier1, 1),
            "organ_toxicity": round(organ_sub["score"], 1),
            "adme_panel": round(adme_sub, 1),
            "metabolic_risk": round(metabolic_sub, 1),
            "pk_parameters": round(pk_sub, 1),
        },
        "weights_used": weights,
        "organ_hits": organ_sub.get("hits", 0),
        "total_components": 5
    }


def get_gauge_html(score: float, color: str, size: int = 200) -> str:
    """
    Generate HTML for a visual gauge meter.
    
    Args:
        score: Score value (0-100)
        color: Hex color for the gauge
        size: Size in pixels
        
    Returns:
        HTML string for the gauge
    """
    angle = (score / 100) * 180
    
    html = f"""
    <div style="position:relative;width:{size}px;height:{size/2}px;margin:0 auto;overflow:hidden;">
        <div style="position:absolute;width:{size}px;height:{size}px;border-radius:50%;
        background:conic-gradient({color} 0deg {angle}deg, #333 {angle}deg 180deg);
        clip-path:polygon(0 0, 100% 0, 100% 50%, 0 50%);"></div>
        <div style="position:absolute;bottom:10px;width:100%;text-align:center;
        font-family:Orbitron;font-size:{size*0.15}px;font-weight:900;color:{color};">
        {score}</div>
    </div>
    """
    return html
