"""
Enhanced PDF Report Module v2
Includes ML predictions, ADME, ToxScore, organ summaries, and QR code.
"""

from fpdf import FPDF
from datetime import datetime
import os
import sys
import qrcode
from io import BytesIO
from typing import Dict, Optional

sys.path.insert(0, os.path.dirname(__file__))


class ToxScreenPDFv2(FPDF):
    """Enhanced PDF report with QR code support."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(0, 80, 150)
        self.cell(0, 8, 'ToxScreen-AI v2', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'Comprehensive Drug Toxicity & PK Report', 0, 1, 'C')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')
    
    def section_title(self, title: str, number: int):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(0, 80, 120)
        self.cell(0, 7, f'{number}. {title}', 0, 1, 'L')
        self.set_draw_color(0, 80, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
    
    def info_row(self, label: str, value: str):
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(60, 60, 60)
        self.cell(60, 5, label + ':', 0, 0, 'L')
        self.set_font('Helvetica', '', 8)
        self.set_text_color(30, 30, 30)
        self.cell(0, 5, str(value), 0, 1, 'L')
    
    def add_qr_code(self, data: str, x: float, y: float, size: float = 30):
        """Add QR code to PDF."""
        qr = qrcode.QRCode(version=1, box_size=2, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to temporary buffer
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        # Save temp file for fpdf
        temp_path = "/tmp/qr_temp.png"
        with open(temp_path, 'wb') as f:
            f.write(buf.read())
        
        self.image(temp_path, x=x, y=y, w=size)
        os.remove(temp_path)


def generate_enhanced_report(
    smiles: str,
    basic_props: Dict,
    lipinski_violations: int,
    veber_violations: int,
    druglikeness_score: float,
    toxscore_data: Optional[Dict] = None,
    organ_results: Optional[Dict] = None,
    adme_results: Optional[Dict] = None,
    pk_results: Optional[Dict] = None,
    blockchain_tx: Optional[str] = None,
    toxicophore_count: int = 0
) -> str:
    """
    Generate enhanced PDF report with all modules.
    
    Args:
        smiles: SMILES string
        basic_props: Basic molecular properties
        lipinski_violations: Lipinski violations count
        veber_violations: Veber violations count
        druglikeness_score: Drug-likeness score
        toxscore_data: ToxScore v2 data
        organ_results: Organ toxicity results
        adme_results: ADME panel results
        pk_results: PK dashboard results
        blockchain_tx: Blockchain transaction hash
        toxicophore_count: Number of toxicophores detected
        
    Returns:
        Path to generated PDF
    """
    pdf = ToxScreenPDFv2()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    section_num = 1
    
    # 1. Molecular Information
    pdf.section_title('MOLECULAR INFORMATION', section_num)
    section_num += 1
    pdf.info_row('SMILES', smiles)
    pdf.info_row('Molecular Weight', f"{basic_props.get('Molecular Weight (g/mol)', 'N/A')} g/mol")
    pdf.info_row('Molecular Formula', basic_props.get('Molecular Formula', 'N/A'))
    pdf.ln(3)
    
    # 2. ToxScore v2
    if toxscore_data:
        pdf.section_title('TOXSCORE v2', section_num)
        section_num += 1
        
        score = toxscore_data.get('composite_score', 0)
        grade = toxscore_data.get('grade', 'N/A')
        
        pdf.set_font('Helvetica', 'B', 28)
        pdf.cell(0, 12, f'{score}/100', 0, 1, 'C')
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, f'Grade: {grade}', 0, 1, 'C')
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, toxscore_data.get('interpretation', ''), 0, 1, 'C')
        pdf.ln(3)
        
        # Sub-scores
        subs = toxscore_data.get('sub_scores', {})
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(0, 80, 120)
        pdf.cell(0, 6, 'Sub-Scores:', 0, 1, 'L')
        for name, val in subs.items():
            pdf.info_row(f"  {name.replace('_', ' ').title()}", str(val))
        pdf.ln(3)
    
    # 3. Drug-Likeness
    pdf.section_title('DRUG-LIKENESS', section_num)
    section_num += 1
    pdf.info_row('Drug-Likeness Score', f"{druglikeness_score}/100")
    pdf.info_row('Lipinski Violations', f"{lipinski_violations}/4")
    pdf.info_row('Veber Violations', f"{veber_violations}/2")
    pdf.ln(3)
    
    # 4. Organ Toxicity Summary
    if organ_results:
        pdf.section_title('ORGAN TOXICITY', section_num)
        section_num += 1
        pdf.info_row('Toxic Organs', f"{organ_results.get('toxic_hits', 0)}/6")
        pdf.info_row('Safety Score', str(organ_results.get('safety_score', 'N/A')))
        
        for organ, data in organ_results.get('models', {}).items():
            pdf.info_row(f"  {organ}", f"{data.get('prediction', 'N/A')} ({data.get('risk_level', 'N/A')})")
        pdf.ln(3)
    
    # 5. ADME Panel
    if adme_results:
        pdf.section_title('ADME PANEL', section_num)
        section_num += 1
        pdf.info_row('ADME Score', str(adme_results.get('adme_score', 'N/A')))
        
        cyp = adme_results.get('cyp450', {})
        pdf.info_row('CYP Inhibited', f"{cyp.get('total_inhibited', 0)}/3")
        
        caco = adme_results.get('permeability', {})
        pdf.info_row('Caco-2', f"{caco.get('absorption', 'N/A')} ({caco.get('logPapp', 'N/A')})")
        pdf.ln(3)
    
    # 6. PK Parameters
    if pk_results:
        pdf.section_title('PK PARAMETERS', section_num)
        section_num += 1
        pdf.info_row('PK Score', str(pk_results.get('pk_score', 'N/A')))
        
        cl = pk_results.get('excretion', {}).get('clearance', {})
        pdf.info_row('Clearance', f"{cl.get('clearance', 'N/A')} mL/min/kg")
        pdf.info_row('Half-Life', f"{cl.get('half_life', 'N/A')} hrs")
        
        ti = pk_results.get('safety', {}).get('therapeutic_index', {})
        pdf.info_row('Therapeutic Index', str(ti.get('therapeutic_index', 'N/A')))
        pdf.ln(3)
    
    # 7. Blockchain Verification
    pdf.section_title('BLOCKCHAIN VERIFICATION', section_num)
    
    if blockchain_tx:
        pdf.info_row('Transaction Hash', blockchain_tx[:40] + '...')
        pdf.info_row('Network', 'Polygon Mumbai Testnet')
        
        # Add QR code for blockchain verification
        explorer_url = f"https://mumbai.polygonscan.com/tx/{blockchain_tx}"
        pdf.add_qr_code(explorer_url, 150, pdf.get_y(), 30)
        pdf.ln(35)
        pdf.set_font('Helvetica', 'I', 7)
        pdf.cell(0, 4, 'Scan QR to verify on Polygonscan', 0, 1, 'C')
    else:
        pdf.info_row('Status', 'Not recorded on blockchain')
    
    # Save
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'generated_reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"ToxScreen_Report_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    pdf.output(filepath)
    
    return filepath
