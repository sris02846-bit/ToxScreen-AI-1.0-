# ToxScreen-AI

Computational Drug Toxicity and Drug-Likeness Screening Platform

ToxScreen-AI is a Streamlit-based web application for early-stage drug
screening that evaluates molecular properties, drug-likeness rules,
and toxicophore alerts.

## Features

### Day 1
- SMILES parsing with RDKit
- Molecular weight calculation
- MW greater than 500 warning system
- Test molecules included: Aspirin, Ethanol

### Day 2
- Lipinski Rule of Five evaluation with pass/fail table
- Veber Rules for oral bioavailability prediction
- Toxicophore Detection using 10 structural alerts
- Drug-Likeness Score with combined penalty system
- Downloadable Reports in text format
- Clean UI with cards, tabs, and color-coded results

## Technology Stack

- Frontend and Backend: Streamlit
- Cheminformatics: RDKit
- Data Processing: Pandas, NumPy
- Platform: ARM64 Snapdragon X and x86_64 compatible

## Installation

Clone the repository:
git clone https://github.com/YOUR_USERNAME/ToxScreen-AI.git
cd ToxScreen-AI

Create virtual environment:
python3.9 -m venv venv
source venv/bin/activate
Install dependencies:
pip install -r requirements.txt

Note: If you encounter NumPy errors, run:
pip install "numpy<2"



## Usage

Run the application:
streamlit run app.py

Or specify a custom port:
streamlit run app.py --server.port 8501


## Project Structure
ToxScreen-AI/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- modules/
| |-- init.py
| |-- molecular_parser.py
| |-- lipinski_rules.py
| |-- veber_rules.py
| |-- toxicophores.py
|-- data/
|-- toxicophore_patterns.json


## Module Descriptions

### molecular_parser.py
Handles SMILES string parsing and calculates basic molecular
properties such as molecular formula, weight, atom counts,
and ring counts.

### lipinski_rules.py
Evaluates Lipinski Rule of Five criteria:
- Molecular Weight less than or equal to 500 g/mol
- LogP less than or equal to 5
- Hydrogen Bond Donors less than or equal to 5
- Hydrogen Bond Acceptors less than or equal to 10

Returns pass/fail status for each rule with detailed table.

### veber_rules.py
Evaluates Veber Rules for oral bioavailability:
- Rotatable Bonds less than or equal to 10
- Topological Polar Surface Area less than or equal to 140 square Angstroms

Returns pass/fail status with detailed results.

### toxicophores.py
Detects toxic structural alerts using 10 SMARTS patterns:
- Aniline (High Risk)
- Epoxide (High Risk)
- Nitroaromatic (High Risk)
- Michael Acceptor (High Risk)
- Alkyl Halide (Medium Risk)
- Thiourea (Medium Risk)
- Hydrazine (High Risk)
- Aromatic Hydroxylamine (High Risk)
- Thiophene (Low Risk)
- Quinone (High Risk)

Calculates toxicity risk score and overall risk level.

## Scoring System

Drug-Likeness Score Formula:
Score = 100 - (Lipinski_Violations x 15) - (Veber_Violations x 10) - (Toxicity_Score x 0.5)

Where:
- Lipinski Violations range from 0 to 4
- Veber Violations range from 0 to 2
- Toxicity Score ranges from 0 to 100

## Score Interpretation

| Score Range | Interpretation |
|-------------|----------------|
| 80 - 100 | Excellent drug-like properties |
| 60 - 79 | Good drug-like properties |
| 40 - 59 | Moderate concerns, optimization needed |
| 0 - 39 | Poor drug-like properties, significant issues |

## Test Molecules

| Name | SMILES | Molecular Weight |
|------|--------|------------------|
| Aspirin | CC(=O)OC1=CC=CC=C1C(=O)O | 180.16 g/mol |
| Paracetamol | CC(=O)NC1=CC=C(O)C=C1 | 151.16 g/mol |
### Streamlit Not Found
Ensure virtual environment is activated:
| Ibuprofen | CC(C)CC1=CC=C(C=C1)C(C)C(=O)O | 206.28 g/mol |
| Caffeine | CN1C=NC2=C1C(=O)N(C(=O)N2C)C | 194.19 g/mol |
| Morphine | CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O | 285.34 g/mol |
| Penicillin G | CC1(C(N2C(S1)C(C2=O)NC(=O)CC3=CC=CC=C3)C(=O)O)C | 334.39 g/mol |

## Troubleshooting

### RDKit Import Error
If you see NumPy compatibility errors:
pip uninstall numpy -y
pip install "numpy<2"

### Streamlit Not Found
Ensure virtual environment is activated:
source venv/bin/activate
pip install -r requirements.txt

### Port Already in Use
Kill existing Streamlit process or use different port:
streamlit run app.py --server.port 8502

## Compatibility

- Windows 11 ARM64 (Snapdragon X) - Native
- Windows 10/11 x64 - Compatible
- Linux ARM64 (aarch64) - Native
- Linux x64 - Compatible
- macOS Apple Silicon (ARM64) - Compatible
- macOS Intel (x64) - Compatible
- Python 3.9 or higher required

## Dependencies

streamlit >= 1.28.0
rdkit-pypi >= 2022.9.5
pandas >= 2.1.0
numpy < 2.0

## Development Notes

This project was built and tested on:
- Device: Snapdragon X ARM64 Laptop
- OS: Ubuntu 24.04 via WSL2
- Python: 3.9
- All packages run natively on ARM64

## License

MIT License

## Author

Your Name

---

Built for computational drug discovery screening and educational purposes.