import numpy as np
from typing import Tuple

def viterbi_decode(bits: np.ndarray, 
                   constraint_length: int = 7,
                   code_rate_inv: int = 2,
                   generator_polys: Tuple[int, ...] = (0o171, 0o133)) -> np.ndarray:
    """
    Viterbi decoder for convolutional codes using commpy.
    
    Args:
        bits: Encoded bit stream
        constraint_length: Constraint length K (3-7)
        code_rate_inv: Inverse of code rate (2 for rate 1/2, 3 for rate 1/3)
        generator_polys: Generator polynomials in octal
    
    Returns:
        Decoded bit stream
    """
    try:
        from commpy.channelcoding import Trellis, viterbi_decode as commpy_viterbi
        
        # Build trellis
        memory = np.array([constraint_length - 1])
        g_matrix = np.array([list(generator_polys)])
        trellis = Trellis(memory, g_matrix)
        
        # Ensure bits length is a multiple of code_rate_inv
        trim = len(bits) % code_rate_inv
        if trim != 0:
            bits = bits[:len(bits) - trim]
        
        # Decode (hard decision)
        decoded = commpy_viterbi(bits.astype(float), trellis, decoding_type='hard')
        
        return decoded.astype(np.int8)
    
    except ImportError:
        raise ImportError(
            "commpy is required for Viterbi decoding. "
            "Install it with: pip install scikit-commpy"
        )
