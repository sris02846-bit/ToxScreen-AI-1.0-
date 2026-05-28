"""
ToxScreen-AI: Complete Luxury Biotech Platform (Days 1-6)
Starfield Background | Glassmorphism | Neon Effects | Cinematic Animations
Full Drug Toxicity Screening with ML, Blockchain, API, Auth, Payments
"""

import warnings
warnings.filterwarnings('ignore')
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'

# Suppress all RDKit and cheminformatics warnings
import warnings
warnings.filterwarnings('ignore')
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
import logging
logging.getLogger('rdkit').setLevel(logging.ERROR)
logging.getLogger('rdkit.Chem').setLevel(logging.ERROR)

import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Draw, Descriptors
from datetime import datetime
import sys
import os
import yaml
import io

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

# Import modules
from molecular_parser import parse_smiles, calculate_basic_properties
from lipinski_rules import evaluate_lipinski
from veber_rules import evaluate_veber
from toxicophores import evaluate_toxicophores
from fingerprint import compare_toxin_similarity
from database import (
    save_prediction, get_all_predictions, get_prediction_count,
    update_blockchain_tx, track_usage, get_daily_usage,
    get_user_tier, set_user_tier, init_database, create_api_key
)
from ml_model import predict_hepatotoxicity
from blockchain import record_on_blockchain
from batch_processor import process_csv_file, generate_batch_summary
from pdf_report import generate_single_report
from government_db import search_all_government_databases, get_cached_data
from email_reports import send_pdf_report_via_email, test_brevo_connection
from cyp450_model import predict_all_cyp, predict_cyp_inhibition
from glucuronidation_model import predict_glucuronidation
from metabolite_generator import assess_metabolic_activation_risk
from caco2_model import predict_caco2
from adme_panel import run_full_adme_panel, get_adme_summary_table
from protein_binding_model import predict_protein_binding
from volume_distribution_model import predict_volume_distribution
from clearance_model import predict_clearance_and_halflife
from therapeutic_index_model import predict_therapeutic_index
from pk_dashboard import run_full_pk_panel, get_pk_summary_table, get_radar_chart_data
from toxscore_v2 import compute_toxscore_v2, get_gauge_html, DEFAULT_WEIGHTS
from pdf_report_v2 import generate_enhanced_report
from performance_optimizer import clear_all_caches, get_performance_stats
from pipeline_validator import run_pipeline_validation, generate_test_summary
from batch_processor_v2 import process_csv_parallel, generate_batch_summary_v2
from molecule_optimizer import suggest_modifications, get_optimization_score
from fda_integration import check_approval_status
from admin_dashboard import get_dashboard_stats, get_user_activity_feed
from molecule_viewer import show_3d_molecule, create_bar_chart_html
from user_profiles import get_user_profile, get_user_stats, get_user_badges, get_saved_compounds, save_compound
from overdose_predictor import predict_overdose_risk, calculate_enhanced_therapeutic_window
from subscription import (
    check_usage_limit, get_payment_link, upgrade_user,
    get_subscription_info, PRICING, PAYMENT_LINKS, DEMO_USERS
)

# Initialize database
init_database()

# Page config
from mobile_optimizer import optimize_for_mobile
from genetic_factors import predict_polymorphism_risk, get_personalized_dosing
from drug_interactions import predict_drug_interaction, predict_synergistic_toxicity
from disease_adjustments import predict_liver_impairment_risk, predict_kidney_impairment_risk, get_age_based_recommendations

st.set_page_config(
    page_title="ToxScreen-AI | Luxury Biotech Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load auth config
with open('users_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# ============== LUXURY CINEMA-GRADE CSS ==============

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Starfield animated background */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 25%, #1b0a2e 50%, #0a1628 75%, #0a0a1a 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glassmorphism cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1rem;
    }
    
    .glass-card:hover {
        border-color: rgba(0, 255, 255, 0.3);
        box-shadow: 0 8px 42px 0 rgba(0, 255, 255, 0.1), 0 0 80px rgba(0, 255, 255, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    /* Neon text effects */
    .neon-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00ffff 0%, #ff00ff 50%, #00ffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(0, 255, 255, 0.5), 0 0 60px rgba(255, 0, 255, 0.3);
        animation: neonPulse 3s ease-in-out infinite;
        letter-spacing: 4px;
    }
    
    @keyframes neonPulse {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.3); }
    }
    
    .neon-subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1rem;
        font-weight: 300;
        color: #8899aa;
        letter-spacing: 6px;
        text-transform: uppercase;
    }
    
    /* Score circle with glow */
    .score-circle-container {
        position: relative;
        width: 120px;
        height: 120px;
        margin: 0 auto;
    }
    
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        position: relative;
        z-index: 1;
    }
    
    .score-glow {
        position: absolute;
        top: -8px;
        left: -8px;
        width: 136px;
        height: 136px;
        border-radius: 50%;
        filter: blur(15px);
        opacity: 0.3;
        z-index: 0;
        animation: glowPulse 2s ease-in-out infinite;
    }
    
    @keyframes glowPulse {
        0%, 100% { opacity: 0.2; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.1); }
    }
    
    /* Pass/Fail badges */
    .badge-pass {
        background: linear-gradient(135deg, rgba(0, 255, 100, 0.15), rgba(0, 200, 100, 0.05));
        border: 1px solid rgba(0, 255, 100, 0.3);
        color: #00ff66;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .badge-fail {
        background: linear-gradient(135deg, rgba(255, 50, 50, 0.15), rgba(200, 0, 0, 0.05));
        border: 1px solid rgba(255, 50, 50, 0.3);
        color: #ff3355;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* Neon section headers */
    .section-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #00ffff;
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
        letter-spacing: 3px;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(0, 255, 255, 0.2);
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 0.8rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(0, 255, 255, 0.2);
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.05);
    }
    
    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00ffff, #00aaff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.65rem;
        color: #667788;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }
    
    /* Custom button */
    .luxury-btn {
        background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
        border: 1px solid rgba(0, 255, 255, 0.3);
        color: #00ffff;
        padding: 0.6rem 1.5rem;
        border-radius: 30px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
    }
    
    .luxury-btn:hover {
        background: linear-gradient(135deg, rgba(0, 255, 255, 0.2), rgba(255, 0, 255, 0.2));
        border-color: rgba(0, 255, 255, 0.6);
        box-shadow: 0 0 40px rgba(0, 255, 255, 0.2), 0 0 80px rgba(255, 0, 255, 0.1);
        transform: translateY(-2px);
    }
    
    /* Tier cards */
    .tier-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    
    .tier-card:hover {
        border-color: rgba(0, 255, 255, 0.2);
        box-shadow: 0 8px 42px 0 rgba(0, 255, 255, 0.08);
        transform: translateY(-4px);
    }
    
    .tier-pro {
        border: 1px solid rgba(0, 255, 255, 0.3);
        background: rgba(0, 255, 255, 0.04);
        box-shadow: 0 0 40px rgba(0, 255, 255, 0.08);
    }
    
    .tier-enterprise {
        border: 1px solid rgba(255, 0, 255, 0.3);
        background: rgba(255, 0, 255, 0.04);
        box-shadow: 0 0 40px rgba(255, 0, 255, 0.08);
    }
    
    /* Alert styling */
    .alert-high {
        color: #ff3355;
        text-shadow: 0 0 10px rgba(255, 50, 50, 0.3);
    }
    
    .alert-medium {
        color: #ffaa00;
        text-shadow: 0 0 10px rgba(255, 170, 0, 0.3);
    }
    
    .alert-low {
        color: #00ff66;
        text-shadow: 0 0 10px rgba(0, 255, 100, 0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #667788;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        letter-spacing: 2px;
        font-size: 0.75rem;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(0, 255, 255, 0.1) !important;
        color: #00ffff !important;
        border: 1px solid rgba(0, 255, 255, 0.3) !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 26, 0.85);
        backdrop-filter: blur(30px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Input field styling */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        letter-spacing: 1px !important;
        padding: 0.7rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus {
        border-color: rgba(0, 255, 255, 0.4) !important;
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.1) !important;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 255, 255, 0.2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 255, 255, 0.4);
    }
    
    /* Radio buttons */
    .stRadio [data-baseweb="radio"] {
        margin-bottom: 0.3rem;
    }
    
    /* File uploader */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px dashed rgba(255, 255, 255, 0.15) !important;
        border-radius: 15px !important;
        padding: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ============== CORE FUNCTIONS ==============

def calculate_druglikeness_score(lipinski_v, veber_v, toxicity_s):
    """Calculate drug-likeness score with penalties."""
    penalty = (lipinski_v * 15) + (veber_v * 10) + (toxicity_s * 0.5)
    score = max(0, min(100, 100 - penalty))
    
    if score >= 80:
        interp, color, glow = "EXCELLENT", "#00ff66", "rgba(0, 255, 100, 0.4)"
    elif score >= 60:
        interp, color, glow = "GOOD", "#00ffff", "rgba(0, 255, 255, 0.4)"
    elif score >= 40:
        interp, color, glow = "MODERATE", "#ffaa00", "rgba(255, 170, 0, 0.4)"
    else:
        interp, color, glow = "POOR", "#ff3355", "rgba(255, 50, 50, 0.4)"
    
    return {"score": round(score, 1), "interpretation": interp, "color": color, "glow": glow}


def predict_page(username, tier):
    """Single molecule prediction page with luxury UI."""
    
    usage = check_usage_limit(username)
    
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <p class="section-header" style="margin-bottom:0;border-bottom:none;">MOLECULAR INPUT</p>
        <div class="glass-card" style="padding:0.5rem 1rem;margin-bottom:0;">
            <span style="font-family:Rajdhani;color:#8899aa;font-size:0.8rem;">
                TIER: <span style="color:#00ffff;font-weight:600;">{tier.upper()}</span> | 
                USED: <span style="color:#ffaa00;">{usage['used_today']}</span>/
                <span style="color:#00ffff;">{usage['daily_limit']}</span>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not usage['can_predict']:
        st.error(f"Daily limit reached ({usage['daily_limit']} predictions). Please upgrade your plan.")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            st.markdown(f'<a href="{PAYMENT_LINKS["pro"]}" target="_blank"><button class="luxury-btn">UPGRADE PRO</button></a>', unsafe_allow_html=True)
        with col_btn2:
            st.markdown(f'<a href="{PAYMENT_LINKS["enterprise"]}" target="_blank"><button class="luxury-btn" style="border-color:rgba(255,0,255,0.3);color:#ff00ff;">UPGRADE ENTERPRISE</button></a>', unsafe_allow_html=True)
        return
    
    col1, col2 = st.columns([4, 1])
    with col1:
        if 'smiles_input' not in st.session_state:
            st.session_state.smiles_input = ""
        smiles = st.text_input(
            "Enter SMILES",
            value=st.session_state.smiles_input,
            placeholder="CC(=O)OC1=CC=CC=C1C(=O)O",
            label_visibility="collapsed",
            key="smiles_main"
        )
        if smiles:
            st.session_state.smiles_input = smiles
    with col2:
        if st.button("CLEAR", width='stretch', key="clear_main"):
            st.session_state.smiles_input = ""
            st.rerun()
    
    if st.session_state.smiles_input:
        mol, error = parse_smiles(st.session_state.smiles_input)
        
        if error:
            st.error(error)
        else:
            track_usage(username)
            
            basic_props = calculate_basic_properties(mol)
            lipinski = evaluate_lipinski(mol)
            veber = evaluate_veber(mol)
            toxicophores = evaluate_toxicophores(mol)
            similarity = compare_toxin_similarity(st.session_state.smiles_input)
            dl = calculate_druglikeness_score(lipinski['violations'], veber['violations'], toxicophores['toxicity_score'])
            
            # Top row with molecule image and score
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            col_img, col_props, col_score = st.columns([1, 1, 1])
            
            with col_img:
                mol_img = Draw.MolToImage(mol, size=(320, 240), bgColor=(10, 10, 26, 0))
                st.image(mol_img, width='stretch')

                # 3D Structure toggle
                with st.expander("View 3D Structure", expanded=False):
                    try:
                        from molecule_viewer import show_3d_molecule
                        show_3d_molecule(st.session_state.smiles_input, width=350, height=300)
                    except:
                        st.info("3D viewer loading...")
                st.markdown(f"""
                <p style="font-family:Rajdhani;color:#667788;text-align:center;font-size:0.7rem;letter-spacing:1px;margin-top:0.3rem;">
                {st.session_state.smiles_input[:40]}{'...' if len(st.session_state.smiles_input) > 40 else ''}
                </p>
                """, unsafe_allow_html=True)
            
            with col_props:
                st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.8rem;letter-spacing:2px;text-align:center;">PROPERTIES</p>', unsafe_allow_html=True)
                for key in ['Molecular Weight (g/mol)', 'Molecular Formula', 'Heavy Atom Count', 'Ring Count']:
                    if key in basic_props:
                        st.markdown(f"""
                        <div class="metric-card" style="margin-bottom:0.4rem;">
                            <div class="metric-value">{basic_props[key]}</div>
                            <div class="metric-label">{key}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            with col_score:
                st.markdown(f"""
                <div style="text-align:center;margin-top:0.5rem;">
                    <p style="font-family:Orbitron;color:#00ffff;font-size:0.8rem;letter-spacing:2px;">DRUG-LIKENESS</p>
                    <div class="score-circle-container">
                        <div class="score-glow" style="background:{dl['glow']};"></div>
                        <div class="score-circle" style="background:linear-gradient(135deg,{dl['color']}22,{dl['color']}11);border:2px solid {dl['color']}44;color:{dl['color']};">
                            {dl['score']}
                            <span style="font-size:0.6rem;opacity:0.7;">/100</span>
                        </div>
                    </div>
                    <p style="font-family:Rajdhani;color:{dl['color']};font-weight:600;letter-spacing:2px;margin-top:0.5rem;font-size:0.8rem;">
                    {dl['interpretation']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Analysis Tabs
            st.markdown('<p class="section-header">DETAILED ANALYSIS</p>', unsafe_allow_html=True)
            
            t1, t2, t3, t4, t5, t6, t7 = st.tabs([
                "RULES", "TOXIC", "SIMILARITY", "ML PREDICT", "SAVE/BC", "PDF", "GOV DB"
            ])
            
            with t1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">RULE VIOLATIONS</p>', unsafe_allow_html=True)
                
                all_rules = lipinski['rules'] + veber['rules']
                for rule in all_rules:
                    badge = "badge-pass" if rule['Status'] == 'PASS' else "badge-fail"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem;
                    background:rgba(255,255,255,0.02);border-radius:8px;margin-bottom:0.3rem;">
                        <span style="font-family:Rajdhani;color:#ccddee;font-size:0.8rem;">{rule['Rule']}</span>
                        <span style="font-family:Rajdhani;color:#8899aa;font-size:0.75rem;margin:0 0.5rem;">Value: {rule['Value']}</span>
                        <span class="{badge}">{rule['Status']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <p style="font-family:Orbitron;color:#00ffff;margin-top:0.5rem;font-size:0.8rem;">
                LIPINSKI: {lipinski['violations']}/4 | VEBER: {veber['violations']}/2
                </p>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with t2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">TOXICOPHORE ALERTS</p>', unsafe_allow_html=True)
                
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{toxicophores['toxicity_score']:.1f}</div>
                        <div class="metric-label">Toxicity Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_t2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{toxicophores['total_alerts']}</div>
                        <div class="metric-label">Alerts Found</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if toxicophores['detected']:
                    st.markdown("<br>", unsafe_allow_html=True)
                    for tox in toxicophores['detected'][:8]:
                        color = {"High": "#ff3355", "Medium": "#ffaa00", "Low": "#00ff66"}
                        st.markdown(f"""
                        <div style="padding:0.4rem;border-left:3px solid {color.get(tox['Risk Level'], '#8899aa')};
                        background:rgba(255,255,255,0.02);border-radius:5px;margin-bottom:0.2rem;">
                            <span style="font-family:Rajdhani;color:{color.get(tox['Risk Level'])};font-weight:600;font-size:0.8rem;">
                            {tox['Toxicophore']}
                            </span>
                            <span style="color:#667788;font-size:0.7rem;float:right;">
                            {tox['Risk Level']} Risk | {tox['Match Count']} matches
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("No toxicophore alerts detected")
                
                st.markdown(f"""
                <p style="font-family:Orbitron;color:#00ffff;margin-top:0.5rem;font-size:0.8rem;">
                RISK LEVEL: {toxicophores['risk_level']}
                </p>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with t3:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">TOXIN SIMILARITY</p>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align:center;padding:1rem;">
                    <p style="font-family:Rajdhani;color:#8899aa;font-size:0.8rem;">Most Similar Known Toxin</p>
                    <p style="font-size:1.3rem;color:#ccddee;font-weight:600;">{similarity.get('most_similar', 'None')}</p>
                    <p style="font-family:Orbitron;font-size:2rem;color:#ffaa00;margin:0.5rem 0;">{similarity.get('similarity', 0):.3f}</p>
                    <p style="font-family:Rajdhani;color:#667788;font-size:0.75rem;">Tanimoto Similarity</p>
                    <p style="color:#8899aa;font-size:0.75rem;margin-top:0.5rem;">{similarity.get('interpretation', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if similarity.get('all_similarities'):
                    st.markdown('<p style="color:#00ffff;font-size:0.8rem;">Top Similar Toxins:</p>', unsafe_allow_html=True)
                    for s in similarity['all_similarities']:
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;padding:0.3rem;
                        background:rgba(255,255,255,0.02);border-radius:5px;margin-bottom:0.2rem;">
                            <span style="font-family:Rajdhani;color:#ccddee;font-size:0.8rem;">{s['name']}</span>
                            <span style="font-family:Orbitron;color:#8899aa;font-size:0.7rem;">{s['similarity']:.3f}</span>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with t4:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;text-align:center;">ML HEPATOTOXICITY</p>', unsafe_allow_html=True)
                
                if st.button("RUN ML PREDICTION", width='stretch', key="ml_btn"):
                    with st.spinner("Running RandomForest model..."):
                        ml_result = predict_hepatotoxicity(st.session_state.smiles_input)
                        st.session_state.ml_result = ml_result
                        
                        if 'error' not in ml_result:
                            pred_color = "#ff3355" if ml_result['prediction'] == 'Hepatotoxic' else "#00ff66"
                            st.markdown(f"""
                            <div style="text-align:center;margin-top:1rem;">
                                <p style="font-family:Orbitron;font-size:1.3rem;color:{pred_color};letter-spacing:2px;">
                                {ml_result['prediction']}
                                </p>
                                <p style="font-family:Rajdhani;color:#8899aa;">Confidence: <b>{ml_result['confidence']}%</b></p>
                                <div style="display:flex;justify-content:center;gap:1rem;margin-top:0.5rem;">
                                    <span style="color:#ff3355;">Toxic: {ml_result['probability_hepatotoxic']}%</span>
                                    <span style="color:#00ff66;">Safe: {ml_result['probability_safe']}%</span>
                                </div>
                                <p style="color:#ffaa00;margin-top:0.5rem;">Risk Level: {ml_result['risk_level']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with t5:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;text-align:center;">SAVE & RECORD</p>', unsafe_allow_html=True)
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    if st.button("SAVE TO DATABASE", width='stretch', key="save_db"):
                        pred_data = {
                            'user': username,
                            'smiles': st.session_state.smiles_input,
                            'druglikeness_score': dl['score'],
                            'lipinski_violations': lipinski['violations'],
                            'veber_violations': veber['violations'],
                            'toxicity_score': toxicophores['toxicity_score'],
                            'risk_level': toxicophores['risk_level'],
                            'result': dl['interpretation'],
                            'ml_prediction': st.session_state.get('ml_result', {}).get('prediction', ''),
                            'ml_confidence': st.session_state.get('ml_result', {}).get('confidence', 0),
                            'most_similar_toxin': similarity.get('most_similar', ''),
                            'toxin_similarity': similarity.get('similarity', 0)
                        }
                        record_id = save_prediction(pred_data)
                        st.session_state.record_id = record_id
                        st.success(f"Saved! Record ID: {record_id}")
                
                with col_s2:
                    if st.button("RECORD ON BLOCKCHAIN", width='stretch', key="blockchain_btn"):
                        tx = record_on_blockchain(st.session_state.smiles_input, dl['score'], toxicophores['risk_level'])
                        if tx['success']:
                            st.session_state.tx_hash = tx['transaction_hash']
                            if 'record_id' in st.session_state:
                                update_blockchain_tx(st.session_state.record_id, tx['transaction_hash'])
                            st.success("Recorded on Polygon Mumbai!")
                            st.code(f"TX: {tx['transaction_hash'][:30]}...")
                            st.markdown(f"[View on PolygonScan]({tx['explorer_url']})")
                        else:
                            st.error(tx.get('error', 'Transaction failed'))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with t6:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;text-align:center;">PDF REPORT & EMAIL</p>', unsafe_allow_html=True)
                
                if st.button("GENERATE PDF REPORT", width='stretch', key="pdf_btn"):
                    results = {
                        'Molecular_Weight': basic_props.get('Molecular Weight (g/mol)', 'N/A'),
                        'Molecular_Formula': basic_props.get('Molecular Formula', 'N/A'),
                        'Lipinski_Violations': lipinski['violations'],
                        'Veber_Violations': veber['violations'],
                        'Toxicity_Score': toxicophores['toxicity_score'],
                        'Risk_Level': toxicophores['risk_level'],
                        'DrugLikeness_Score': dl['score'],
                        'Result': dl['interpretation'],
                        'Most_Similar_Toxin': similarity.get('most_similar', 'None'),
                        'Toxin_Similarity': similarity.get('similarity', 0),
                        'Toxicophore_Count': toxicophores['total_alerts']
                    }
                    tx_hash = st.session_state.get('tx_hash', None)
                    pdf_path = generate_enhanced_report(
                        smiles=st.session_state.smiles_input,
                        basic_props=basic_props,
                        lipinski_violations=lipinski['violations'],
                        veber_violations=veber['violations'],
                        druglikeness_score=dl['score'],
                        toxscore_data=st.session_state.get('toxscore'),
                        organ_results=st.session_state.get('all_tox_results'),
                        adme_results=st.session_state.get('adme_results'),
                        pk_results=st.session_state.get('pk_dash_results'),
                        blockchain_tx=tx_hash,
                        toxicophore_count=toxicophores['total_alerts']
                    )
                    st.session_state.pdf_path = pdf_path
                    with open(pdf_path, 'rb') as f:
                        st.download_button("DOWNLOAD PDF", f, file_name=os.path.basename(pdf_path), 
                                         mime="application/pdf", width='stretch')
                    st.success("PDF generated successfully!")
                
                if 'pdf_path' in st.session_state:
                    st.markdown("---")
                    st.markdown('<p style="font-family:Orbitron;color:#ff00ff;font-size:0.8rem;letter-spacing:2px;text-align:center;">EMAIL PDF REPORT</p>', unsafe_allow_html=True)
                    
                    col_em1, col_em2 = st.columns(2)
                    with col_em1:
                        recipient_email = st.text_input("Recipient Email", value="sris02846@gmail.com", key="email_to")
                    with col_em2:
                        recipient_name = st.text_input("Recipient Name", value="User", key="email_name")
                    
                    if st.button("SEND PDF VIA EMAIL", width='stretch', key="send_email_btn"):
                        with st.spinner("Sending email via Brevo..."):
                            email_result = send_pdf_report_via_email(
                                recipient_email=recipient_email,
                                recipient_name=recipient_name,
                                pdf_path=st.session_state.pdf_path,
                                compound_name=st.session_state.smiles_input[:30],
                                druglikeness_score=dl['score'],
                                smiles=st.session_state.smiles_input,
                                risk_level=toxicophores['risk_level']
                            )
                            
                            if email_result['success']:
                                st.success(f"Email sent to {recipient_email}!")
                                st.info(f"Message ID: {email_result.get('message_id', 'N/A')}")
                            else:
                                st.error(f"Failed: {email_result['message']}")
                st.markdown('</div>', unsafe_allow_html=True)

            
            with t7:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;text-align:center;">GOVERNMENT DATABASE</p>', unsafe_allow_html=True)
                
                if st.button("CHECK OFFICIAL DATABASES", width='stretch', key="gov_check"):
                    with st.spinner("Querying PubChem and government databases..."):
                        gov_data = search_all_government_databases(st.session_state.smiles_input)
                        st.session_state.gov_data = gov_data
                
                if 'gov_data' in st.session_state:
                    gov = st.session_state.gov_data
                    
                    st.markdown(f'<p style="color:#8899aa;text-align:center;">{gov["summary"]}</p>', unsafe_allow_html=True)
                    
                    pubchem = gov.get("pubchem_data", {})
                    if pubchem and pubchem.get("found"):
                        st.markdown('<p style="color:#00ff66;font-weight:600;">FOUND IN PUBCHEM</p>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f'<div class="metric-card" style="margin-bottom:0.4rem;"><div class="metric-value" style="font-size:0.8rem;">{pubchem.get("iupac_name", "N/A")}</div><div class="metric-label">IUPAC Name</div></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-card" style="margin-bottom:0.4rem;"><div class="metric-value">{pubchem.get("molecular_formula", "N/A")}</div><div class="metric-label">Official Formula</div></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-card" style="margin-bottom:0.4rem;"><div class="metric-value">{pubchem.get("molecular_weight", "N/A")}</div><div class="metric-label">Official MW (g/mol)</div></div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f'<div class="metric-card" style="margin-bottom:0.4rem;"><div class="metric-value">{pubchem.get("xlogp", "N/A")}</div><div class="metric-label">XLogP</div></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-card" style="margin-bottom:0.4rem;"><div class="metric-value">{pubchem.get("tpsa", "N/A")}</div><div class="metric-label">TPSA (Official)</div></div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-card" style="margin-bottom:0.4rem;"><div class="metric-value">{pubchem.get("cid", "N/A")}</div><div class="metric-label">PubChem CID</div></div>', unsafe_allow_html=True)
                        
                        st.markdown(f'<a href="{pubchem.get("pubchem_url", "#")}" target="_blank"><button class="luxury-btn">VIEW ON PUBCHEM</button></a>', unsafe_allow_html=True)
                        
                        toxicity = gov.get("toxicity_data", {})
                        if toxicity and toxicity.get("toxicity_alerts"):
                            st.markdown('<p style="color:#ffaa00;margin-top:1rem;">TOXICITY ASSAYS FOUND:</p>', unsafe_allow_html=True)
                            for alert in toxicity["toxicity_alerts"][:5]:
                                st.markdown(f'<div style="padding:0.3rem;background:rgba(255,170,0,0.1);border-radius:5px;margin-bottom:0.2rem;"><span style="color:#ffaa00;font-size:0.75rem;">{alert["assay"][:80]}</span><span style="color:#8899aa;font-size:0.7rem;"> - {alert["result"]}</span></div>', unsafe_allow_html=True)
                    else:
                        st.info("Compound not found in PubChem database. It may be a novel or unregistered compound.")
                
                st.markdown('</div>', unsafe_allow_html=True)
            

            
            # ToxScore v2 Section
            st.markdown("---")
            st.markdown('<p style="font-family:Orbitron;color:#ff00ff;font-size:1rem;letter-spacing:2px;text-align:center;">TOXSCORE v2</p>', unsafe_allow_html=True)

            if st.button("CALCULATE TOXSCORE v2", width='stretch', type="primary", key="toxscore_btn"):
                with st.spinner("Computing composite ToxScore..."):
                    toxscore = compute_toxscore_v2(
                        lipinski_violations=lipinski['violations'],
                        veber_violations=veber['violations'],
                        toxicophore_score=toxicophores['toxicity_score'],
                        organ_results=st.session_state.get('all_tox_results'),
                        adme_results=st.session_state.get('adme_results'),
                        metabolic_results=st.session_state.get('met_result'),
                        pk_results=st.session_state.get('pk_dash_results')
                    )
                    st.session_state.toxscore = toxscore

            if 'toxscore' in st.session_state:
                ts = st.session_state.toxscore

                st.markdown(get_gauge_html(ts['composite_score'], ts['grade_color']), unsafe_allow_html=True)

                st.markdown(f'<div style="text-align:center;"><p style="font-family:Orbitron;font-size:2rem;color:{ts["grade_color"]};">GRADE {ts["grade"]}</p><p style="color:#8899aa;">{ts["interpretation"]}</p></div>', unsafe_allow_html=True)

                cols = st.columns(5)
                sub_names = ['tier1_rules', 'organ_toxicity', 'adme_panel', 'metabolic_risk', 'pk_parameters']
                sub_labels = ['Rules', 'Organs', 'ADME', 'Metab', 'PK']

                for col, name, label in zip(cols, sub_names, sub_labels):
                    val = ts['sub_scores'].get(name, 0)
                    color = "#00ff66" if val >= 80 else "#ffaa00" if val >= 50 else "#ff3355"
                    with col:
                        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color};">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)


            
def batch_page(username, tier):
    """Batch processing page with luxury styling."""
    
    st.markdown('<p class="section-header">BATCH PROCESSING</p>', unsafe_allow_html=True)
    
    usage = check_usage_limit(username)
    
    if not usage['can_batch']:
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        st.error("Batch processing requires Pro or Enterprise subscription.")
        st.markdown(f"""
        <a href="{PAYMENT_LINKS['pro']}" target="_blank">
            <button class="luxury-btn" style="width:auto;margin:0.5rem;">UPGRADE TO PRO - Rs 499</button>
        </a>
        <a href="{PAYMENT_LINKS['enterprise']}" target="_blank">
            <button class="luxury-btn" style="width:auto;margin:0.5rem;border-color:rgba(255,0,255,0.3);color:#ff00ff;">
            UPGRADE TO ENTERPRISE - Rs 1,999</button>
        </a>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">UPLOAD CSV FILE</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#8899aa;font-size:0.8rem;">CSV must contain a SMILES column</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], label_visibility="collapsed")
    
    if uploaded_file:
        try:
            content = uploaded_file.read().decode('utf-8')
            results_df, valid, invalid = process_csv_file(content)
            summary = generate_batch_summary(results_df)
            
            st.success(f"Processed {summary['total']} compounds: {summary['valid']} valid, {summary['invalid']} invalid")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{summary['avg_score']}</div>
                    <div class="metric-label">Average Score</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="background:linear-gradient(135deg,#00ff66,#00ff66);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{summary['excellent']}</div>
                    <div class="metric-label">Excellent</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="background:linear-gradient(135deg,#ffaa00,#ffaa00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{summary['moderate']}</div>
                    <div class="metric-label">Moderate</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="background:linear-gradient(135deg,#ff3355,#ff3355);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{summary['poor']}</div>
                    <div class="metric-label">Poor</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.dataframe(results_df, width='stretch', hide_index=True)
            
            csv = results_df.to_csv(index=False)
            st.download_button("DOWNLOAD RESULTS CSV", csv, "toxscreen_batch_results.csv", 
                             "text/csv", width='stretch')
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def history_page(username):
    """Prediction history page."""
    st.markdown('<p class="section-header">PREDICTION HISTORY</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    df = get_all_predictions(username=username)
    
    if len(df) > 0:
        display_cols = ['id', 'smiles', 'druglikeness_score', 'risk_level', 'result', 'date']
        st.dataframe(df[display_cols], width='stretch', hide_index=True)
        
        csv = df.to_csv(index=False)
        st.download_button("DOWNLOAD HISTORY CSV", csv, "toxscreen_history.csv", 
                         "text/csv", width='stretch')
    else:
        st.info("No predictions saved yet. Start analyzing molecules!")
    st.markdown('</div>', unsafe_allow_html=True)


def subscription_page(username, tier):
    """Subscription plans page with luxury tier cards."""
    
    st.markdown('<p class="section-header">SUBSCRIPTION PLANS</p>', unsafe_allow_html=True)
    
    current_info = get_subscription_info(username)
    
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;margin-bottom:2rem;">
        <p style="font-family:Rajdhani;color:#8899aa;">Current Plan: 
        <span style="color:#00ffff;font-weight:700;font-size:1.2rem;">{tier.upper()}</span></p>
        <p style="color:#667788;font-size:0.8rem;">
        Used Today: {current_info['used_today']}/{current_info['daily_limit']} predictions
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="tier-card">', unsafe_allow_html=True)
        st.markdown('<p style="font-family:Orbitron;font-size:1.5rem;color:#8899aa;">FREE</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-family:Orbitron;font-size:2rem;color:#ccddee;">FREE</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color:#8899aa;font-family:Rajdhani;font-size:0.9rem;line-height:2;">
        <p>5 predictions/day</p>
        <p>Basic analysis</p>
        <p>SQLite storage</p>
        <p>API: 100 calls/day</p>
        <p style="color:#667788;">No batch processing</p>
        </div>
        """, unsafe_allow_html=True)
        if tier == 'free':
            st.markdown('<p style="color:#00ff66;font-weight:600;">ACTIVE PLAN</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="tier-card tier-pro">', unsafe_allow_html=True)
        st.markdown('<p style="font-family:Orbitron;font-size:1.5rem;color:#00ffff;">PRO</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-family:Orbitron;font-size:2rem;color:#00ffff;">Rs 499</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color:#8899aa;font-family:Rajdhani;font-size:0.9rem;line-height:2;">
        <p>100 predictions/day</p>
        <p>Batch processing</p>
        <p>ML predictions</p>
        <p>PDF reports</p>
        <p>API: 1000 calls/day</p>
        <p>Blockchain recording</p>
        </div>
        """, unsafe_allow_html=True)
        if tier == 'pro':
            st.markdown('<p style="color:#00ffff;font-weight:600;">ACTIVE PLAN</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<a href="{PAYMENT_LINKS["pro"]}" target="_blank"><button class="luxury-btn">UPGRADE - Rs 499</button></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="tier-card tier-enterprise">', unsafe_allow_html=True)
        st.markdown('<p style="font-family:Orbitron;font-size:1.5rem;color:#ff00ff;">ENTERPRISE</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-family:Orbitron;font-size:2rem;color:#ff00ff;">Rs 1,999</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color:#8899aa;font-family:Rajdhani;font-size:0.9rem;line-height:2;">
        <p>Unlimited predictions</p>
        <p>Batch processing</p>
        <p>ML predictions</p>
        <p>PDF reports</p>
        <p>Unlimited API</p>
        <p>Blockchain recording</p>
        <p>Priority support</p>
        </div>
        """, unsafe_allow_html=True)
        if tier == 'enterprise':
            st.markdown('<p style="color:#ff00ff;font-weight:600;">ACTIVE PLAN</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<a href="{PAYMENT_LINKS["enterprise"]}" target="_blank"><button class="luxury-btn" style="border-color:rgba(255,0,255,0.3);color:#ff00ff;">UPGRADE - Rs 1,999</button></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Demo credentials
    st.markdown("---")
    st.markdown("""
    <div class="glass-card" style="text-align:center;">
        <p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">DEMO CREDENTIALS</p>
        <table style="width:100%;color:#8899aa;font-family:Rajdhani;font-size:0.9rem;">
            <tr><td style="padding:0.3rem;">Free:</td><td style="color:#00ff66;">demo / demo123</td></tr>
            <tr><td style="padding:0.3rem;">Pro:</td><td style="color:#00ffff;">devil / devil@123ch</td></tr>
            <tr><td style="padding:0.3rem;">Enterprise:</td><td style="color:#ff00ff;">monkey / monkey@123ch</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)


def api_page(username, tier):
    """API documentation page."""
    
    st.markdown('<p class="section-header">API ACCESS</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">EMAIL CONFIGURATION</p>', unsafe_allow_html=True)
    
    if st.button("TEST BREVO CONNECTION", width='stretch'):
        result = test_brevo_connection()
        if result['success']:
            st.success(f"Connected! Email: {result.get('email', 'N/A')}")
            st.info(f"Plan: {result.get('plan', 'N/A')} | Credits: {result.get('credits', 'N/A')}")
        else:
            st.error(f"Failed: {result['message']}")
    
    st.markdown("---")
    st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">YOUR API KEY</p>', unsafe_allow_html=True)
    
    if st.button("GENERATE API KEY", width='stretch'):
        api_key = create_api_key(username, tier)
        st.session_state.api_key = api_key
        st.success("API Key generated!")
    
    if 'api_key' in st.session_state:
        st.code(st.session_state.api_key, language="text")
        st.caption("Save this key securely. It will not be shown again.")
    
    st.markdown("---")
    st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">ENDPOINTS</p>', unsafe_allow_html=True)
    
    st.code("""
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"}'

# Batch prediction (Pro/Enterprise)
curl -X POST http://localhost:8000/batch \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"smiles_list": ["CCO", "c1ccccc1"]}'

# Usage stats
curl http://localhost:8000/usage \\
  -H "X-API-Key: YOUR_API_KEY"
    """, language="bash")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============== MAIN APPLICATION ==============
def adme_page(username, tier):
    """ADME Panel page - Metabolism and Pharmacokinetics."""
    
    st.markdown('<p class="section-header">ADME PANEL</p>', unsafe_allow_html=True)
    
    if 'smiles_input' not in st.session_state or not st.session_state.smiles_input:
        st.info("Enter a SMILES string in the Predict page first, then come here for ADME analysis.")
        return
    
    smiles = st.session_state.smiles_input
    st.markdown(f'<p style="color:#8899aa;">Analyzing: <b>{smiles[:40]}</b></p>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    adme_tab1, adme_tab2, adme_tab3, adme_tab4, adme_tab5 = st.tabs([
        "CYP450", "Phase II", "Permeability", "Metabolic Activation", "Full Panel"
    ])
    
    with adme_tab1:
        st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">CYP450 INHIBITION RISK</p>', unsafe_allow_html=True)
        
        if st.button("RUN CYP450 PANEL", width='stretch', key="cyp_btn"):
            with st.spinner("Predicting CYP450 inhibition..."):
                cyp_results = predict_all_cyp(smiles)
                st.session_state.cyp_results = cyp_results
        
        if 'cyp_results' in st.session_state:
            cyp = st.session_state.cyp_results
            
            col1, col2, col3 = st.columns(3)
            isoforms = ['CYP2C9', 'CYP2D6', 'CYP3A4']
            
            for col, iso in zip([col1, col2, col3], isoforms):
                data = cyp['isoforms'].get(iso, {})
                is_inhibitor = data.get('prediction') == 'Inhibitor'
                color = "#ff3355" if is_inhibitor else "#00ff66"
                
                with col:
                    st.markdown(f'<div class="metric-card"><p style="font-family:Orbitron;color:#00ffff;font-size:0.8rem;">{iso}</p><p style="font-size:1.1rem;color:{color};">{data.get("prediction", "N/A")}</p><p style="color:#8899aa;font-size:0.7rem;">Confidence: {data.get("confidence", 0)}%</p></div>', unsafe_allow_html=True)
            
            st.markdown(f'<p style="text-align:center;color:#ffaa00;margin-top:0.5rem;">Inhibited: {cyp["total_inhibited"]}/3 | {cyp["overall_risk"]}</p>', unsafe_allow_html=True)
    
    with adme_tab2:
        st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">PHASE II METABOLISM</p>', unsafe_allow_html=True)
        
        if st.button("RUN GLUCURONIDATION PREDICTION", width='stretch', key="gluc_btn"):
            with st.spinner("Predicting glucuronidation..."):
                gluc_result = predict_glucuronidation(smiles)
                st.session_state.gluc_result = gluc_result
        
        if 'gluc_result' in st.session_state:
            g = st.session_state.gluc_result
            color = "#00ff66" if g.get('prediction') == 'Glucuronidated' else "#ffaa00"
            st.markdown(f'<div style="text-align:center;"><p style="font-size:1.3rem;color:{color};">{g.get("prediction", "N/A")}</p><p style="color:#8899aa;">Confidence: {g.get("confidence", 0)}%</p><p style="color:#667788;">{g.get("interpretation", "")}</p></div>', unsafe_allow_html=True)
    
    with adme_tab3:
        st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">CACO-2 PERMEABILITY</p>', unsafe_allow_html=True)
        
        if st.button("RUN PERMEABILITY PREDICTION", width='stretch', key="caco_btn"):
            with st.spinner("Predicting Caco-2 permeability..."):
                caco_result = predict_caco2(smiles)
                st.session_state.caco_result = caco_result
        
        if 'caco_result' in st.session_state:
            c = st.session_state.caco_result
            st.markdown(f'<div style="text-align:center;"><p style="font-size:2rem;color:#00ffff;">{c.get("logPapp", "N/A")}</p><p style="color:#8899aa;">logPapp (cm/s)</p><p style="font-size:1.2rem;color:#00ff66;">{c.get("absorption", "N/A")} Absorption</p><p style="color:#667788;">{c.get("interpretation", "")}</p></div>', unsafe_allow_html=True)
    
    with adme_tab4:
        st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">METABOLIC ACTIVATION RISK</p>', unsafe_allow_html=True)
        
        if st.button("ASSESS METABOLIC ACTIVATION", width='stretch', key="metab_btn"):
            with st.spinner("Generating metabolites and screening for reactive species..."):
                met_result = assess_metabolic_activation_risk(smiles)
                st.session_state.met_result = met_result
        
        if 'met_result' in st.session_state:
            m = st.session_state.met_result
            risk_color = {"High": "#ff3355", "Medium": "#ffaa00", "Low": "#00ff66"}.get(m.get('metabolic_activation_risk', 'Low'), '#8899aa')
            
            st.markdown(f'<div style="text-align:center;"><p style="font-size:1.5rem;color:{risk_color};">{m.get("metabolic_activation_risk", "N/A")} Risk</p><p style="color:#8899aa;">Metabolites Generated: {m.get("metabolites_generated", 0)}</p><p style="color:#ff3355;">Reactive Metabolites: {m.get("reactive_metabolites", 0)}</p><p style="color:#ffaa00;">{m.get("warning", "")}</p></div>', unsafe_allow_html=True)
            
            if m.get('reactive_species'):
                st.markdown('<p style="color:#ff3355;margin-top:1rem;">Reactive Species Detected:</p>', unsafe_allow_html=True)
                for species in m['reactive_species'][:5]:
                    st.markdown(f'<div style="padding:0.3rem;background:rgba(255,50,50,0.1);border-radius:5px;margin-bottom:0.2rem;"><span style="color:#ff3355;font-size:0.75rem;">{species["alert"]}</span><span style="color:#8899aa;font-size:0.7rem;"> - {species["risk"]}</span></div>', unsafe_allow_html=True)
    
    with adme_tab5:
        st.markdown('<p style="font-family:Orbitron;color:#ff00ff;font-size:0.9rem;letter-spacing:2px;text-align:center;">FULL ADME PANEL</p>', unsafe_allow_html=True)
        
        if st.button("RUN COMPLETE ADME PANEL", width='stretch', key="full_adme_btn", type="primary"):
            with st.spinner("Running full ADME panel..."):
                adme_results = run_full_adme_panel(smiles)
                st.session_state.adme_results = adme_results
        
        if 'adme_results' in st.session_state:
            ar = st.session_state.adme_results
            score_color = "#00ff66" if ar['adme_score'] >= 70 else "#ffaa00" if ar['adme_score'] >= 40 else "#ff3355"
            
            st.markdown(f'<div style="text-align:center;"><div style="width:100px;height:100px;border-radius:50%;background:{score_color}22;border:3px solid {score_color}44;display:flex;align-items:center;justify-content:center;margin:0 auto;font-family:Orbitron;font-size:1.5rem;font-weight:900;color:{score_color};">{ar["adme_score"]}</div><p style="color:#8899aa;margin-top:0.5rem;">ADME Score</p></div>', unsafe_allow_html=True)
            
            summary = get_adme_summary_table(ar)
            summary_df = pd.DataFrame(summary)
            st.dataframe(summary_df, width='stretch', hide_index=True)
            
            if ar.get('flags'):
                st.markdown('<p style="color:#ff3355;margin-top:1rem;">Warnings:</p>', unsafe_allow_html=True)
                for flag in ar['flags']:
                    st.warning(flag)
    
    st.markdown('</div>', unsafe_allow_html=True)

def adme_page(username, tier):
    """ADME Panel page - Metabolism and Pharmacokinetics."""
    
    st.markdown('<p class="section-header">ADME PANEL</p>', unsafe_allow_html=True)
    
    if 'smiles_input' not in st.session_state or not st.session_state.smiles_input:
        st.info("Enter a SMILES string in the Predict page first, then come here for ADME analysis.")
        return
    
    smiles = st.session_state.smiles_input
    st.markdown(f'<p style="color:#8899aa;">Analyzing: <b>{smiles[:40]}</b></p>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    adme_tab1, adme_tab2, adme_tab3, adme_tab4, adme_tab5 = st.tabs([
        "CYP450", "Phase II", "Permeability", "Metabolic Activation", "Full Panel"
    ])
    
    with adme_tab1:
        st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">CYP450 INHIBITION RISK</p>', unsafe_allow_html=True)
        
        if st.button("RUN CYP450 PANEL", width='stretch', key="cyp_btn"):
            with st.spinner("Predicting CYP450 inhibition..."):
                cyp_results = predict_all_cyp(smiles)
                st.session_state.cyp_results = cyp_results
        
        if 'cyp_results' in st.session_state:
            cyp = st.session_state.cyp_results
            
            col1, col2, col3 = st.columns(3)
            isoforms = ['CYP2C9', 'CYP2D6', 'CYP3A4']
            
            for col, iso in zip([col1, col2, col3], isoforms):
                data = cyp['isoforms'].get(iso, {})
                is_inhibitor = data.get('prediction') == 'Inhibitor'
                color = "#ff3355" if is_inhibitor else "#00ff66"
                
                with col:
                    st.markdown(f'<div class="metric-card"><p style="font-family:Orbitron;color:#00ffff;font-size:0.8rem;">{iso}</p><p style="font-size:1.1rem;color:{color};">{data.get("prediction", "N/A")}</p><p style="color:#8899aa;font-size:0.7rem;">Confidence: {data.get("confidence", 0)}%</p></div>', unsafe_allow_html=True)
            
            st.markdown(f'<p style="text-align:center;color:#ffaa00;margin-top:0.5rem;">Inhibited: {cyp["total_inhibited"]}/3 | {cyp["overall_risk"]}</p>', unsafe_allow_html=True)
    
    with adme_tab2:
        st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">PHASE II METABOLISM</p>', unsafe_allow_html=True)
        
        if st.button("RUN GLUCURONIDATION PREDICTION", width='stretch', key="gluc_btn"):
            with st.spinner("Predicting glucuronidation..."):
                gluc_result = predict_glucuronidation(smiles)
                st.session_state.gluc_result = gluc_result
        
        if 'gluc_result' in st.session_state:
            g = st.session_state.gluc_result
            color = "#00ff66" if g.get('prediction') == 'Glucuronidated' else "#ffaa00"
            st.markdown(f'<div style="text-align:center;"><p style="font-size:1.3rem;color:{color};">{g.get("prediction", "N/A")}</p><p style="color:#8899aa;">Confidence: {g.get("confidence", 0)}%</p><p style="color:#667788;">{g.get("interpretation", "")}</p></div>', unsafe_allow_html=True)
    
    with adme_tab3:
        st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">CACO-2 PERMEABILITY</p>', unsafe_allow_html=True)
        
        if st.button("RUN PERMEABILITY PREDICTION", width='stretch', key="caco_btn"):
            with st.spinner("Predicting Caco-2 permeability..."):
                caco_result = predict_caco2(smiles)
                st.session_state.caco_result = caco_result
        
        if 'caco_result' in st.session_state:
            c = st.session_state.caco_result
            st.markdown(f'<div style="text-align:center;"><p style="font-size:2rem;color:#00ffff;">{c.get("logPapp", "N/A")}</p><p style="color:#8899aa;">logPapp (cm/s)</p><p style="font-size:1.2rem;color:#00ff66;">{c.get("absorption", "N/A")} Absorption</p><p style="color:#667788;">{c.get("interpretation", "")}</p></div>', unsafe_allow_html=True)
    
    with adme_tab4:
        st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.9rem;letter-spacing:2px;">METABOLIC ACTIVATION RISK</p>', unsafe_allow_html=True)
        
        if st.button("ASSESS METABOLIC ACTIVATION", width='stretch', key="metab_btn"):
            with st.spinner("Generating metabolites and screening for reactive species..."):
                met_result = assess_metabolic_activation_risk(smiles)
                st.session_state.met_result = met_result
        
        if 'met_result' in st.session_state:
            m = st.session_state.met_result
            risk_color = {"High": "#ff3355", "Medium": "#ffaa00", "Low": "#00ff66"}.get(m.get('metabolic_activation_risk', 'Low'), '#8899aa')
            
            st.markdown(f'<div style="text-align:center;"><p style="font-size:1.5rem;color:{risk_color};">{m.get("metabolic_activation_risk", "N/A")} Risk</p><p style="color:#8899aa;">Metabolites Generated: {m.get("metabolites_generated", 0)}</p><p style="color:#ff3355;">Reactive Metabolites: {m.get("reactive_metabolites", 0)}</p><p style="color:#ffaa00;">{m.get("warning", "")}</p></div>', unsafe_allow_html=True)
            
            if m.get('reactive_species'):
                st.markdown('<p style="color:#ff3355;margin-top:1rem;">Reactive Species Detected:</p>', unsafe_allow_html=True)
                for species in m['reactive_species'][:5]:
                    st.markdown(f'<div style="padding:0.3rem;background:rgba(255,50,50,0.1);border-radius:5px;margin-bottom:0.2rem;"><span style="color:#ff3355;font-size:0.75rem;">{species["alert"]}</span><span style="color:#8899aa;font-size:0.7rem;"> - {species["risk"]}</span></div>', unsafe_allow_html=True)
    
    with adme_tab5:
        st.markdown('<p style="font-family:Orbitron;color:#ff00ff;font-size:0.9rem;letter-spacing:2px;text-align:center;">FULL ADME PANEL</p>', unsafe_allow_html=True)
        
        if st.button("RUN COMPLETE ADME PANEL", width='stretch', key="full_adme_btn", type="primary"):
            with st.spinner("Running full ADME panel..."):
                adme_results = run_full_adme_panel(smiles)
                st.session_state.adme_results = adme_results
        
        if 'adme_results' in st.session_state:
            ar = st.session_state.adme_results
            score_color = "#00ff66" if ar['adme_score'] >= 70 else "#ffaa00" if ar['adme_score'] >= 40 else "#ff3355"
            
            st.markdown(f'<div style="text-align:center;"><div style="width:100px;height:100px;border-radius:50%;background:{score_color}22;border:3px solid {score_color}44;display:flex;align-items:center;justify-content:center;margin:0 auto;font-family:Orbitron;font-size:1.5rem;font-weight:900;color:{score_color};">{ar["adme_score"]}</div><p style="color:#8899aa;margin-top:0.5rem;">ADME Score</p></div>', unsafe_allow_html=True)
            
            summary = get_adme_summary_table(ar)
            summary_df = pd.DataFrame(summary)
            st.dataframe(summary_df, width='stretch', hide_index=True)
            
            if ar.get('flags'):
                st.markdown('<p style="color:#ff3355;margin-top:1rem;">Warnings:</p>', unsafe_allow_html=True)
                for flag in ar['flags']:
                    st.warning(flag)
    
    st.markdown('</div>', unsafe_allow_html=True)

def pk_dashboard_page(username, tier):
    """Full Pharmacokinetics Dashboard with all ADME/PK outputs."""
    
    st.markdown('<p class="section-header">PHARMACOKINETICS DASHBOARD</p>', unsafe_allow_html=True)
    
    if 'smiles_input' not in st.session_state or not st.session_state.smiles_input:
        st.info("Enter a SMILES string in the Predict page first, then come here.")
        return
    
    smiles = st.session_state.smiles_input
    st.markdown(f'<p style="color:#8899aa;">Compound: <b>{smiles[:50]}</b></p>', unsafe_allow_html=True)
    
    # Single button to run all PK tests
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if st.button("RUN FULL PK ANALYSIS", width='stretch', type="primary", key="run_pk_all"):
        with st.spinner("Running all PK/ADME models..."):
            try:
                pk_results = run_full_pk_panel(smiles)
                st.session_state.pk_dash_results = pk_results
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if 'pk_dash_results' in st.session_state:
        pr = st.session_state.pk_dash_results
        
        # PK Score
        score = pr.get('pk_score', 0)
        score_color = "#00ff66" if score >= 70 else "#ffaa00" if score >= 40 else "#ff3355"
        st.markdown(f'<div style="text-align:center;margin:1rem 0;"><div style="width:100px;height:100px;border-radius:50%;background:{score_color}22;border:3px solid {score_color}44;display:flex;align-items:center;justify-content:center;margin:0 auto;font-family:Orbitron;font-size:1.5rem;font-weight:900;color:{score_color};">{score}</div><p style="color:#8899aa;margin-top:0.3rem;">PK Score</p></div>', unsafe_allow_html=True)
        
        # Summary Table
        try:
            summary = get_pk_summary_table(pr)
            if summary:
                summary_df = pd.DataFrame(summary)
                st.dataframe(summary_df, width='stretch', hide_index=True)
        except Exception as e:
            st.warning(f"Could not generate summary: {str(e)}")
        
        # Show individual results in expandable sections
        with st.expander("Absorption (Caco-2)", expanded=True):
            caco = pr.get("absorption", {}).get("caco2", {})
            if caco:
                st.metric("logPapp", f"{caco.get('logPapp', 'N/A')} cm/s")
                st.metric("Absorption Class", caco.get('absorption', 'N/A'))
                st.caption(caco.get('interpretation', ''))
        
        with st.expander("Distribution"):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                ppb = pr.get("distribution", {}).get("protein_binding", {})
                if ppb:
                    st.metric("Protein Bound", f"{ppb.get('percent_bound', 'N/A')}%")
                    st.caption(ppb.get('binding_class', ''))
            with col_d2:
                vd = pr.get("distribution", {}).get("volume_distribution", {})
                if vd:
                    st.metric("Volume of Distribution", f"{vd.get('vd', 'N/A')} L/kg")
                    st.caption(vd.get('vd_class', ''))
        
        with st.expander("Metabolism"):
            cyp = pr.get("metabolism", {}).get("cyp450", {})
            if cyp:
                cols = st.columns(3)
                for col, iso in zip(cols, ['CYP2C9', 'CYP2D6', 'CYP3A4']):
                    data = cyp.get('isoforms', {}).get(iso, {})
                    with col:
                        st.metric(iso, data.get('prediction', 'N/A'))
                st.caption(f"Inhibited: {cyp.get('total_inhibited', 0)}/3 isoforms")
            
            metab = pr.get("metabolism", {}).get("metabolic_activation", {})
            if metab:
                risk = metab.get('metabolic_activation_risk', 'Low')
                st.metric("Metabolic Activation Risk", risk)
                st.caption(metab.get('warning', ''))
        
        with st.expander("Excretion"):
            cl = pr.get("excretion", {}).get("clearance", {})
            if cl:
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.metric("Clearance", f"{cl.get('clearance', 'N/A')} mL/min/kg")
                with col_e2:
                    t12 = cl.get('half_life', 'N/A')
                    st.metric("Half-Life", f"{t12} hrs" if t12 != 'N/A' else 'N/A')
        
        with st.expander("Safety"):
            ti = pr.get("safety", {}).get("therapeutic_index", {})
            if ti:
                st.metric("Therapeutic Index", f"TI = {ti.get('therapeutic_index', 'N/A')}")
                st.caption(ti.get('alert', ''))
        
        # Flags/Warnings
        if pr.get('flags'):
            st.markdown("---")
            st.markdown('<p style="color:#ff3355;">Warnings:</p>', unsafe_allow_html=True)
            for flag in pr['flags']:
                st.warning(flag)
    
    st.markdown('</div>', unsafe_allow_html=True)

def optimizer_page(username, tier):
    """Molecule optimization suggestions."""
    st.markdown('<p class="section-header">MOLECULE OPTIMIZER</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if 'smiles_input' not in st.session_state or not st.session_state.smiles_input:
        st.info("Enter a SMILES in the Predict page first")
    else:
        smiles = st.session_state.smiles_input
        st.markdown(f'<p style="color:#8899aa;">Compound: <b>{smiles[:50]}</b></p>', unsafe_allow_html=True)
        
        if st.button("GET OPTIMIZATION SUGGESTIONS", use_container_width=True, type="primary"):
            with st.spinner("Analyzing..."):
                opt = get_optimization_score(smiles)
                st.session_state.opt_score = opt
                st.session_state.opt_suggestions = suggest_modifications(smiles)
        
        if 'opt_score' in st.session_state:
            s = st.session_state.opt_score
            st.metric("Optimization Potential", f"{s.get('optimization_potential', 0)}/100")
            st.caption(f"Toxic Substructures: {s.get('toxic_substructures', 0)} | Lipinski Violations: {s.get('lipinski_violations', 0)}")
        
        if 'opt_suggestions' in st.session_state:
            for sug in st.session_state.opt_suggestions:
                if 'error' not in sug:
                    st.info(f"{sug.get('toxicophore', '')}: {sug.get('suggestion', '')}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def fda_check_page(username, tier):
    """FDA approval checker."""
    st.markdown('<p class="section-header">FDA APPROVAL CHECKER</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    drug_name = st.text_input("Enter Drug Name", placeholder="Aspirin, Ibuprofen, Paracetamol")
    
    if st.button("CHECK FDA STATUS", use_container_width=True, type="primary") and drug_name:
        with st.spinner(f"Querying FDA for {drug_name}..."):
            fda = get_fda_summary(drug_name)
            st.session_state.fda_result = fda
    
    if 'fda_result' in st.session_state:
        r = st.session_state.fda_result
        app = r.get('approval', {})
        if app.get('fda_approved'):
            st.success(f"APPROVED | Sponsor: {app.get('sponsor', 'N/A')}")
        else:
            st.warning(app.get('status', 'Not found'))
    
    st.markdown('</div>', unsafe_allow_html=True)


def admin_page(username, tier):
    """Admin panel."""
    st.markdown('<p class="section-header">ADMIN PANEL</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if tier not in ['pro', 'enterprise']:
        st.error("Admin access requires Pro or Enterprise")
    else:
        st.success(f"Welcome Admin: {username} ({tier})")
        
        from admin_panel import get_all_users, get_platform_stats
        users = get_all_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True)
        
        stats = get_platform_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Predictions", stats.get('total_predictions', 0))
        with col2:
            st.metric("Active Users", stats.get('active_users', 0))
    
    st.markdown('</div>', unsafe_allow_html=True)


def dashboard_page(username, tier):
    """Admin Dashboard with analytics."""
    st.markdown('<p class="section-header">DASHBOARD</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    try:
        from admin_dashboard import get_dashboard_stats, get_user_activity_feed
        stats = get_dashboard_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Users", stats["users"]["total_active"])
        with col2:
            st.metric("Predictions", stats["predictions"]["total"])
        with col3:
            st.metric("Today", stats["predictions"]["today"])
        with col4:
            st.metric("API Calls", stats["api"]["total_calls"])
        
        st.markdown("---")
        st.markdown('<p style="color:#00ffff;">Recent Activity</p>', unsafe_allow_html=True)
        activities = get_user_activity_feed(10)
        if activities:
            for act in activities:
                st.text(f"{act['date'][:16]} | {act['user']} | Score: {act['score']}")
    except Exception as e:
        st.warning(f"Dashboard loading: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def profile_page(username, tier):
    """User Profile page."""
    st.markdown('<p class="section-header">MY PROFILE</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    try:
        from user_profiles import get_user_profile, get_user_stats, get_user_badges, get_saved_compounds
        
        profile = get_user_profile(username)
        stats = get_user_stats(username)
        badges = get_user_badges(username)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f'<p style="font-size:1.5rem;color:#00ffff;">{username}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color:#8899aa;">{profile.get("email", "N/A")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color:#8899aa;">Tier: <b style="color:#ffaa00;">{tier.upper()}</b></p>', unsafe_allow_html=True)
            if badges:
                st.markdown('<p style="color:#00ffff;margin-top:1rem;">Badges</p>', unsafe_allow_html=True)
                for badge in badges:
                    st.markdown(f'<span title="{badge["description"]}">{badge["icon"]}</span>', unsafe_allow_html=True)
        
        with col2:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Predictions", stats.get("total_predictions", 0))
            with col_b:
                st.metric("Avg Score", stats.get("avg_score", 0))
            with col_c:
                st.metric("Today", stats.get("today_predictions", 0))
            
            st.markdown('<p style="color:#00ffff;margin-top:1rem;">Saved Compounds</p>', unsafe_allow_html=True)
            saved = get_saved_compounds(username)
            if len(saved) > 0:
                st.dataframe(saved, use_container_width=True, hide_index=True)
            else:
                st.info("No saved compounds yet")
    except Exception as e:
        st.warning(f"Profile loading: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def genetics_page(username, tier):
    """Genetic Factors & Personalized Dosing."""
    st.markdown('<p class="section-header">GENETIC FACTORS</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if 'smiles_input' not in st.session_state or not st.session_state.smiles_input:
        st.info("Enter a SMILES in Predict page first")
    else:
        smiles = st.session_state.smiles_input
        
        col1, col2 = st.columns(2)
        with col1:
            ethnicity = st.selectbox("Ethnicity", ["Caucasian", "Asian", "African", "Hispanic"])
        with col2:
            age = st.number_input("Age", 0, 120, 30)
        
        if st.button("PREDICT GENETIC RISK", use_container_width=True):
            genetic = predict_polymorphism_risk(smiles, ethnicity)
            st.session_state.genetic = genetic
            
            dose = get_personalized_dosing(smiles, ethnicity, age, 70)
            st.session_state.personalized_dose = dose
        
        if 'genetic' in st.session_state:
            g = st.session_state.genetic
            st.metric("Genetic Risk", g['overall_genetic_risk'])
            st.info(g['pharmacogenetic_recommendation'])
        
        if 'personalized_dose' in st.session_state:
            d = st.session_state.personalized_dose
            st.metric("Recommended Dose", f"{d['recommended_percent']}%")
            for adj in d['adjustments']:
                st.caption(f"• {adj}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def interactions_page(username, tier):
    """Drug-Drug Interaction Checker."""
    st.markdown('<p class="section-header">DRUG INTERACTIONS</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        drug1 = st.text_input("Drug 1 SMILES", "CC(=O)OC1=CC=CC=C1C(=O)O")
        name1 = st.text_input("Drug 1 Name", "Aspirin")
    with col2:
        drug2 = st.text_input("Drug 2 SMILES", "CC(=O)NC1=CC=C(O)C=C1")
        name2 = st.text_input("Drug 2 Name", "Paracetamol")
    
    if st.button("CHECK INTERACTIONS", use_container_width=True):
        result = predict_drug_interaction(drug1, drug2, name1, name2)
        st.session_state.ddi = result
    
    if 'ddi' in st.session_state:
        d = st.session_state.ddi
        risk_color = {"Critical": "#ff3355", "High": "#ff6600", "Medium": "#ffaa00", "Low": "#00ff66"}
        st.markdown(f'<p style="font-size:1.5rem;color:{risk_color.get(d["overall_risk"], "#fff")};">Risk: {d["overall_risk"]}</p>', unsafe_allow_html=True)
        st.caption(d['recommendation'])
        
        if d['detected_interactions']:
            st.markdown("**Detected Interactions:**")
            for i in d['detected_interactions']:
                st.markdown(f'<div style="padding:0.3rem;background:rgba(255,255,255,0.03);border-radius:5px;margin-bottom:0.2rem;"><b>{i["mechanism"]}</b>: {i["effect"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def disease_page(username, tier):
    """Disease State Adjustments."""
    st.markdown('<p class="section-header">DISEASE STATE ADJUSTMENTS</p>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if 'smiles_input' not in st.session_state or not st.session_state.smiles_input:
        st.info("Enter a SMILES in Predict page first")
    else:
        smiles = st.session_state.smiles_input
        
        tab1, tab2, tab3 = st.tabs(["Liver", "Kidney", "Age"])
        
        with tab1:
            if st.button("ASSESS LIVER RISK", use_container_width=True):
                liver = predict_liver_impairment_risk(smiles)
                st.session_state.liver = liver
            
            if 'liver' in st.session_state:
                l = st.session_state.liver
                st.metric("Hepatic Risk", l['hepatic_risk'])
                st.caption(l['recommendation'])
        
        with tab2:
            if st.button("ASSESS KIDNEY RISK", use_container_width=True):
                kidney = predict_kidney_impairment_risk(smiles)
                st.session_state.kidney = kidney
            
            if 'kidney' in st.session_state:
                k = st.session_state.kidney
                st.metric("Renal Risk", k['renal_risk'])
                st.caption(k['recommendation'])
        
        with tab3:
            age = st.number_input("Patient Age", 0, 120, 30, key="disease_age")
            if st.button("GET AGE RECOMMENDATIONS", use_container_width=True):
                age_rec = get_age_based_recommendations(smiles, age)
                st.session_state.age_rec = age_rec
            
            if 'age_rec' in st.session_state:
                a = st.session_state.age_rec
                st.metric("Age Group", a['age_group'])
                st.metric("Dose", f"{a['recommended_percent']}%")
                st.caption(a['note'])
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    optimize_for_mobile()
    """Main application with luxury cinema-grade interface."""
    
    # Header
    st.markdown('<div style="text-align:center;padding:2rem 0 1rem 0;">', unsafe_allow_html=True)
    st.markdown('<h1 class="neon-title">TOXSCREEN-AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="neon-subtitle">Luxury Biotech Platform • Cinema-Grade Interface</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#667788;font-size:0.7rem;letter-spacing:4px;">ML • BLOCKCHAIN • API • AUTH • PAYMENTS</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Authentication
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    if authentication_status == False:
        st.error("Username/password is incorrect")
        st.markdown("""
        <div class="glass-card" style="text-align:center;margin-top:2rem;">
            <p style="color:#8899aa;">Demo Credentials:</p>
            <p style="color:#00ff66;">Free: demo / demo123</p>
            <p style="color:#00ffff;">Pro: devil / devil@123ch</p>
            <p style="color:#ff00ff;">Enterprise: monkey / monkey@123ch</p>
        </div>
        """, unsafe_allow_html=True)
    elif authentication_status == None:
        st.warning("Please enter your credentials to access the platform")
        st.markdown("""
        <div class="glass-card" style="text-align:center;margin-top:2rem;">
            <p style="color:#8899aa;">Demo Credentials:</p>
            <p style="color:#00ff66;">Free: demo / demo123</p>
            <p style="color:#00ffff;">Pro: devil / devil@123ch</p>
            <p style="color:#ff00ff;">Enterprise: monkey / monkey@123ch</p>
        </div>
        """, unsafe_allow_html=True)
    elif authentication_status:
        tier = get_user_tier(username)
        if username in DEMO_USERS and DEMO_USERS[username]['tier'] != 'free':
            set_user_tier(username, DEMO_USERS[username]['tier'])
            tier = DEMO_USERS[username]['tier']
        
        with st.sidebar:
            st.markdown(f"""
            <div style="text-align:center;padding:1rem 0;">
                <p style="font-family:Orbitron;color:#00ffff;font-size:1rem;letter-spacing:2px;">WELCOME</p>
                <p style="color:#ccddee;font-weight:600;">{name}</p>
                <p style="color:#8899aa;font-size:0.8rem;">Tier: <span style="color:#00ffff;">{tier.upper()}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            authenticator.logout('Logout', 'sidebar')
            
            st.markdown("---")
            st.markdown('<p style="font-family:Orbitron;color:#00ffff;font-size:0.8rem;text-align:center;letter-spacing:2px;">NAVIGATION</p>', unsafe_allow_html=True)
            
            page = st.radio(
                "Select Page",
                ["Predict", "ADME Panel", "PK Dashboard", "Batch Process", "Optimizer", "FDA Check", "Genetics", "Drug Interactions", "Disease States", "Dashboard", "Profile", "History", "Subscription", "API", "Admin"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            usage = check_usage_limit(username)
            st.markdown(f"""
            <div class="glass-card" style="padding:0.8rem;text-align:center;">
                <p style="font-family:Rajdhani;color:#8899aa;font-size:0.7rem;">DAILY USAGE</p>
                <p style="font-family:Orbitron;color:#ffaa00;font-size:1rem;">{usage['used_today']}/{usage['daily_limit']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if page == "Predict":
            predict_page(username, tier)
        elif page == "ADME Panel":
            adme_page(username, tier)
        elif page == "PK Dashboard":
            pk_dashboard_page(username, tier)
        elif page == "Batch Process":
            batch_page(username, tier)
        elif page == "Optimizer":
            optimizer_page(username, tier)
        elif page == "Dashboard":
            dashboard_page(username, tier)
        elif page == "Genetics":
            genetics_page(username, tier)
        elif page == "Drug Interactions":
            interactions_page(username, tier)
        elif page == "Disease States":
            disease_page(username, tier)
        elif page == "FDA Check":
            fda_check_page(username, tier)
        elif page == "Profile":
            profile_page(username, tier)
        elif page == "History":
            history_page(username)
        elif page == "Subscription":
            subscription_page(username, tier)
        elif page == "API":
            api_page(username, tier)
        elif page == "Admin":
            admin_page(username, tier)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;padding:0.5rem;">
        <p style="font-family:Rajdhani;color:#445566;font-size:0.65rem;letter-spacing:3px;">
        TOXSCREEN-AI • LUXURY BIOTECH PLATFORM • CINEMA-GRADE INTERFACE
        </p>
        <p style="color:#334455;font-size:0.6rem;">
        ML • BLOCKCHAIN • API • AUTH • PAYMENTS • DAYS 1-6
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
