"""
Deep Learning Module for advanced signal classification.

This module provides a 1D Convolutional Neural Network (CNN) architecture
designed to take raw I/Q samples (2xN arrays) directly, bypassing the 
need for manual statistical feature extraction.

Note: Requires PyTorch (`pip install torch`)
"""

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

if TORCH_AVAILABLE:
    class IQNet(nn.Module):
        """
        A 1D-CNN architecture inspired by VT-CNN2 for RadioML.
        Input shape: (Batch, 2, 1024) [I and Q channels, 1024 samples]
        """
        def __init__(self, num_classes=7, dropout_rate=0.5):
            super(IQNet, self).__init__()
            
            # Convolutional blocks
            self.conv1 = nn.Conv1d(in_channels=2, out_channels=64, kernel_size=7, padding=3)
            self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=5, padding=2)
            self.conv3 = nn.Conv1d(in_channels=128, out_channels=128, kernel_size=3, padding=1)
            
            self.pool = nn.MaxPool1d(2)
            self.dropout = nn.Dropout(dropout_rate)
            
            # 1024 -> pool -> 512 -> pool -> 256 -> pool -> 128
            self.fc1 = nn.Linear(128 * 128, 256)
            self.fc2 = nn.Linear(256, num_classes)
            
        def forward(self, x):
            # x shape: (B, 2, L)
            x = self.pool(F.relu(self.conv1(x)))
            x = self.pool(F.relu(self.conv2(x)))
            x = self.pool(F.relu(self.conv3(x)))
            
            # Flatten
            x = x.view(x.size(0), -1)
            
            x = F.relu(self.fc1(x))
            x = self.dropout(x)
            x = self.fc2(x)
            
            return x

class DeepIQClassifier:
    """Wrapper for inference using a pre-trained PyTorch model."""
    
    def __init__(self, model_path: str, classes: list):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for DeepIQClassifier")
            
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.classes = classes
        
        self.model = IQNet(num_classes=len(classes))
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
    def classify(self, iq_signal: np.ndarray) -> dict:
        """
        Run inference on raw I/Q data.
        iq_signal: complex64 numpy array of shape (N,)
        """
        # Ensure length is 1024 (pad or truncate)
        L = 1024
        if len(iq_signal) > L:
            iq_signal = iq_signal[:L]
        elif len(iq_signal) < L:
            iq_signal = np.pad(iq_signal, (0, L - len(iq_signal)))
            
        # Convert to (1, 2, 1024) format -> Batch=1, Channels=2 (I, Q)
        i_chan = np.real(iq_signal)
        q_chan = np.imag(iq_signal)
        tensor_in = torch.tensor([[i_chan, q_chan]], dtype=torch.float32).to(self.device)
        
        with torch.no_grad():
            logits = self.model(tensor_in)
            probs = F.softmax(logits, dim=1)[0].cpu().numpy()
            
        pred_idx = np.argmax(probs)
        return {
            "prediction": self.classes[pred_idx],
            "confidence": float(probs[pred_idx]),
            "all_probs": {cls: float(p) for cls, p in zip(self.classes, probs)}
        }
