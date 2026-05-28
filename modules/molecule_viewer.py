"""
3D Molecule Viewer & Interactive Charts Module
Provides 3D structure visualization and interactive data charts.
"""

import streamlit as st
from rdkit import Chem
from rdkit.Chem import AllChem, Draw, Descriptors
from rdkit.Chem import rdMolDescriptors
import py3Dmol
import pandas as pd
import numpy as np
from typing import Dict, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


def generate_3d_coordinates(smiles: str) -> Optional[Chem.Mol]:
    """
    Generate 3D coordinates for a molecule.
    
    Args:
        smiles: SMILES string
        
    Returns:
        RDKit molecule with 3D coordinates or None
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol)
    
    return mol


def show_3d_molecule(smiles: str, width: int = 400, height: int = 300):
    """
    Display 3D molecule viewer in Streamlit.
    
    Args:
        smiles: SMILES string
        width: Viewer width
        height: Viewer height
    """
    mol = generate_3d_coordinates(smiles)
    if mol is None:
        st.error("Could not generate 3D structure")
        return
    
    # Convert to XYZ format for py3Dmol
    conf = mol.GetConformer()
    xyz = f"{mol.GetNumAtoms()}\n\n"
    
    for atom in mol.GetAtoms():
        pos = conf.GetAtomPosition(atom.GetIdx())
        symbol = atom.GetSymbol()
        xyz += f"{symbol} {pos.x:.4f} {pos.y:.4f} {pos.z:.4f}\n"
    
    # Create 3D viewer
    viewer = py3Dmol.view(width=width, height=height)
    viewer.addModel(xyz, "xyz")
    viewer.setStyle({"stick": {}, "sphere": {"scale": 0.3}})
    viewer.setBackgroundColor("#0a0a1a")
    viewer.zoomTo()
    
    # Render in Streamlit
    viewer_html = viewer._make_html()
    st.components.v1.html(viewer_html, width=width, height=height)


def create_toxicity_radar_chart(scores: Dict) -> str:
    """
    Create radar chart HTML for toxicity scores.
    
    Args:
        scores: Dictionary of organ toxicity scores
        
    Returns:
        HTML string for radar chart
    """
    labels = list(scores.keys())
    values = list(scores.values())
    
    # Simple HTML/CSS radar chart
    html = """
    <div style="position:relative;width:300px;height:300px;margin:0 auto;">
        <canvas id="radarChart" width="300" height="300"></canvas>
    </div>
    <script>
    // Radar chart would be rendered with Chart.js in production
    </script>
    """
    return html


def create_property_distribution_chart(properties: Dict) -> pd.DataFrame:
    """
    Create property distribution data for charting.
    
    Args:
        properties: Molecular properties dictionary
        
    Returns:
        DataFrame formatted for charts
    """
    chart_data = []
    
    for name, value in properties.items():
        if isinstance(value, (int, float)):
            chart_data.append({
                "Property": name,
                "Value": value,
                "Normalized": min(100, max(0, value))
            })
    
    return pd.DataFrame(chart_data)


def create_bar_chart_html(labels: list, values: list, title: str = "") -> str:
    """
    Create interactive bar chart HTML.
    
    Args:
        labels: Bar labels
        values: Bar values
        title: Chart title
        
    Returns:
        HTML string
    """
    max_val = max(values) if values else 1
    
    html = f'<div style="padding:1rem;"><p style="color:#00ffff;text-align:center;">{title}</p>'
    
    for label, value in zip(labels, values):
        width = (value / max_val) * 100
        color = "#00ff66" if value >= 70 else "#ffaa00" if value >= 40 else "#ff3355"
        html += f"""
        <div style="margin-bottom:0.5rem;">
            <span style="color:#8899aa;font-size:0.7rem;">{label}</span>
            <div style="background:rgba(255,255,255,0.05);border-radius:5px;height:20px;">
                <div style="width:{width}%;height:100%;background:{color};border-radius:5px;"></div>
            </div>
            <span style="color:#ccddee;font-size:0.7rem;float:right;">{value}</span>
        </div>
        """
    
    html += '</div>'
    return html
