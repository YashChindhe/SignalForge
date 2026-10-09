import numpy as np
from typing import List, Tuple

def bits_to_hex(bits: np.ndarray) -> str:
    """Convert bit array to hex string."""
    pad = (8 - len(bits) % 8) % 8
    padded = np.concatenate([bits, np.zeros(pad, dtype=np.int8)])
    byte_vals = np.packbits(padded)
    return ' '.join(f'{b:02X}' for b in byte_vals)

def bits_to_hex_lines(bits: np.ndarray, bytes_per_line: int = 16) -> List[str]:
    """Format bits as hex dump with addresses."""
    pad = (8 - len(bits) % 8) % 8
    padded = np.concatenate([bits, np.zeros(pad, dtype=np.int8)])
    byte_vals = np.packbits(padded)
    
    lines = []
    for offset in range(0, len(byte_vals), bytes_per_line):
        chunk = byte_vals[offset:offset + bytes_per_line]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f'{offset:08X}  {hex_part:<{bytes_per_line * 3}}  |{ascii_part}|')
    
    return lines

def search_sync_word(bits: np.ndarray, 
                      sync_pattern: np.ndarray,
                      threshold: float = 0.9) -> List[int]:
    """
    Search for a sync word pattern in the bit stream using cross-correlation.
    
    Args:
        bits: Full bit stream
        sync_pattern: Known sync word as bit array
        threshold: Correlation threshold (0.0 to 1.0)
    
    Returns:
        List of bit positions where sync word is found
    """
    # Convert to +1/-1 for correlation
    signal = 2.0 * bits.astype(float) - 1.0
    pattern = 2.0 * sync_pattern.astype(float) - 1.0
    
    # Cross-correlate
    correlation = np.correlate(signal, pattern, mode='valid')
    normalized = correlation / len(pattern)
    
    # Find peaks above threshold
    positions = np.where(normalized >= threshold)[0]
    
    return positions.tolist()

def find_frame_structure(bits: np.ndarray, 
                          sync_positions: List[int]) -> List[Tuple[int, int]]:
    """
    Given sync word positions, identify frame boundaries.
    
    Returns:
        List of (start, length) tuples for each frame
    """
    frames = []
    for i in range(len(sync_positions) - 1):
        start = sync_positions[i]
        length = sync_positions[i + 1] - sync_positions[i]
        frames.append((start, length))
    
    # Last frame (to end of stream)
    if sync_positions:
        frames.append((sync_positions[-1], len(bits) - sync_positions[-1]))
    
    return frames
