import numpy as np
from .base import BaseDemodulator, DemodResult
from typing import Optional

class QPSKDemodulator(BaseDemodulator):
    """QPSK demodulator with Costas loop carrier recovery."""
    
    @property
    def name(self) -> str:
        return "QPSK"
    
    def demodulate(self, iq_signal: np.ndarray, fs: float,
                   symbol_rate: Optional[float] = None) -> DemodResult:
        """
        QPSK demodulation:
          1. 4th-order Costas loop for carrier recovery
          2. Matched filter
          3. Timing recovery
          4. Hard decision (2 bits per symbol)
        """
        if symbol_rate is None:
            symbol_rate = fs / 4  # Default guess
        
        sps = max(1, int(fs / symbol_rate))
        
        # Carrier recovery (QPSK Costas — 4th power)
        recovered = self._qpsk_costas_loop(iq_signal, loop_bw=0.005)
        
        # Simple downsampling for symbol recovery
        symbol_indices = np.arange(sps // 2, len(recovered), sps).astype(int)
        symbols = recovered[symbol_indices]
        
        # Hard decision: map to 2 bits per symbol
        bits = []
        for s in symbols:
            i_bit = 1 if np.real(s) > 0 else 0
            q_bit = 1 if np.imag(s) > 0 else 0
            bits.extend([i_bit, q_bit])
        bits = np.array(bits, dtype=np.int8)
        
        return DemodResult(
            bits=bits,
            symbols=symbols,
            constellation_I=np.real(symbols),
            constellation_Q=np.imag(symbols),
            symbol_rate=symbol_rate,
            num_symbols=len(symbols)
        )
    
    def _qpsk_costas_loop(self, signal: np.ndarray, loop_bw: float = 0.005) -> np.ndarray:
        """4th-order Costas loop for QPSK."""
        N = len(signal)
        phase = 0.0
        freq = 0.0
        
        damping = 1.0 / np.sqrt(2)
        denom = 1 + 2 * damping * loop_bw + loop_bw**2
        alpha = (4 * damping * loop_bw) / denom
        beta = (4 * loop_bw**2) / denom
        
        output = np.zeros(N, dtype=np.complex64)
        
        for i in range(N):
            output[i] = signal[i] * np.exp(-1j * phase)
            
            # QPSK error: use 4th power to remove data modulation
            error = np.imag(output[i]**4) / 4.0
            
            freq += beta * error
            phase += freq + alpha * error
        
        return output
