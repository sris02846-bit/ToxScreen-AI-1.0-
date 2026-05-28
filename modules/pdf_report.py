"""
PDF Report Generation Module
Creates professional PDF reports using fpdf2.
Report Order:
1. Molecular Information
2. Drug-Likeness Score
3. Lipinski Rule of Five
4. Veber Rules
5. Toxicophore Detection
6. ML Hepatotoxicity Prediction
7. Blockchain Verification
"""

from fpdf import FPDF
from datetime import datetime
import os
from typing import Dict, List, Optional


class ToxScreenPDF(FPDF):
    """Custom PDF report class for ToxScreen-AI."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Custom header with luxury branding."""
        self.set_font('Helvetica', 'B', 22)
        self.set_text_color(0, 100, 150)
        self.cell(0, 10, 'ToxScreen-AI', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'Computational Drug Toxicity Screening Report', 0, 1, 'C')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
    
    def footer(self):
        """Custom footer."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | ToxScreen-AI', 0, 0, 'C')
    
    def section_title(self, title: str, number: int):
        """Add a numbered section title."""
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 80, 120)
        self.cell(0, 8, f'{number}. {title}', 0, 1, 'L')
        self.set_draw_color(0, 80, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
    
    def info_row(self, label: str, value: str):
        """Add an info row with label and value."""
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(60, 60, 60)
        self.cell(65, 6, label + ':', 0, 0, 'L')
        self.set_font('Helvetica', '', 9)
        self.set_text_color(30, 30, 30)
        self.cell(0, 6, str(value), 0, 1, 'L')
    
    def result_badge(self, result: str):
        """Add a colored result badge."""
        colors = {
            'EXCELLENT': (0, 180, 0),
            'Excellent': (0, 180, 0),
            'GOOD': (0, 120, 200),
            'Good': (0, 120, 200),
            'MODERATE': (200, 150, 0),
            'Moderate': (200, 150, 0),
            'POOR': (200, 0, 0),
            'Poor': (200, 0, 0)
        }
        color = colors.get(result, (100, 100, 100))
        
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 14)
        self.cell(55, 8, result, 0, 1, 'C', True)
        self.ln(3)
    
    def pass_fail_badge(self, status: str):
        """Add PASS/FAIL badge."""
        if status == 'PASS':
            self.set_fill_color(0, 180, 100)
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(200, 50, 50)
            self.set_text_color(255, 255, 255)
        
        self.set_font('Helvetica', 'B', 8)
        self.cell(18, 5, status, 0, 0, 'C', True)


def generate_single_report(smiles: str, results: Dict, blockchain_tx: str = None, 
                           ml_result: Dict = None, toxicophore_data: Dict = None) -> str:
    """
    Generate a PDF report for a single molecule.
    
    Report Order:
    1. Molecular Information
    2. Drug-Likeness Score
    3. Lipinski Rule of Five
    4. Veber Rules
    5. Toxicophore Detection
    6. ML Hepatotoxicity Prediction
    7. Blockchain Verification
    
    Args:
        smiles: SMILES string
        results: Dictionary of analysis results
        blockchain_tx: Optional blockchain transaction hash
        ml_result: Optional ML prediction result
        toxicophore_data: Optional toxicophore detection data
        
    Returns:
        Path to generated PDF file
    """
    pdf = ToxScreenPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # ============ 1. MOLECULAR INFORMATION ============
    pdf.section_title('MOLECULAR INFORMATION', 1)
    
    pdf.info_row('SMILES', smiles)
    pdf.info_row('Molecular Weight', f"{results.get('Molecular_Weight', 'N/A')} g/mol")
    pdf.info_row('Molecular Formula', results.get('Molecular_Formula', 'N/A'))
    
    # Add additional molecular properties if available
    if 'Heavy_Atom_Count' in results:
        pdf.info_row('Heavy Atom Count', str(results.get('Heavy_Atom_Count', 'N/A')))
    if 'Ring_Count' in results:
        pdf.info_row('Ring Count', str(results.get('Ring_Count', 'N/A')))
    
    pdf.ln(6)
    
    # ============ 2. DRUG-LIKENESS SCORE ============
    pdf.section_title('DRUG-LIKENESS SCORE', 2)
    
    score = results.get('DrugLikeness_Score', 0)
    result_text = results.get('Result', 'N/A')
    
    # Score display
    pdf.set_font('Helvetica', 'B', 36)
    if score >= 80:
        pdf.set_text_color(0, 180, 0)
    elif score >= 60:
        pdf.set_text_color(0, 120, 200)
    elif score >= 40:
        pdf.set_text_color(200, 150, 0)
    else:
        pdf.set_text_color(200, 0, 0)
    
    pdf.cell(0, 18, f'{score}/100', 0, 1, 'C')
    pdf.result_badge(result_text)
    
    # Score interpretation
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    
    if score >= 80:
        interpretation = "Excellent drug-like properties. Compound meets all major criteria for oral bioavailability."
    elif score >= 60:
        interpretation = "Good drug-like profile. Minor violations that may be acceptable with formulation."
    elif score >= 40:
        interpretation = "Moderate concerns. Further optimization may be required for development."
    else:
        interpretation = "Poor drug-like properties. Significant issues that may hinder development."
    
    pdf.multi_cell(0, 5, interpretation)
    pdf.ln(6)
    
    # ============ 3. LIPINSKI RULE OF FIVE ============
    pdf.section_title('LIPINSKI RULE OF FIVE', 3)
    
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'Oral drug-likeness evaluation (no more than 1 violation recommended)', 0, 1, 'L')
    pdf.ln(3)
    
    lipinski_violations = results.get('Lipinski_Violations', 0)
    
    # Table header
    pdf.set_fill_color(0, 80, 120)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(8, 7, '', 0, 0, 'C', True)
    pdf.cell(72, 7, 'Rule', 0, 0, 'L', True)
    pdf.cell(35, 7, 'Value', 0, 0, 'C', True)
    pdf.cell(35, 7, 'Threshold', 0, 0, 'C', True)
    pdf.cell(25, 7, 'Status', 0, 1, 'C', True)
    
    # Lipinski rules
    lipinski_rules_list = [
        ("1", "Molecular Weight <= 500", f"{results.get('Molecular_Weight', 'N/A')} g/mol", "<= 500 g/mol", 
         "PASS" if float(str(results.get('Molecular_Weight', 0)).replace('N/A', '0')) <= 500 else "FAIL"),
        ("2", "LogP <= 5", str(results.get('XLogP', results.get('LogP', 'N/A'))), "<= 5",
         "PASS" if float(str(results.get('XLogP', results.get('LogP', 0))).replace('N/A', '0')) <= 5 else "FAIL"),
        ("3", "H-Bond Donors <= 5", str(results.get('HBD', results.get('HBD_Count', 'N/A'))), "<= 5",
         "PASS" if int(str(results.get('HBD', results.get('HBD_Count', 0))).replace('N/A', '0')) <= 5 else "FAIL"),
        ("4", "H-Bond Acceptors <= 10", str(results.get('HBA', results.get('HBA_Count', 'N/A'))), "<= 10",
         "PASS" if int(str(results.get('HBA', results.get('HBA_Count', 0))).replace('N/A', '0')) <= 10 else "FAIL"),
    ]
    
    for i, (num, rule, value, threshold, status) in enumerate(lipinski_rules_list):
        if i % 2 == 0:
            pdf.set_fill_color(245, 245, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.set_text_color(60, 60, 60)
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(8, 7, num, 0, 0, 'C', True)
        pdf.cell(72, 7, rule, 0, 0, 'L', True)
        pdf.cell(35, 7, value, 0, 0, 'C', True)
        pdf.cell(35, 7, threshold, 0, 0, 'C', True)
        
        # Status badge
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.pass_fail_badge(status)
        pdf.set_xy(x + 25, y)
        pdf.ln(7)
    
    # Violations summary
    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(0, 80, 120)
    pdf.cell(0, 7, f'Total Lipinski Violations: {lipinski_violations}/4', 0, 1, 'L')
    
    if lipinski_violations <= 1:
        pdf.set_text_color(0, 150, 0)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, 'Status: PASSES Lipinski Rule of Five', 0, 1, 'L')
    else:
        pdf.set_text_color(200, 0, 0)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, 'Status: FAILS Lipinski Rule of Five', 0, 1, 'L')
    
    pdf.ln(6)
    
    # ============ 4. VEBER RULES ============
    pdf.section_title('VEBER RULES', 4)
    
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'Oral bioavailability prediction criteria', 0, 1, 'L')
    pdf.ln(3)
    
    veber_violations = results.get('Veber_Violations', 0)
    
    # Table header
    pdf.set_fill_color(0, 80, 120)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(8, 7, '', 0, 0, 'C', True)
    pdf.cell(72, 7, 'Rule', 0, 0, 'L', True)
    pdf.cell(35, 7, 'Value', 0, 0, 'C', True)
    pdf.cell(35, 7, 'Threshold', 0, 0, 'C', True)
    pdf.cell(25, 7, 'Status', 0, 1, 'C', True)
    
    # Veber rules
    veber_rules_list = [
        ("1", "Rotatable Bonds <= 10", str(results.get('Rotatable_Bonds', 'N/A')), "<= 10",
         "PASS" if int(str(results.get('Rotatable_Bonds', 0)).replace('N/A', '0')) <= 10 else "FAIL"),
        ("2", "TPSA <= 140 Angstrom^2", f"{results.get('TPSA', 'N/A')} Angstrom^2", "<= 140 Angstrom^2",
         "PASS" if float(str(results.get('TPSA', 0)).replace('N/A', '0')) <= 140 else "FAIL"),
    ]
    
    for i, (num, rule, value, threshold, status) in enumerate(veber_rules_list):
        if i % 2 == 0:
            pdf.set_fill_color(245, 245, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.set_text_color(60, 60, 60)
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(8, 7, num, 0, 0, 'C', True)
        pdf.cell(72, 7, rule, 0, 0, 'L', True)
        pdf.cell(35, 7, value, 0, 0, 'C', True)
        pdf.cell(35, 7, threshold, 0, 0, 'C', True)
        
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.pass_fail_badge(status)
        pdf.set_xy(x + 25, y)
        pdf.ln(7)
    
    # Violations summary
    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(0, 80, 120)
    pdf.cell(0, 7, f'Total Veber Violations: {veber_violations}/2', 0, 1, 'L')
    
    if veber_violations == 0:
        pdf.set_text_color(0, 150, 0)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, 'Status: PASSES Veber Rules', 0, 1, 'L')
    else:
        pdf.set_text_color(200, 0, 0)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, 'Status: FAILS Veber Rules', 0, 1, 'L')
    
    pdf.ln(6)
    
    # ============ 5. TOXICOPHORE DETECTION ============
    pdf.section_title('TOXICOPHORE DETECTION', 5)
    
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'Structural alerts for potential toxicity', 0, 1, 'L')
    pdf.ln(3)
    
    toxicity_score = results.get('Toxicity_Score', 0)
    risk_level = results.get('Risk_Level', 'N/A')
    toxicophore_count = results.get('Toxicophore_Count', 0)
    
    # Summary box
    pdf.set_fill_color(245, 245, 250)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(0, 80, 120)
    pdf.cell(60, 7, 'Toxicity Score:', 0, 0, 'L', True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 7, f'{toxicity_score}/100', 0, 1, 'L', True)
    
    pdf.set_fill_color(245, 245, 250)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(0, 80, 120)
    pdf.cell(60, 7, 'Risk Level:', 0, 0, 'L', True)
    pdf.set_font('Helvetica', 'B', 10)
    
    if 'High' in str(risk_level):
        pdf.set_text_color(200, 0, 0)
    elif 'Medium' in str(risk_level) or 'Moderate' in str(risk_level):
        pdf.set_text_color(200, 150, 0)
    else:
        pdf.set_text_color(0, 150, 0)
    
    pdf.cell(0, 7, str(risk_level), 0, 1, 'L', True)
    
    pdf.set_fill_color(245, 245, 250)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(0, 80, 120)
    pdf.cell(60, 7, 'Alerts Found:', 0, 0, 'L', True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 7, str(toxicophore_count), 0, 1, 'L', True)
    
    # Toxicophore details if available
    if toxicophore_data and toxicophore_data.get('detected'):
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(0, 80, 120)
        pdf.cell(0, 6, 'Detected Toxicophores:', 0, 1, 'L')
        
        for tox in toxicophore_data['detected'][:10]:
            risk_color = (200, 0, 0) if tox.get('Risk Level') == 'High' else (200, 150, 0) if tox.get('Risk Level') == 'Medium' else (0, 150, 0)
            
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(*risk_color)
            pdf.cell(50, 5, f"[{tox.get('Risk Level', 'N/A')}]", 0, 0, 'L')
            
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(0, 5, f"{tox.get('Toxicophore', 'N/A')} - {tox.get('Match Count', 0)} match(es)", 0, 1, 'L')
    
    pdf.ln(6)
    
    # ============ 6. ML HEPATOTOXICITY PREDICTION ============
    pdf.section_title('ML HEPATOTOXICITY PREDICTION', 6)
    
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'RandomForest model trained on Tox21 SR-HSE data (83.3% accuracy)', 0, 1, 'L')
    pdf.ln(3)
    
    if ml_result and 'error' not in ml_result:
        prediction = ml_result.get('prediction', 'N/A')
        confidence = ml_result.get('confidence', 0)
        prob_hep = ml_result.get('probability_hepatotoxic', 0)
        prob_safe = ml_result.get('probability_safe', 0)
        ml_risk = ml_result.get('risk_level', 'N/A')
        
        # Prediction result
        pdf.set_fill_color(245, 245, 250)
        
        if 'Hepatotoxic' in str(prediction):
            pdf.set_text_color(200, 0, 0)
            pred_icon = '[WARNING]'
        else:
            pdf.set_text_color(0, 150, 0)
            pred_icon = '[SAFE]'
        
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, f'{pred_icon} Prediction: {prediction}', 0, 1, 'C', True)
        
        pdf.ln(3)
        
        # Confidence
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 80, 120)
        pdf.cell(0, 6, f'Confidence: {confidence}%', 0, 1, 'L')
        
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 6, f'Hepatotoxic Probability: {prob_hep}%', 0, 1, 'L')
        pdf.cell(0, 6, f'Safe Probability: {prob_safe}%', 0, 1, 'L')
        pdf.cell(0, 6, f'ML Risk Level: {ml_risk}', 0, 1, 'L')
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 8, 'ML prediction not available for this report.', 0, 1, 'C')
    
    pdf.ln(6)
    
    # ============ 7. BLOCKCHAIN VERIFICATION ============
    pdf.section_title('BLOCKCHAIN VERIFICATION', 7)
    
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'Immutable prediction record on Polygon Mumbai Testnet', 0, 1, 'L')
    pdf.ln(3)
    
    if blockchain_tx:
        # Transaction details
        pdf.set_fill_color(240, 248, 255)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(0, 80, 120)
        pdf.cell(40, 7, 'Network:', 0, 0, 'L', True)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 7, 'Polygon Mumbai Testnet', 0, 1, 'L', True)
        
        pdf.set_fill_color(240, 248, 255)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(0, 80, 120)
        pdf.cell(40, 7, 'TX Hash:', 0, 0, 'L', True)
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 7, blockchain_tx, 0, 1, 'L', True)
        
        pdf.set_fill_color(240, 248, 255)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(0, 80, 120)
        pdf.cell(40, 7, 'Explorer:', 0, 0, 'L', True)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 100, 200)
        pdf.cell(0, 7, f'https://mumbai.polygonscan.com/tx/{blockchain_tx}', 0, 1, 'L', True)
        
        pdf.ln(3)
        
        # Verification status
        pdf.set_fill_color(230, 255, 230)
        pdf.set_text_color(0, 150, 0)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 10, '[VERIFIED] Prediction recorded on blockchain', 0, 1, 'C', True)
        
        pdf.ln(2)
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 4, 'This prediction has been cryptographically hashed and stored on the Polygon Mumbai blockchain, ensuring immutability and verifiability of results.')
    else:
        pdf.set_fill_color(255, 245, 230)
        pdf.set_text_color(200, 150, 0)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 10, '[NOT RECORDED] Blockchain verification not performed', 0, 1, 'C', True)
        
        pdf.ln(2)
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 4, 'This prediction has not been recorded on the blockchain. Use the "Record on Blockchain" feature for immutable storage.')
    
    pdf.ln(8)
    
    # Disclaimer
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font('Helvetica', 'I', 7)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 4, 'Disclaimer: This report is generated by computational models and should be used for research purposes only. Results are not a substitute for professional medical advice or experimental validation. ToxScreen-AI makes no guarantees regarding the accuracy of predictions.')
    
    # Save
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"ToxScreen_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    pdf.output(filepath)
    
    return filepath
