import numpy as np
from scipy.io import wavfile
from scipy.signal import hilbert
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class IQFormat(Enum):
    COMPLEX_FLOAT32 = "complex64"       # 2 x float32 interleaved
    COMPLEX_FLOAT64 = "complex128"      # 2 x float64 interleaved
    INTERLEAVED_INT16 = "int16"         # I, Q as int16 pairs
    INTERLEAVED_FLOAT32 = "float32"     # I, Q as float32 pairs

@dataclass
class SignalData:
    """Unified signal container."""
    samples: np.ndarray           # Complex64 array
    sample_rate: float            # Hz
    duration: float               # Seconds
    num_samples: int
    source_format: str            # "wav" or "iq"
    filename: str
    
    @property
    def bandwidth_estimate(self) -> float:
        """Rough -3dB bandwidth from PSD."""
        from scipy.signal import welch
        freqs, psd = welch(self.samples, fs=self.sample_rate, 
                           nperseg=min(4096, len(self.samples)))
        psd_db = 10 * np.log10(np.abs(psd) + 1e-12)
        peak = np.max(psd_db)
        bw_mask = psd_db >= (peak - 3.0)
        bw_freqs = freqs[bw_mask]
        if len(bw_freqs) > 0:
            return float(bw_freqs[-1] - bw_freqs[0])
        return 0.0

def load_wav(filepath: str) -> SignalData:
    """
    Load a .wav file. Converts real-valued signals to analytic (complex)
    using the Hilbert transform.
    """
    sample_rate, data = wavfile.read(filepath)
    
    # Normalize to float
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    elif data.dtype != np.float32:
        data = data.astype(np.float32)
    
    # If stereo: channel 0 = I, channel 1 = Q
    if data.ndim == 2 and data.shape[1] == 2:
        samples = data[:, 0] + 1j * data[:, 1]
    else:
        # Mono — apply Hilbert transform for analytic signal
        if data.ndim == 2:
            data = data[:, 0]
        samples = hilbert(data).astype(np.complex64)
    
    samples = samples.astype(np.complex64)
    
    return SignalData(
        samples=samples,
        sample_rate=float(sample_rate),
        duration=len(samples) / float(sample_rate),
        num_samples=len(samples),
        source_format="wav",
        filename=filepath
    )

def load_iq(filepath: str, fmt: IQFormat, sample_rate: float) -> SignalData:
    """
    Load a raw .IQ binary file.
    
    Args:
        filepath: Path to .iq file
        fmt: Sample format (see IQFormat enum)
        sample_rate: User-provided sample rate in Hz
    """
    if fmt == IQFormat.COMPLEX_FLOAT32:
        raw = np.fromfile(filepath, dtype=np.complex64)
        samples = raw
        
    elif fmt == IQFormat.COMPLEX_FLOAT64:
        raw = np.fromfile(filepath, dtype=np.complex128)
        samples = raw.astype(np.complex64)
        
    elif fmt == IQFormat.INTERLEAVED_INT16:
        raw = np.fromfile(filepath, dtype=np.int16)
        raw = raw.astype(np.float32) / 32768.0
        samples = raw[0::2] + 1j * raw[1::2]
        samples = samples.astype(np.complex64)
        
    elif fmt == IQFormat.INTERLEAVED_FLOAT32:
        raw = np.fromfile(filepath, dtype=np.float32)
        samples = raw[0::2] + 1j * raw[1::2]
        samples = samples.astype(np.complex64)
    else:
        raise ValueError(f"Unknown IQ format: {fmt}")
    
    return SignalData(
        samples=samples,
        sample_rate=sample_rate,
        duration=len(samples) / sample_rate,
        num_samples=len(samples),
        source_format="iq",
        filename=filepath
    )
