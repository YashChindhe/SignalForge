import numpy as np

def rs_decode(data: np.ndarray, nsym: int = 10, 
              n: int = 255, k: int = 223) -> np.ndarray:
    """
    Reed-Solomon decoder using reedsolo library.
    
    Args:
        data: Input byte array (packed bits -> bytes)
        nsym: Number of error-correction symbols (n - k)
        n: RS block length
        k: RS message length
    """
    try:
        from reedsolo import RSCodec
        
        rs = RSCodec(nsym)
        
        # Convert bits to bytes
        if data.dtype == np.int8 or data.max() <= 1:
            # Pack bits into bytes
            pad = (8 - len(data) % 8) % 8
            padded = np.concatenate([data, np.zeros(pad, dtype=data.dtype)])
            byte_data = np.packbits(padded)
        else:
            byte_data = data.astype(np.uint8)
        
        # Decode
        decoded_bytes = rs.decode(bytes(byte_data))
        
        # Unpack back to bits
        decoded_bits = np.unpackbits(np.frombuffer(decoded_bytes, dtype=np.uint8))
        
        return decoded_bits.astype(np.int8)
    
    except ImportError:
        raise ImportError(
            "reedsolo is required for Reed-Solomon decoding. "
            "Install it with: pip install reedsolo"
        )
