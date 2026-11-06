import numpy as np
from .features import extract_features
from .classifier import ClassificationResult

class HeuristicClassifier:
    """
    Fallback deterministic classifier to auto-detect basic modulations
    when the trained Random Forest model is not available.
    """
    
    def classify(self, iq_signal: np.ndarray, fs: float = 1.0) -> ClassificationResult:
        features = extract_features(iq_signal, fs)
        
        sigma_a = features[0]      # Amplitude variance
        sigma_f = features[3]      # Frequency variance
        
        # Simple heuristic logic
        # If amplitude varies a lot, it's likely QAM or AM
        if sigma_a > 0.15:
            pred = "16QAM"
            conf = 0.75
        else:
            # Constant envelope. If frequency varies heavily, it's FSK.
            if sigma_f > 0.1:
                pred = "2FSK"  # Hard to distinguish 2/4 without deeper dive
                conf = 0.80
            else:
                # Phase modulation
                pred = "BPSK"  # Hard to distinguish B/Q/8PSK blindly without constellation 
                conf = 0.65
                
        # Fill probabilities with dummy
        probs = {"BPSK": 0.0, "QPSK": 0.0, "2FSK": 0.0, "16QAM": 0.0}
        probs[pred] = conf
        
        return ClassificationResult(
            predicted_mod=pred,
            confidence=conf,
            all_probabilities=probs,
            features_used=features
        )
