from abc import ABC, abstractmethod
import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class DemodResult:
    """Demodulation output."""
    bits: np.ndarray                 # Decoded bit stream (0/1 array)
    symbols: np.ndarray              # Complex symbols after timing recovery
    constellation_I: np.ndarray      # I values for plotting
    constellation_Q: np.ndarray      # Q values for plotting
    symbol_rate: float               # Estimated or user-provided symbol rate
    num_symbols: int

class BaseDemodulator(ABC):
    """Abstract base for all demodulators."""
    
    @abstractmethod
    def demodulate(self, iq_signal: np.ndarray, fs: float,
                   symbol_rate: Optional[float] = None) -> DemodResult:
        """Demodulate the signal and return bit stream + constellation."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
