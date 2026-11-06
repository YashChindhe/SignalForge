import numpy as np
from scipy.signal import butter, lfilter
from .base import BaseDemodulator, DemodResult
from typing import Optional

class FSKDemodulator(BaseDemodulator):
    """2FSK / 4FSK frequency discriminator demodulator."""
    
    def __init__(self, num_levels: int = 2):
        """
        Args:
            num_levels: 2 for 2FSK, 4 for 4FSK
        """
        self.num_levels = num_levels
    
    @property
    def name(self) -> str:
        return f"{self.num_levels}FSK"
    
    def demodulate(self, iq_signal: np.ndarray, fs: float,
                   symbol_rate: Optional[float] = None) -> DemodResult:
        """
        FSK demodulation via frequency discriminator.
        """
        # Step 1: Instantaneous frequency
        phase = np.unwrap(np.angle(iq_signal))
        inst_freq = np.diff(phase) / (2.0 * np.pi) * fs
        
        # Step 2: Low-pass filter (cutoff at ~symbol_rate if known)
        if symbol_rate is None:
            symbol_rate = self._estimate_symbol_rate(inst_freq, fs)
        
        cutoff = symbol_rate * 0.8  # LPF cutoff
        nyq = fs / 2.0
        if cutoff < nyq:
            b, a = butter(4, cutoff / nyq, btype='low')
            inst_freq_filtered = lfilter(b, a, inst_freq)
        else:
            inst_freq_filtered = inst_freq
        
        # Step 3: Symbol timing — sample at symbol centers
        samples_per_symbol = int(fs / symbol_rate)
        if samples_per_symbol < 1:
            samples_per_symbol = 1
        
        symbol_indices = np.arange(
            samples_per_symbol // 2, 
            len(inst_freq_filtered), 
            samples_per_symbol
        ).astype(int)
        symbol_values = inst_freq_filtered[symbol_indices]
        
        # Step 4: Bit slicing
        if self.num_levels == 2:
            # 2FSK: threshold at median
            threshold = np.median(symbol_values)
            bits = (symbol_values > threshold).astype(np.int8)
        else:
            # 4FSK: 2 bits per symbol, use 3 thresholds
            sorted_vals = np.sort(symbol_values)
            thresholds = [
                np.percentile(sorted_vals, 25),
                np.percentile(sorted_vals, 50),
                np.percentile(sorted_vals, 75)
            ]
            bits = []
            for sv in symbol_values:
                if sv < thresholds[0]:
                    bits.extend([0, 0])
                elif sv < thresholds[1]:
                    bits.extend([0, 1])
                elif sv < thresholds[2]:
                    bits.extend([1, 0])
                else:
                    bits.extend([1, 1])
            bits = np.array(bits, dtype=np.int8)
        
        constellation_I = symbol_values
        constellation_Q = np.zeros_like(symbol_values)
        
        return DemodResult(
            bits=bits,
            symbols=symbol_values + 0j,
            constellation_I=constellation_I,
            constellation_Q=constellation_Q,
            symbol_rate=symbol_rate,
            num_symbols=len(symbol_values)
        )
    
    def _estimate_symbol_rate(self, inst_freq: np.ndarray, fs: float) -> float:
        """Estimate symbol rate from autocorrelation of instantaneous frequency."""
        x = inst_freq - np.mean(inst_freq)
        corr = np.correlate(x[:min(len(x), 10000)], x[:min(len(x), 10000)], mode='full')
        corr = corr[len(corr)//2:]  # Positive lags only
        
        min_lag = max(2, int(fs / (fs / 2)))  # At least 2 samples
        if len(corr) > min_lag + 10:
            peak_idx = min_lag + np.argmax(corr[min_lag:min(len(corr), min_lag + int(fs))])
            return fs / peak_idx
        
        return fs / 10  # Fallback
