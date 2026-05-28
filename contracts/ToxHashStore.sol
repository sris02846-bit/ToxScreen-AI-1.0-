// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ToxHashStore
 * @dev Stores toxicity prediction hashes on-chain for immutability
 */
contract ToxHashStore {
    
    struct Prediction {
        string smiles;
        string resultHash;
        uint256 score;        // Drug-likeness score * 100
        uint256 timestamp;
        address submitter;
    }
    
    // Mapping from prediction ID to Prediction
    mapping(uint256 => Prediction) public predictions;
    
    // Counter for prediction IDs
    uint256 public predictionCount;
    
    // Events
    event PredictionStored(
        uint256 indexed predictionId,
        string smiles,
        string resultHash,
        uint256 score,
        address submitter
    );
    
    /**
     * @dev Store a new prediction on-chain
     * @param smiles SMILES string of the molecule
     * @param resultHash SHA-256 hash of the prediction result
     * @param score Drug-likeness score multiplied by 100
     * @return predictionId The ID of the stored prediction
     */
    function storePrediction(
        string memory smiles,
        string memory resultHash,
        uint256 score
    ) public returns (uint256) {
        predictionCount++;
        
        predictions[predictionCount] = Prediction({
            smiles: smiles,
            resultHash: resultHash,
            score: score,
            timestamp: block.timestamp,
            submitter: msg.sender
        });
        
        emit PredictionStored(
            predictionCount,
            smiles,
            resultHash,
            score,
            msg.sender
        );
        
        return predictionCount;
    }
    
    /**
     * @dev Retrieve a prediction by ID
     * @param predictionId The ID of the prediction
     * @return Prediction details
     */
    function getPrediction(uint256 predictionId) 
        public 
        view 
        returns (
            string memory smiles,
            string memory resultHash,
            uint256 score,
            uint256 timestamp
        ) 
    {
        Prediction memory pred = predictions[predictionId];
        return (pred.smiles, pred.resultHash, pred.score, pred.timestamp);
    }
    
    /**
     * @dev Verify if a prediction hash matches stored hash
     * @param predictionId The ID of the prediction
     * @param resultHash Hash to verify
     * @return bool True if hashes match
     */
    function verifyPrediction(uint256 predictionId, string memory resultHash) 
        public 
        view 
        returns (bool) 
    {
        return keccak256(abi.encodePacked(predictions[predictionId].resultHash)) 
               == keccak256(abi.encodePacked(resultHash));
    }
}
