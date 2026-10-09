import numpy as np
from scipy.signal import welch, spectrogram
from dataclasses import dataclass

@dataclass
class SpectralResult:
    """Container for spectral analysis outputs."""
    freqs_fft: np.ndarray
    fft_magnitude: np.ndarray          # dB
    freqs_psd: np.ndarray
    psd: np.ndarray                    # dB
    spectrogram_times: np.ndarray
    spectrogram_freqs: np.ndarray
    spectrogram_power: np.ndarray      # dB
    bandwidth_3db: float               # Hz
    bandwidth_10db: float              # Hz
    center_frequency: float            # Hz (estimated)
    peak_frequency: float              # Hz


def analyze_spectrum(samples: np.ndarray, fs: float,
                     fft_size: int = 4096,
                     psd_nperseg: int = 2048,
                     spec_nperseg: int = 256) -> SpectralResult:
    """
    Full spectral analysis pipeline.
    
    Args:
        samples: Complex64 IQ samples
        fs: Sample rate (Hz)
        fft_size: FFT length
        psd_nperseg: PSD segment length (Welch method)
        spec_nperseg: Spectrogram segment length
    """
    # ── FFT ──
    N = min(fft_size, len(samples))
    windowed = samples[:N] * np.hanning(N)
    fft_result = np.fft.fftshift(np.fft.fft(windowed, n=fft_size))
    freqs_fft = np.fft.fftshift(np.fft.fftfreq(fft_size, d=1.0/fs))
    fft_mag_db = 20.0 * np.log10(np.abs(fft_result) + 1e-12)
    
    # ── PSD (Welch) ──
    freqs_psd, psd_raw = welch(samples, fs=fs, 
                                nperseg=min(psd_nperseg, len(samples)),
                                return_onesided=False)
    psd_db = 10.0 * np.log10(np.abs(psd_raw) + 1e-12)
    
    # ── Spectrogram ──
    spec_freqs, spec_times, Sxx = spectrogram(
        samples, fs=fs,
        nperseg=min(spec_nperseg, len(samples)),
        noverlap=min(spec_nperseg, len(samples)) // 2,
        return_onesided=False
    )
    spec_db = 10.0 * np.log10(np.abs(Sxx) + 1e-12)
    
    # ── Bandwidth estimation ──
    peak_idx = np.argmax(psd_db)
    peak_power = psd_db[peak_idx]
    peak_freq = float(freqs_psd[peak_idx])
    
    # -3 dB bandwidth
    bw3_mask = psd_db >= (peak_power - 3.0)
    bw3_freqs = freqs_psd[bw3_mask]
    bw_3db = float(bw3_freqs[-1] - bw3_freqs[0]) if len(bw3_freqs) > 1 else 0.0
    
    # -10 dB bandwidth
    bw10_mask = psd_db >= (peak_power - 10.0)
    bw10_freqs = freqs_psd[bw10_mask]
    bw_10db = float(bw10_freqs[-1] - bw10_freqs[0]) if len(bw10_freqs) > 1 else 0.0
    
    # Center frequency estimate
    weighted_freqs = freqs_psd * (10 ** (psd_db / 10.0))
    center_freq = float(np.sum(weighted_freqs) / np.sum(10 ** (psd_db / 10.0)))
    
    return SpectralResult(
        freqs_fft=freqs_fft,
        fft_magnitude=fft_mag_db,
        freqs_psd=freqs_psd,
        psd=psd_db,
        spectrogram_times=spec_times,
        spectrogram_freqs=spec_freqs,
        spectrogram_power=spec_db,
        bandwidth_3db=bw_3db,
        bandwidth_10db=bw_10db,
        center_frequency=center_freq,
        peak_frequency=peak_freq
    )
