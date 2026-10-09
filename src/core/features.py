import numpy as np
from scipy.signal import welch

def extract_features(iq_signal: np.ndarray, fs: float = 1.0) -> np.ndarray:
    """
    Extract 6 statistical features for modulation classification.
    
    Args:
        iq_signal: Complex64 numpy array of IQ samples
        fs: Sampling frequency (Hz)
    
    Returns:
        Feature vector [6,]
    """
    # Instantaneous amplitude, phase, frequency
    amplitude = np.abs(iq_signal)
    phase = np.unwrap(np.angle(iq_signal))
    frequency = np.diff(phase) / (2.0 * np.pi) * fs
    
    # Feature 1: Std dev of instantaneous amplitude
    sigma_a = np.std(amplitude)
    
    # Feature 2: Kurtosis of instantaneous amplitude
    mean_a = np.mean(amplitude)
    kurtosis_a = np.mean((amplitude - mean_a) ** 4) / (np.std(amplitude) ** 4 + 1e-12)
    
    # Feature 3: Std dev of instantaneous phase
    sigma_phi = np.std(phase)
    
    # Feature 4: Std dev of instantaneous frequency
    sigma_f = np.std(frequency)
    
    # Feature 5: Max spectral power density
    freqs, psd = welch(iq_signal, fs=fs, nperseg=min(256, len(iq_signal)))
    gamma_max = np.max(np.abs(psd))
    
    # Feature 6: Zero-crossing rate
    real_part = np.real(iq_signal)
    zc = np.sum(np.abs(np.diff(np.sign(real_part)))) / (2.0 * len(real_part))
    
    return np.array([sigma_a, kurtosis_a, sigma_phi, sigma_f, gamma_max, zc])
