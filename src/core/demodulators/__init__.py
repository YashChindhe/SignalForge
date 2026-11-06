from .base import BaseDemodulator, DemodResult
from .fsk import FSKDemodulator
from .bpsk import BPSKDemodulator
from .qpsk import QPSKDemodulator
from .qam import QAM16Demodulator

DEMODULATOR_MAP = {
    "2FSK": lambda: FSKDemodulator(num_levels=2),
    "4FSK": lambda: FSKDemodulator(num_levels=4),
    "BPSK": lambda: BPSKDemodulator(),
    "QPSK": lambda: QPSKDemodulator(),
    "8PSK": lambda: QPSKDemodulator(),  # Reuse QPSK with modifications
    "16QAM": lambda: QAM16Demodulator(),
}

def get_demodulator(mod_type: str) -> BaseDemodulator:
    """Factory: return the appropriate demodulator for a modulation type."""
    if mod_type not in DEMODULATOR_MAP:
        raise ValueError(
            f"No demodulator for '{mod_type}'. "
            f"Supported: {list(DEMODULATOR_MAP.keys())}"
        )
    return DEMODULATOR_MAP[mod_type]()
