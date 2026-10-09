# System Architecture

## 1. High-Level Architecture
SignalForge uses a layered, modular architecture separating the GUI layer from the DSP and ML backend.
- **Frontend**: PyQt6 for desktop UI.
- **Backend**: Pure Python utilizing NumPy, SciPy, and scikit-learn.

## 2. System Pipeline
The application follows a strict 5-stage processing pipeline:
1. **Stage 1 (File Ingest)**: Read `.wav` (PCM) and `.IQ` (binary). Convert to `complex64` array.
2. **Stage 2 (Analysis)**: Calculate FFT, PSD, Spectrogram. Run Random Forest ML classifier for modulation recognition based on 6 statistical features.
3. **Stage 3 (Demodulation)**: Apply specific demodulator (FSK via frequency discriminator; PSK via Costas loop and RRC filter) to extract symbol stream and bit array.
4. **Stage 4 (De-Interleaving)**: Matrix-based restructuring based on user-provided parameters (Block, Convolutional).
5. **Stage 5 (FEC & Bitstream)**: Error correction (Viterbi, RS) via `commpy`. Output to Hex viewer for sync word correlation.

## 3. Directory Structure
```
signalforge/
├── models/             # Pre-trained ML (.pkl files)
├── data/               # Sample ground-truth signals
├── src/
│   ├── core/           # Backend Engine
│   │   ├── demodulators/
│   │   ├── deinterleave/
│   │   ├── fec/
│   │   └── pipeline.py # Orchestrator
│   ├── gui/            # PyQt6 Layer
│   │   ├── widgets/
│   │   └── threads/    # QThread workers
│   └── utils/
└── run.py              # Entry point
```

## 4. Concurrency Model
To prevent blocking the PyQt6 event loop during heavy DSP calculations, all backend pipeline execution is offloaded to background threads using `QThread`. Communication between the DSP engine and GUI is handled entirely via `pyqtSignal` events.
