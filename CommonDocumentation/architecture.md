# SignalForge — System Architecture

---

## Overview

SignalForge is a **desktop GUI application** built with Python + PyQt6. It follows a **layered automation pipeline** architecture — fully automated where reliable, user-assisted where blind automation is not yet trustworthy.

---

## High-Level Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                       SignalForge GUI (PyQt6)                          │
│                                                                        │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ File Load  │  │ Spectrum + │  │ Constellation│  │ Bit Stream    │  │
│  │ Panel      │  │ Waterfall  │  │ Plot         │  │ Hex Viewer    │  │
│  │            │  │ Tabs       │  │              │  │ + Search      │  │
│  └─────┬──────┘  └─────▲──────┘  └──────▲───────┘  └──────▲────────┘  │
│        │               │               │                  │           │
│  ┌─────┴───────────────┴───────────────┴──────────────────┴────────┐  │
│  │                    Backend Engine (Python)                       │  │
│  │  Ingest → PSD → ML Classify → Demod → De-Interl → FEC → Bits   │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  STAGE 1    │────▶│  STAGE 2     │────▶│  STAGE 3     │────▶│  STAGE 4     │────▶│  STAGE 5     │
│  File Load  │     │  Visualize & │     │  Demodulate  │     │  De-interl.  │     │  FEC Decode  │
│  & Parse    │     │  Param ID    │     │              │     │  (with known │     │  & Bit View  │
│             │     │              │     │              │     │   params)    │     │              │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
   FULLY AUTO          AUTO + GUI           AUTO-SELECT          USER-ASSISTED         LIBRARY-BASED
```

---

## Stage Details

### Stage 1 — File Ingest (Fully Automated)

| Format | Parsing Method | Output |
|--------|---------------|--------|
| `.wav` | `scipy.io.wavfile.read()` — PCM samples + sample rate from header. Hilbert transform applied if signal is real-valued. | NumPy `complex64` array + metadata dict |
| `.IQ` | `np.fromfile()` — user selects format from dropdown (float32, int16, complex64, interleaved/non-interleaved). Preview of first few hundred samples shown for verification. | NumPy `complex64` array + metadata dict |

> `.IQ` files have no standard header — auto-detection is unreliable. User selects format via dropdown. This is intentional.

**Output of Stage 1:** `complex64` NumPy array + metadata dict `{sample_rate, duration, n_samples}`

---

### Stage 2 — Signal Parameter Identification (Auto + GUI)

| Parameter | Method |
|-----------|--------|
| **Sampling Frequency** | From `.wav` header (auto); user-provided for `.IQ` |
| **Power Spectral Density** | Welch method — `scipy.signal.welch` |
| **Bandwidth** | −3 dB / −10 dB threshold on spectral envelope |
| **Modulation Type** | Random Forest classifier on 6 statistical features (scikit-learn) |
| **Constellation Diagram** | I vs Q scatter plot after timing recovery (visualization only) |

**ML Feature Set (6 features):**
- `σ(|a(t)|)` — std dev of instantaneous amplitude
- `κ(|a(t)|)` — kurtosis of instantaneous amplitude
- `σ(φ(t))` — std dev of instantaneous phase
- `σ(f(t))` — std dev of instantaneous frequency
- `γ_max` — max value of spectral power density
- `R_zc` — zero-crossing rate

**Supported Modulation Types:** BPSK, QPSK, 2FSK, 4FSK, AM-DSB, FM, 8PSK

---

### Stage 3 — Demodulation (Auto-Select with Override)

| Modulation | Demodulation Method | Status |
|-----------|--------------------|----|
| **2FSK / 4FSK** | Frequency discriminator → LPF → symbol timing recovery (zero-crossing) → bit slicer | MVP |
| **BPSK** | Costas loop → RRC matched filter (`commpy.filters.rrcosfilter`) → M&M timing recovery → hard-decision | MVP |
| **QPSK** | Same as BPSK + phase ambiguity handling | MVP |
| **16-QAM** | CMA blind equalization + decision-directed | Stretch goal |

**Output:** Hard-decision bit stream + constellation plot

---

### Stage 4 — De-Interleaving (User-Assisted)

> Blind detection of interleaving type/parameters from a raw bit stream is an open research problem. SignalForge does NOT claim to auto-detect — user provides parameters.

| Type | Implementation | User Input |
|------|---------------|-----------|
| **Block** | `numpy.reshape + transpose` | Block size |
| **Convolutional** | Shift-register inverse | Depth, span |
| **Diagonal** | Row-column reversal | Parameters |
| **Pseudo-Random** | Inverse LFSR permutation | LFSR polynomial |

---

### Stage 5 — FEC Decoding & Bit Stream Viewer (Library-Based)

| FEC Type | Library | User Input | Status |
|----------|---------|-----------|--------|
| **Viterbi** (convolutional) | `commpy.channelcoding.convcode` | Constraint length K=3–7, code rate 1/2 or 1/3 | MVP |
| **Reed-Solomon** | `commpy` / `reedsolo` | (n, k) parameters | MVP |
| **LDPC** | `commpy` (limited) | — | Stretch goal |
| **Concatenated** | Chain RS + Viterbi | — | Future scope |

**Bit Stream Viewer:**
- Hex dump display of decoded bits
- Sync word search via `numpy.correlate` (cross-correlation)
- User inputs known sync word → highlights matches

---

## Module Map

```
signalforge/
├── main.py                  # Entry point, PyQt6 app init
├── gui/
│   ├── main_window.py       # Main QMainWindow layout
│   ├── file_panel.py        # File load + format selector
│   ├── spectrum_tab.py      # FFT spectrum + waterfall (PyQtGraph)
│   ├── constellation_tab.py # I/Q scatter plot (Matplotlib)
│   └── bitstream_viewer.py  # Hex dump + sync word search
├── backend/
│   ├── ingest.py            # .wav and .IQ file parsing
│   ├── spectral.py          # PSD, bandwidth estimation
│   ├── classifier.py        # Feature extraction + RF classifier
│   ├── demodulators/
│   │   ├── fsk.py           # FSK frequency discriminator
│   │   ├── psk.py           # BPSK/QPSK Costas loop + M&M
│   │   └── qam.py           # QAM CMA (stretch goal)
│   ├── deinterleaver.py     # Block/Conv/Diag/PR de-interleaving
│   └── fec/
│       ├── viterbi.py       # Convolutional + Viterbi wrapper
│       ├── reed_solomon.py  # RS decoder wrapper
│       └── ldpc.py          # LDPC (stretch goal)
├── models/
│   └── rf_classifier.pkl    # Pre-trained Random Forest (joblib)
└── requirements.txt
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.10+ | DSP/ML ecosystem, rapid dev |
| **GUI** | PyQt6 | Desktop widget framework |
| **DSP** | NumPy + SciPy | FFT, filtering, Welch PSD, Hilbert transform |
| **Plotting** | Matplotlib + PyQtGraph | Static plots + interactive waterfall |
| **ML** | scikit-learn | Random Forest classifier |
| **Demod / FEC** | commpy | Viterbi, RS, RRC filter, channel coding |
| **IQ Parsing** | `np.fromfile` | Raw binary read |
| **Model Persistence** | joblib | Save/load trained RF model |

---

## Data Flow

```
File (.wav/.IQ)
      │
      ▼
[Ingest] → complex64 NumPy array + {sample_rate, duration, n_samples}
      │
      ▼
[Spectral] → PSD (Welch) → spectrum plot, waterfall, bandwidth estimate
      │
      ▼
[Classifier] → 6-feature vector → RF model → modulation type + confidence
      │
      ▼
[Demodulator] → bit stream (hard decisions)
      │
      ▼
[De-Interleaver] → reordered bit stream (user-provided params)
      │
      ▼
[FEC Decoder] → decoded payload bits
      │
      ▼
[Bit Viewer] → hex dump + sync word search
```

---

## Hardware Requirements

| Level | Spec |
|-------|------|
| **Minimum** | Python 3.10+, 4 GB RAM, any OS |
| **Recommended** | 8 GB RAM for large `.IQ` files (>100 MB) |
| **Not required** | GPU, SDR hardware, internet connection |

---

## Python Dependencies

```
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
PyQt6>=6.5
pyqtgraph>=0.13
scikit-learn>=1.3
commpy>=0.7
reedsolo>=1.7
```

All are pure-Python or pre-built wheels — no compilation step required.
