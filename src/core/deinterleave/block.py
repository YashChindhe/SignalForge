import numpy as np

def block_deinterleave(bits: np.ndarray, rows: int, cols: int) -> np.ndarray:
    """
    Block de-interleaver.
    
    The interleaver wrote data row-by-row into a matrix, then read column-by-column.
    To reverse: write column-by-column, read row-by-row.
    
    Args:
        bits: Input bit stream (1D array)
        rows: Number of rows in interleaver matrix
        cols: Number of columns in interleaver matrix
    """
    block_size = rows * cols
    num_blocks = len(bits) // block_size
    
    output = np.zeros(num_blocks * block_size, dtype=bits.dtype)
    
    for b in range(num_blocks):
        block = bits[b * block_size : (b + 1) * block_size]
        # Write column-by-column into matrix, read row-by-row
        matrix = block.reshape(cols, rows).T  # Transpose reverses the interleaving
        output[b * block_size : (b + 1) * block_size] = matrix.flatten()
    
    return output
