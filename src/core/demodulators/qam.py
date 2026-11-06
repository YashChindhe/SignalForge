import numpy as np
from .base import BaseDemodulator, DemodResult
from typing import Optional

class QAM16Demodulator(BaseDemodulator):
    """16-QAM Demodulator."""
    
    @property
    def name(self) -> str:
        return "16QAM"
    
    def demodulate(self, iq_signal: np.ndarray, fs: float,
                   symbol_rate: Optional[float] = None) -> DemodResult:
        """
        16-QAM Demodulation (Basic decision-directed approach).
        Assumes carrier recovery has roughly converged, or uses CMA in a full system.
        """
        if symbol_rate is None:
            symbol_rate = fs / 4  # Default guess
            
        sps = max(1, int(fs / symbol_rate))
        
        # Simple matched filter and downsampling
        if sps > 1:
            kernel = np.ones(sps) / sps
            filtered_i = np.convolve(np.real(iq_signal), kernel, mode='same')
            filtered_q = np.convolve(np.imag(iq_signal), kernel, mode='same')
            filtered = filtered_i + 1j * filtered_q
        else:
            filtered = iq_signal
            
        symbol_indices = np.arange(sps // 2, len(filtered), sps).astype(int)
        symbols = filtered[symbol_indices]
        
        # Normalize amplitude for 16-QAM (Levels: +/-1, +/-3)
        # Average power of 16-QAM is 10 (1^2 + 3^2, etc.)
        # We'll normalize the RMS to sqrt(10)
        rms = np.sqrt(np.mean(np.abs(symbols)**2))
        if rms > 0:
            symbols = symbols * (np.sqrt(10) / rms)
        
        bits = []
        for s in symbols:
            # Slicer for 4 PAM on I and Q
            i_val = np.real(s)
            q_val = np.imag(s)
            
            # I bits (Gray coded)
            b0 = 1 if i_val > 0 else 0
            b1 = 1 if abs(i_val) < 2 else 0
            
            # Q bits (Gray coded)
            b2 = 1 if q_val > 0 else 0
            b3 = 1 if abs(q_val) < 2 else 0
            
            bits.extend([b0, b1, b2, b3])
            
        bits = np.array(bits, dtype=np.int8)
        
        return DemodResult(
            bits=bits,
            symbols=symbols,
            constellation_I=np.real(symbols),
            constellation_Q=np.imag(symbols),
            symbol_rate=symbol_rate,
            num_symbols=len(symbols)
        )
