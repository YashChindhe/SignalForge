import numpy as np

def convolutional_deinterleave(bits: np.ndarray, 
                                num_branches: int, 
                                delay: int) -> np.ndarray:
    """
    Convolutional de-interleaver (Forney/Ramsey type).
    
    Args:
        bits: Input bit stream
        num_branches: Number of branches (B)
        delay: Unit delay per branch (D)
    """
    output = np.zeros_like(bits)
    # Each branch i has delay (B - 1 - i) * D
    buffers = [np.zeros(max(0, (num_branches - 1 - i) * delay), dtype=bits.dtype)
               for i in range(num_branches)]
    
    out_idx = 0
    for n in range(len(bits)):
        branch = n % num_branches
        buf = buffers[branch]
        if len(buf) == 0:
            output[out_idx] = bits[n]
        else:
            output[out_idx] = buf[0]
            buf[:-1] = buf[1:]  # Shift
            buf[-1] = bits[n]
        out_idx += 1
    
    return output[:out_idx]
