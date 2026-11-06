import numpy as np
from .viterbi import viterbi_decode
from .reed_solomon import rs_decode

def concatenated_decode(bits: np.ndarray) -> np.ndarray:
    """
    Concatenated decoder (Viterbi inner + Reed-Solomon outer).
    Commonly used in deep space communications (CCSDS) and satellite TV (DVB-S).
    """
    print("Concatenated Decoder: Running Inner Viterbi...")
    # Step 1: Inner convolutional decode
    # Using default CCSDS rate 1/2 constraint 7
    inner_bits = viterbi_decode(bits)
    
    print("Concatenated Decoder: Running Outer Reed-Solomon...")
    # Step 2: Outer block decode
    # Assuming CCSDS standard RS(255, 223)
    outer_bits = rs_decode(inner_bits)
    
    return outer_bits
