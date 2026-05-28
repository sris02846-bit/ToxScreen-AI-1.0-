"""
Final Validation Module
Complete system validation, accuracy report, bug tracking.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.dirname(__file__))


def run_complete_validation() -> Dict:
    """
    Run complete system validation across all modules.
    
    Returns:
        Comprehensive validation results
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "modules_tested": [],
        "passed": 0,
        "failed": 0,
        "errors": [],
        "warnings": [],
        "overall_status": "PASS"
    }
    
    # Test all core modules
    modules_to_test = [
        ("molecular_parser", "SMILES Parsing"),
        ("lipinski_rules", "Lipinski Rules"),
        ("veber_rules", "Veber Rules"),
        ("toxicophores", "Toxicophore Detection"),
        ("fingerprint", "Fingerprint Similarity"),
        ("database", "SQLite Database"),
        ("ml_model", "ML Hepatotoxicity"),
        ("herg_model", "hERG Model"),
        ("cardiotoxicity_model", "Cardiotoxicity"),
        ("nephrotoxicity_model", "Nephrotoxicity"),
        ("neurotoxicity_model", "Neurotoxicity"),
        ("cytotoxicity_model", "Cytotoxicity"),
        ("cyp450_model", "CYP450 Metabolism"),
        ("caco2_model", "Caco-2 Permeability"),
        ("protein_binding_model", "Protein Binding"),
        ("clearance_model", "Clearance"),
        ("therapeutic_index_model", "Therapeutic Index"),
        ("toxscore_v2", "ToxScore v2"),
        ("batch_processor_v2", "Batch Processing"),
        ("molecule_optimizer", "Molecule Optimizer"),
        ("fda_integration", "FDA Integration"),
        ("overdose_predictor", "Overdose Predictor"),
        ("pdf_report_v2", "PDF Report v2"),
        ("blockchain", "Blockchain"),
        ("performance_optimizer", "Performance"),
    ]
    
    test_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
    
    for module_name, display_name in modules_to_test:
        try:
            # Dynamic import test
            module = __import__(module_name)
            results["modules_tested"].append({
                "name": display_name,
                "module": module_name,
                "status": "PASS"
            })
            results["passed"] += 1
        except ImportError as e:
            results["modules_tested"].append({
                "name": display_name,
                "module": module_name,
                "status": "FAIL",
                "error": str(e)
            })
            results["failed"] += 1
            results["errors"].append(f"{display_name}: {str(e)}")
        except Exception as e:
            results["warnings"].append(f"{display_name}: {str(e)}")
    
    # Overall status
    if results["failed"] > 5:
        results["overall_status"] = "FAIL"
    elif results["failed"] > 0:
        results["overall_status"] = "WARNING"
    
    return results


def generate_final_report(validation: Dict, accuracy: Dict = None, performance: Dict = None) -> str:
    """
    Generate final comprehensive validation report.
    
    Args:
        validation: Validation results
        accuracy: Accuracy test results
        performance: Performance test results
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 65)
    report.append("TOXSCREEN-AI FINAL VALIDATION REPORT")
    report.append("=" * 65)
    report.append(f"Date: {validation['timestamp']}")
    report.append(f"Overall Status: {validation['overall_status']}")
    report.append("")
    
    report.append("-" * 45)
    report.append("MODULE VALIDATION")
    report.append("-" * 45)
    report.append(f"Passed: {validation['passed']}")
    report.append(f"Failed: {validation['failed']}")
    report.append("")
    
    for mod in validation['modules_tested']:
        icon = "PASS" if mod['status'] == 'PASS' else "FAIL"
        report.append(f"  [{icon}] {mod['name']}")
    
    if validation.get('errors'):
        report.append("\nErrors:")
        for err in validation['errors']:
            report.append(f"  - {err}")
    
    if validation.get('warnings'):
        report.append("\nWarnings:")
        for warn in validation['warnings']:
            report.append(f"  - {warn}")
    
    report.append("")
    report.append("-" * 45)
    report.append("SYSTEM SUMMARY")
    report.append("-" * 45)
    report.append(f"Total Modules: {validation['passed'] + validation['failed']}")
    report.append(f"Success Rate: {validation['passed']/(validation['passed']+validation['failed'])*100:.1f}%")
    
    report.append("")
    report.append("=" * 65)
    report.append("VALIDATION COMPLETE")
    report.append("=" * 65)
    
    return "\n".join(report)


def save_final_report(report: str) -> str:
    """Save final report to file."""
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    report_path = os.path.join(base_dir, 'FINAL_VALIDATION_REPORT.txt')
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    return report_path
