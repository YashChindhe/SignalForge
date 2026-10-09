import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from .file_ingest import SignalData, load_wav, load_iq, IQFormat
from .spectral import SpectralResult, analyze_spectrum
from .classifier import ModulationClassifier, ClassificationResult
from .demodulators import get_demodulator, DemodResult
from .bitstream import bits_to_hex_lines, search_sync_word

@dataclass
class PipelineState:
    """Tracks the full pipeline state through all stages."""
    # Stage 1
    signal: Optional[SignalData] = None
    
    # Stage 2
    spectral: Optional[SpectralResult] = None
    classification: Optional[ClassificationResult] = None
    
    # Stage 3
    demod: Optional[DemodResult] = None
    
    # Stage 4
    deinterleaved_bits: Optional[np.ndarray] = None
    
    # Stage 5
    decoded_bits: Optional[np.ndarray] = None
    hex_dump: Optional[list] = None
    sync_positions: Optional[list] = None
    
    # Metadata
    current_stage: int = 0
    errors: Dict[int, str] = field(default_factory=dict)


class SignalForgePipeline:
    """Orchestrates the full Stage 1->5 signal analysis pipeline."""
    
    def __init__(self, model_path: str, scaler_path: str, encoder_path: str):
        self.classifier = None
        try:
            self.classifier = ModulationClassifier(model_path, scaler_path, encoder_path)
        except Exception as e:
            print(f"Warning: Could not load ML model: {e}")
        self.state = PipelineState()
    
    def stage1_load_file(self, filepath: str, 
                          iq_format: Optional[IQFormat] = None,
                          sample_rate: Optional[float] = None) -> SignalData:
        """Stage 1: File Ingest."""
        if filepath.lower().endswith('.wav'):
            self.state.signal = load_wav(filepath)
        elif filepath.lower().endswith('.iq') or iq_format is not None:
            if iq_format is None:
                raise ValueError("IQ format must be specified for .iq files")
            if sample_rate is None:
                raise ValueError("Sample rate must be specified for .iq files")
            self.state.signal = load_iq(filepath, iq_format, sample_rate)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")
        
        self.state.current_stage = 1
        return self.state.signal
    
    def stage2_analyze(self) -> tuple:
        """Stage 2: Spectral analysis + ML classification."""
        if self.state.signal is None:
            raise RuntimeError("Stage 1 (file load) must complete first")
        
        sig = self.state.signal
        
        # Spectral analysis
        self.state.spectral = analyze_spectrum(sig.samples, sig.sample_rate)
        
        # ML classification
        if self.classifier:
            self.state.classification = self.classifier.classify(
                sig.samples, sig.sample_rate
            )
        
        self.state.current_stage = 2
        return self.state.spectral, self.state.classification
    
    def stage3_demodulate(self, mod_type: Optional[str] = None,
                           symbol_rate: Optional[float] = None) -> DemodResult:
        """Stage 3: Demodulation."""
        if self.state.signal is None:
            raise RuntimeError("Stage 1 must complete first")
        
        # Use ML result if no override
        if mod_type is None:
            if self.state.classification is None:
                raise RuntimeError("Run Stage 2 first, or specify mod_type")
            mod_type = self.state.classification.predicted_mod
        
        demod = get_demodulator(mod_type)
        self.state.demod = demod.demodulate(
            self.state.signal.samples,
            self.state.signal.sample_rate,
            symbol_rate
        )
        
        self.state.current_stage = 3
        return self.state.demod
    
    def stage4_deinterleave(self, method: str, **params) -> np.ndarray:
        """Stage 4: De-interleaving (user-assisted)."""
        if self.state.demod is None:
            raise RuntimeError("Stage 3 must complete first")
        
        bits = self.state.demod.bits
        
        if method == "block":
            from .deinterleave.block import block_deinterleave
            self.state.deinterleaved_bits = block_deinterleave(
                bits, params['rows'], params['cols']
            )
        elif method == "convolutional":
            from .deinterleave.convolutional import convolutional_deinterleave
            self.state.deinterleaved_bits = convolutional_deinterleave(
                bits, params['num_branches'], params['delay']
            )
        else:
            raise ValueError(f"Unknown de-interleaving method: {method}")
        
        self.state.current_stage = 4
        return self.state.deinterleaved_bits
    
    def stage5_fec_decode(self, method: str, **params) -> np.ndarray:
        """Stage 5: FEC decoding."""
        bits = self.state.deinterleaved_bits
        if bits is None:
            bits = self.state.demod.bits if self.state.demod else None
        if bits is None:
            raise RuntimeError("No bits available for FEC decoding")
        
        if method == "viterbi":
            from .fec.viterbi import viterbi_decode
            self.state.decoded_bits = viterbi_decode(
                bits,
                constraint_length=params.get('constraint_length', 7),
                code_rate_inv=params.get('code_rate_inv', 2),
                generator_polys=params.get('generator_polys', (0o171, 0o133))
            )
        elif method == "reed_solomon":
            from .fec.reed_solomon import rs_decode
            self.state.decoded_bits = rs_decode(
                bits,
                nsym=params.get('nsym', 10)
            )
        else:
            raise ValueError(f"Unknown FEC method: {method}")
        
        # Generate hex dump
        self.state.hex_dump = bits_to_hex_lines(self.state.decoded_bits)
        
        self.state.current_stage = 5
        return self.state.decoded_bits
    
    def search_sync(self, sync_word_hex: str, threshold: float = 0.9) -> list:
        """Search for sync word in current bit stream."""
        bits = (self.state.decoded_bits if self.state.decoded_bits is not None
                else self.state.deinterleaved_bits if self.state.deinterleaved_bits is not None
                else self.state.demod.bits if self.state.demod is not None
                else None)
        
        if bits is None:
            raise RuntimeError("No bit stream available")
        
        # Convert hex to bit pattern
        sync_bytes = bytes.fromhex(sync_word_hex.replace(' ', ''))
        sync_bits = np.unpackbits(np.frombuffer(sync_bytes, dtype=np.uint8))
        
        self.state.sync_positions = search_sync_word(bits, sync_bits, threshold)
        return self.state.sync_positions
