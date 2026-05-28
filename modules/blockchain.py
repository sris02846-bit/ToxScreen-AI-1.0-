"""
Blockchain Module
Web3 integration for storing predictions on Polygon Mumbai testnet.
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Optional


# Note: Full Web3 integration requires:
# 1. MetaMask wallet with MATIC on Mumbai testnet
# 2. Infura/Alchemy API key
# 3. Deployed smart contract address
# 
# For demo purposes, we simulate the blockchain transaction
# and provide the structure for real integration.

# Smart Contract ABI (simplified for ToxHashStore)
TOX_HASH_STORE_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "smiles", "type": "string"},
            {"internalType": "string", "name": "resultHash", "type": "string"},
            {"internalType": "uint256", "name": "score", "type": "uint256"}
        ],
        "name": "storePrediction",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "predictionId", "type": "uint256"}],
        "name": "getPrediction",
        "outputs": [
            {"internalType": "string", "name": "smiles", "type": "string"},
            {"internalType": "string", "name": "resultHash", "type": "string"},
            {"internalType": "uint256", "name": "score", "type": "uint256"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Contract address on Polygon Mumbai (placeholder - deploy your own)
CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000000"

# Network configuration
MUMBAI_RPC_URL = "https://rpc-mumbai.maticvigil.com"
CHAIN_ID = 80001


def hash_prediction(smiles: str, druglikeness_score: float, risk_level: str) -> str:
    """
    Create SHA-256 hash of prediction data.
    
    Args:
        smiles: SMILES string
        druglikeness_score: Drug-likeness score
        risk_level: Risk level assessment
        
    Returns:
        SHA-256 hash string
    """
    data = {
        "smiles": smiles,
        "score": druglikeness_score,
        "risk_level": risk_level,
        "timestamp": datetime.now().isoformat()
    }
    
    data_string = json.dumps(data, sort_keys=True)
    hash_object = hashlib.sha256(data_string.encode())
    return hash_object.hexdigest()


def simulate_blockchain_transaction(smiles: str, druglikeness_score: float, 
                                     risk_level: str) -> Dict:
    """
    Simulate recording a prediction on blockchain.
    In production, this would use web3.py to send a real transaction.
    
    Args:
        smiles: SMILES string
        druglikeness_score: Drug-likeness score
        risk_level: Risk level assessment
        
    Returns:
        Dictionary with simulated transaction details
    """
    # Generate prediction hash
    pred_hash = hash_prediction(smiles, druglikeness_score, risk_level)
    
    # Simulate transaction hash (in real implementation, this comes from web3)
    tx_data = f"{smiles}{pred_hash}{datetime.now().timestamp()}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
    
    # Simulate block number
    block_number = 45000000 + int(datetime.now().timestamp()) % 10000
    
    return {
        "success": True,
        "transaction_hash": f"0x{tx_hash[:64]}",
        "block_number": block_number,
        "prediction_hash": pred_hash,
        "explorer_url": f"https://mumbai.polygonscan.com/tx/0x{tx_hash[:64]}",
        "network": "Polygon Mumbai Testnet",
        "contract_address": CONTRACT_ADDRESS,
        "note": "SIMULATED TRANSACTION - For production, deploy contract and use real web3.py"
    }


def get_web3_connection() -> Optional[object]:
    """
    Attempt to connect to Web3 provider.
    Falls back to simulation if connection fails.
    
    Returns:
        Web3 instance or None
    """
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider(MUMBAI_RPC_URL))
        if w3.is_connected():
            return w3
    except Exception:
        pass
    
    return None


def record_on_blockchain(smiles: str, druglikeness_score: float, 
                          risk_level: str, private_key: str = None) -> Dict:
    """
    Record prediction on blockchain.
    Uses real Web3 if connected, otherwise simulates.
    
    Args:
        smiles: SMILES string
        druglikeness_score: Drug-likeness score
        risk_level: Risk level assessment
        private_key: Optional private key for signing
        
    Returns:
        Dictionary with transaction details
    """
    w3 = get_web3_connection()
    
    if w3 and private_key:
        try:
            # Real blockchain transaction
            account = w3.eth.account.from_key(private_key)
            contract = w3.eth.contract(
                address=CONTRACT_ADDRESS,
                abi=TOX_HASH_STORE_ABI
            )
            
            # Build transaction
            score_uint = int(druglikeness_score * 100)
            result_hash = hash_prediction(smiles, druglikeness_score, risk_level)
            
            tx = contract.functions.storePrediction(
                smiles,
                result_hash,
                score_uint
            ).build_transaction({
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gas': 200000,
                'gasPrice': w3.eth.gas_price
            })
            
            # Sign and send
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {
                "success": True,
                "transaction_hash": tx_hash.hex(),
                "explorer_url": f"https://mumbai.polygonscan.com/tx/{tx_hash.hex()}",
                "network": "Polygon Mumbai Testnet",
                "note": "REAL TRANSACTION"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "note": "Transaction failed, falling back to simulation"
            }
    
    # Fallback to simulation
    return simulate_blockchain_transaction(smiles, druglikeness_score, risk_level)
