import numpy as np
from scipy.io import wavfile
import os

def generate_bpsk(num_symbols=1000, sps=8, snr_db=15):
    bits = np.random.randint(0, 2, num_symbols)
    symbols = 2 * bits - 1
    # Pulse shaping (rect)
    signal = np.repeat(symbols, sps).astype(np.complex64)
    # Add noise
    noise_pwr = 10**(-snr_db/10)
    noise = np.sqrt(noise_pwr/2) * (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal)))
    return bits, signal + noise

def generate_qpsk(num_symbols=1000, sps=8, snr_db=15):
    bits = np.random.randint(0, 2, num_symbols * 2)
    i_bits = bits[0::2]
    q_bits = bits[1::2]
    symbols = (2 * i_bits - 1) + 1j * (2 * q_bits - 1)
    symbols /= np.sqrt(2) # Normalize power
    
    signal = np.repeat(symbols, sps).astype(np.complex64)
    noise_pwr = 10**(-snr_db/10)
    noise = np.sqrt(noise_pwr/2) * (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal)))
    return bits, signal + noise

def generate_16qam(num_symbols=1000, sps=8, snr_db=25):
    bits = np.random.randint(0, 2, num_symbols * 4)
    # Map to +/-1, +/-3
    levels = np.array([-3, -1, 1, 3]) / np.sqrt(10)
    i_idx = bits[0::4]*2 + bits[1::4]
    q_idx = bits[2::4]*2 + bits[3::4]
    
    symbols = levels[i_idx] + 1j * levels[q_idx]
    
    signal = np.repeat(symbols, sps).astype(np.complex64)
    noise_pwr = 10**(-snr_db/10)
    noise = np.sqrt(noise_pwr/2) * (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal)))
    return bits, signal + noise

def generate_fsk(num_symbols=1000, sps=8, snr_db=15, levels=2, modulation_index=0.5):
    bits_per_sym = int(np.log2(levels))
    bits = np.random.randint(0, 2, num_symbols * bits_per_sym)
    
    # Map bits to symbols [-M+1, ..., M-1]
    if levels == 2:
        symbols = 2 * bits - 1
    elif levels == 4:
        idx = bits[0::2]*2 + bits[1::2]
        sym_map = np.array([-3, -1, 1, 3])
        symbols = sym_map[idx]
        
    signal = np.zeros(num_symbols * sps, dtype=np.complex64)
    phase = 0.0
    
    # Continuous Phase FSK
    idx = 0
    for sym in symbols:
        freq_dev = sym * modulation_index / 2.0
        for _ in range(sps):
            signal[idx] = np.exp(1j * phase)
            phase += 2 * np.pi * freq_dev / sps
            idx += 1
            
    noise_pwr = 10**(-snr_db/10)
    noise = np.sqrt(noise_pwr/2) * (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal)))
    return bits, signal + noise

def save_wav(filename, signal, fs=100000):
    # Normalize and convert to float32 WAV (stereo = I/Q)
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val
        
    stereo = np.vstack((np.real(signal), np.imag(signal))).T
    wavfile.write(filename, fs, stereo.astype(np.float32))

def save_iq(filename, signal):
    # Save as interleaved float32 binary
    interleaved = np.empty(signal.size * 2, dtype=np.float32)
    interleaved[0::2] = np.real(signal)
    interleaved[1::2] = np.imag(signal)
    interleaved.tofile(filename)

if __name__ == "__main__":
    out_dir = "data/test_signals"
    os.makedirs(out_dir, exist_ok=True)
    
    # BPSK
    for snr in [5, 10, 15, 30]:
        bits, sig = generate_bpsk(snr_db=snr)
        save_wav(f"{out_dir}/bpsk_{snr}db.wav", sig)
        np.save(f"{out_dir}/bpsk_{snr}db_bits.npy", bits)
        
    # QPSK
    for snr in [10, 20, 30]:
        bits, sig = generate_qpsk(snr_db=snr)
        save_wav(f"{out_dir}/qpsk_{snr}db.wav", sig)
        np.save(f"{out_dir}/qpsk_{snr}db_bits.npy", bits)
        
    # 16QAM (needs high SNR to look good)
    for snr in [20, 30, 40]:
        bits, sig = generate_16qam(snr_db=snr)
        save_iq(f"{out_dir}/qam16_{snr}db.iq", sig) # Save as raw IQ
        np.save(f"{out_dir}/qam16_{snr}db_bits.npy", bits)

    # 2FSK
    for snr in [10, 20]:
        bits, sig = generate_fsk(levels=2, snr_db=snr)
        save_iq(f"{out_dir}/fsk2_{snr}db.iq", sig)
        np.save(f"{out_dir}/fsk2_{snr}db_bits.npy", bits)
        
    # 4FSK
    for snr in [15, 30]:
        bits, sig = generate_fsk(levels=4, snr_db=snr)
        save_wav(f"{out_dir}/fsk4_{snr}db.wav", sig)
        np.save(f"{out_dir}/fsk4_{snr}db_bits.npy", bits)
        
    print(f"Generated a massive variety of synthetic signals in {out_dir}")
