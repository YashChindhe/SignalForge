import numpy as np
from .base import BaseDemodulator, DemodResult
from typing import Optional

class BPSKDemodulator(BaseDemodulator):
    """BPSK demodulator using Costas loop carrier recovery."""
    
    @property
    def name(self) -> str:
        return "BPSK"
    
    def demodulate(self, iq_signal: np.ndarray, fs: float,
                   symbol_rate: Optional[float] = None) -> DemodResult:
        """
        BPSK demodulation pipeline:
          1. Costas loop for carrier recovery
          2. Matched filter (RRC)
          3. Mueller & Müller timing recovery
          4. Hard decision
        """
        if symbol_rate is None:
            symbol_rate = self._estimate_symbol_rate(iq_signal, fs)
        
        sps = int(fs / symbol_rate)  # Samples per symbol
        
        # Step 1: Costas Loop (carrier recovery)
        recovered = self._costas_loop(iq_signal, loop_bw=0.01)
        
        # Step 2: Matched filter (simple moving average as RRC approx)
        if sps > 1:
            kernel = np.ones(sps) / sps
            filtered = np.convolve(np.real(recovered), kernel, mode='same')
        else:
            filtered = np.real(recovered)
        
        # Step 3: Timing recovery (Gardner)
        symbols, indices = self._gardner_timing(filtered, sps)
        
        # Step 4: Hard decision
        bits = (symbols > 0).astype(np.int8)
        
        constellation_I = symbols
        constellation_Q = np.zeros_like(symbols)
        
        return DemodResult(
            bits=bits,
            symbols=symbols + 0j,
            constellation_I=constellation_I,
            constellation_Q=constellation_Q,
            symbol_rate=symbol_rate,
            num_symbols=len(symbols)
        )
    
    def _costas_loop(self, signal: np.ndarray, loop_bw: float = 0.01) -> np.ndarray:
        """
        Second-order Costas loop for BPSK carrier recovery.
        """
        N = len(signal)
        phase = 0.0
        freq = 0.0
        
        # Loop filter coefficients (proportional + integral)
        damping = 1.0 / np.sqrt(2)
        bw_norm = loop_bw
        denom = 1 + 2 * damping * bw_norm + bw_norm**2
        alpha = (4 * damping * bw_norm) / denom
        beta = (4 * bw_norm**2) / denom
        
        output = np.zeros(N, dtype=np.complex64)
        
        for i in range(N):
            # Mix input with NCO
            output[i] = signal[i] * np.exp(-1j * phase)
            
            # Error detector (BPSK: sign of I * Q)
            error = np.real(output[i]) * np.imag(output[i])
            
            # Loop filter
            freq += beta * error
            phase += freq + alpha * error
        
        return output
    
    def _gardner_timing(self, signal: np.ndarray, sps: int):
        """Gardner timing error detector for symbol synchronization."""
        symbols = []
        indices = []
        mu = 0.0       # Fractional timing offset
        gain = 0.05    # Loop gain
        
        idx = sps  # Start at second symbol
        while idx < len(signal) - sps:
            i = int(idx)
            symbols.append(signal[i])
            indices.append(i)
            
            # Gardner TED: e(n) = x(n-1/2) * [x(n) - x(n-1)]
            mid = int(idx - sps // 2)
            prev = int(idx - sps)
            if prev >= 0 and mid >= 0:
                error = signal[mid] * (signal[i] - signal[prev])
                mu = gain * error
            
            idx += sps + mu
        
        return np.array(symbols), np.array(indices)
    
    def _estimate_symbol_rate(self, iq_signal: np.ndarray, fs: float) -> float:
        """Estimate symbol rate from spectral analysis of squared signal."""
        squared = iq_signal ** 2
        fft = np.abs(np.fft.fft(squared[:min(len(squared), 65536)]))
        freqs = np.fft.fftfreq(len(fft), d=1.0/fs)
        
        positive = freqs > 0
        peak_idx = np.argmax(fft[positive])
        return float(freqs[positive][peak_idx])
