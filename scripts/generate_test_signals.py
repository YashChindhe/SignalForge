import numpy as np
from scipy.io import wavfile
import os

def generate_bpsk_wav(filename, fs=48000, symbol_rate=1200, 
                       num_symbols=1000, snr_db=15):
    """Generate a BPSK .wav file with known bit pattern."""
    sps = int(fs / symbol_rate)
    
    # Known bit pattern (for verification)
    np.random.seed(42)
    bits = np.random.randint(0, 2, num_symbols)
    
    # BPSK modulation: 0 -> -1, 1 -> +1
    symbols = 2 * bits - 1
    
    # Upsample
    signal = np.repeat(symbols, sps).astype(np.float32)
    
    # Carrier
    t = np.arange(len(signal)) / fs
    carrier_freq = 5000  # 5 kHz carrier
    modulated = signal * np.cos(2 * np.pi * carrier_freq * t)
    
    # Add noise
    signal_power = np.mean(modulated ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_power) * np.random.randn(len(modulated))
    noisy = (modulated + noise).astype(np.float32)
    
    # Normalize
    noisy = noisy / np.max(np.abs(noisy)) * 0.9
    
    # Save
    wavfile.write(filename, fs, noisy)
    
    # Save ground truth bits
    np.save(filename.replace('.wav', '_bits.npy'), bits)
    
    print(f"Generated {filename}: {num_symbols} symbols, "
          f"SNR={snr_db} dB, SR={symbol_rate} sym/s")

def generate_fsk_iq(filename, fs=100000, symbol_rate=2400,
                     num_symbols=1000, snr_db=20, deviation=5000):
    """Generate a 2FSK .iq file (complex64 format)."""
    sps = int(fs / symbol_rate)
    
    np.random.seed(42)
    bits = np.random.randint(0, 2, num_symbols)
    
    # FSK: bit -> frequency
    freq_map = {0: -deviation, 1: +deviation}
    inst_freq = np.array([freq_map[b] for b in bits])
    inst_freq_upsampled = np.repeat(inst_freq, sps)
    
    # Phase integration
    phase = 2 * np.pi * np.cumsum(inst_freq_upsampled) / fs
    signal = np.exp(1j * phase).astype(np.complex64)
    
    # Add complex noise
    signal_power = np.mean(np.abs(signal) ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_power / 2) * (
        np.random.randn(len(signal)) + 1j * np.random.randn(len(signal))
    )
    noisy = (signal + noise).astype(np.complex64)
    
    # Save as raw IQ (float32 interleaved I, Q)
    # Using complex64 saves it exactly as float32 I, float32 Q
    noisy.tofile(filename)
    np.save(filename.replace('.iq', '_bits.npy'), bits)
    
    print(f"Generated {filename}: {num_symbols} symbols, "
          f"SNR={snr_db} dB, deviation={deviation} Hz")

if __name__ == "__main__":
    # Go up to the root project dir and make the data/test_signals folders
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(project_root, "data", "test_signals")
    os.makedirs(target_dir, exist_ok=True)
    
    # Generate test suite
    generate_bpsk_wav(os.path.join(target_dir, "bpsk_15db.wav"), snr_db=15)
    generate_bpsk_wav(os.path.join(target_dir, "bpsk_10db.wav"), snr_db=10)
    generate_bpsk_wav(os.path.join(target_dir, "bpsk_05db.wav"), snr_db=5)
    generate_fsk_iq(os.path.join(target_dir, "fsk2_20db.iq"), snr_db=20)
    generate_fsk_iq(os.path.join(target_dir, "fsk2_10db.iq"), snr_db=10)
    
    print("\n[SUCCESS] All test signals generated successfully.")
