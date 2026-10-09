import numpy as np
import joblib
from dataclasses import dataclass
from typing import Dict
from .features import extract_features

@dataclass
class ClassificationResult:
    """Modulation classification output."""
    predicted_mod: str               # E.g., "QPSK"
    confidence: float                # 0.0 to 1.0
    all_probabilities: Dict[str, float]  # All class probabilities
    features_used: np.ndarray        # The 6 features extracted


class ModulationClassifier:
    """Random Forest-based automatic modulation recognition."""
    
    def __init__(self, model_path: str, scaler_path: str, encoder_path: str):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.label_encoder = joblib.load(encoder_path)
        self.classes = self.label_encoder.classes_
    
    def classify(self, iq_signal: np.ndarray, fs: float = 1.0) -> ClassificationResult:
        """
        Classify the modulation type of an IQ signal.
        
        Args:
            iq_signal: Complex64 numpy array
            fs: Sample rate (Hz)
        
        Returns:
            ClassificationResult with prediction and confidence
        """
        # Extract features
        features = extract_features(iq_signal, fs)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Map back to labels
        predicted_label = self.label_encoder.inverse_transform([prediction])[0]
        confidence = float(np.max(probabilities))
        
        # All class probabilities
        prob_dict = {
            self.classes[i]: float(probabilities[i])
            for i in range(len(self.classes))
        }
        
        return ClassificationResult(
            predicted_mod=predicted_label,
            confidence=confidence,
            all_probabilities=prob_dict,
            features_used=features
        )
