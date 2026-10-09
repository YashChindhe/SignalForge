# SignalForge — Project Memory & Key Decisions

> This document captures critical design decisions, honest constraints, and rationale so any team member or AI agent working on this project understands **why** things are built the way they are. Do not override these decisions without discussion.

---

## Project Context

- **Competition**: Smart India Hackathon (SIH) 2026
- **Problem ID**: 26147
- **Organization**: National Technical Research Organisation (NTRO)
- **Category**: Software — Space Technology theme
- **Project Name**: SignalForge — Automated Signal Analysis Workbench
- **Format**: 36-hour hackathon
- **Team Size**: 6 members (3 parallel tracks: GUI, DSP, ML+FEC)

---

## Core Design Decisions

### 1. Random Forest, Not CNN

**Decision**: Use a Random Forest classifier on 6 hand-crafted statistical features, NOT a CNN/LSTM on raw IQ samples.

**Why**:
- RF is trainable in ~5 minutes on a laptop (pre-hackathon)
- No GPU, no CUDA, no dependency hell
- Interpretable — can explain why it chose a modulation type
- ~75-85% accuracy at SNR ≥ 5 dB on target modulation types — honest and demonstrable
- CNN sounds impressive but is fragile to deploy correctly under hackathon pressure

**Stretch goal only**: A simple 1D-CNN may be trained if time permits — but RF is the workhorse.

---

### 2. No .IQ Format Auto-Detection

**Decision**: We do NOT auto-detect `.IQ` file format. User selects from dropdown (float32 / int16 / complex64).

**Why**:
- Raw bytes have no reliable way to distinguish float32 from int16 without metadata
- Attempting auto-detection gives false confidence and silently corrupts the pipeline
- A dropdown with a preview window is honest, fast, and user-friendly

---

### 3. No Blind De-Interleaving Detection

**Decision**: De-interleaving is ALWAYS user-assisted. User selects type (Block/Convolutional/Diagonal/Pseudo-Random) and provides parameters.

**Why**:
- Blind detection of interleaving type/parameters from a raw bit stream is an open research problem — not solvable in 36 hours
- Getting it wrong silently corrupts the entire downstream chain
- Better to be correct with user input than wrong with false automation

---

### 4. No Blind FEC Parameter Detection

**Decision**: FEC decoding (Viterbi, RS) is always user-provided parameters.

**Why**:
- Without knowing constraint length K, code rate, and polynomial, Viterbi cannot decode
- Without (n, k), Reed-Solomon cannot decode
- These parameters are known in operational contexts (the analyst has them)
- Viterbi and RS work perfectly with correct params — the library is reliable

---

### 5. Fully Offline Architecture

**Decision**: No internet, no cloud, no external API calls.

**Why**:
- NTRO is an intelligence organization — operational security is non-negotiable
- The tool must run on a standalone laptop in potentially air-gapped environments
- All processing is local: NumPy/SciPy/scikit-learn/commpy

---

### 6. PyQt6 (Not Web, Not Tkinter, Not PySimpleGUI)

**Decision**: PyQt6 for the desktop GUI.

**Why**:
- Mature widget library with excellent plotting integration (Matplotlib canvas + PyQtGraph)
- QThread support for non-blocking background computation
- Better than Tkinter for complex multi-tab layouts
- Team has prior experience

---

### 7. GNU Radio Excluded

**Decision**: GNU Radio is NOT part of the stack.

**Why**:
- Heavy installation, complex GR flowgraph development
- Slows down development time in a 36-hour sprint
- NumPy + SciPy + commpy cover everything we need

---

## Honest Accuracy Expectations (ML Classifier)

These numbers MUST be used whenever discussing accuracy — do not claim higher:

| SNR Range | Expected Accuracy | Notes |
|-----------|-----------------|-------|
| ≥ 10 dB | ~80–85% | Good separation |
| 5–10 dB | ~70–75% | FSK/PSK distinguishable; QAM variants blur |
| 0–5 dB | ~55–65% | AM/FM still OK; digital mods get confused |
| < 0 dB | ~35–45% | Near random — expected |

**Supported modulation types** (where classifier is reliable): BPSK, QPSK, 2FSK, 4FSK, AM-DSB, FM, 8PSK

---

## What We Will NOT Claim

These are firm boundaries — do not add features that claim to do these:

- ❌ Auto-detect `.IQ` file format
- ❌ Auto-detect interleaving type or parameters
- ❌ Auto-detect FEC code parameters
- ❌ 90%+ classification accuracy (honest range is 70–85% at reasonable SNR)
- ❌ Real-time processing of live SDR streams (file-based only)
- ❌ Blind QAM equalization in MVP (stretch goal)

---

## Tier System (What We Guarantee vs. Attempt)

### 🟢 Tier 1 — WILL Demo (Guaranteed)
- Load `.IQ` and `.wav` files
- Display FFT spectrum + waterfall spectrogram
- Show signal statistics (sample rate, duration, bandwidth)
- ML modulation classification with confidence score
- Constellation diagram
- FSK demodulation → bit stream output

### 🟡 Tier 2 — SHOULD Demo (High Confidence)
- BPSK / QPSK demodulation
- Viterbi decoder (user provides K and rate)
- Reed-Solomon decoder (user provides n, k)
- Block de-interleaving (user provides block size)
- Hex bit stream viewer with sync word search

### 🔴 Tier 3 — MAY Demo (Stretch Goals)
- 16-QAM demodulation (CMA equalization)
- Convolutional / diagonal / pseudo-random de-interleaving
- LDPC decoding
- Automated PDF report export

---

## Pre-Hackathon Checklist (Must Be Done Before Day 1)

- [ ] Download **RadioML 2018.01A** dataset (~2.5 GB HDF5)
- [ ] Extract 6 statistical features per sample
- [ ] Train Random Forest (100 trees, max_depth=20) → `rf_classifier.pkl`
- [ ] Validate on held-out set → record confusion matrix
- [ ] Prepare 5 known FSK recordings for FSK accuracy test
- [ ] Prepare 5 known PSK recordings for PSK accuracy test
- [ ] Prepare one known convolutional-coded signal for Viterbi test
- [ ] Set up dev environment with all pip dependencies on team laptops

---

## Team Track Allocation

| Track | Members | Responsibility |
|-------|---------|---------------|
| **GUI** | 2 | PyQt6 main window, file panel, spectrum/waterfall tabs, constellation tab, bit stream viewer |
| **DSP** | 2 | File parser, PSD/bandwidth, FSK demodulator, BPSK/QPSK demodulator, de-interleaving |
| **ML + FEC** | 2 | Feature extraction, RF classifier, GUI integration, Viterbi decoder, RS decoder, demo prep |

---

## Demo Performance Targets

| Metric | Target |
|--------|--------|
| File load → spectrum display | < 3 seconds |
| Modulation classification time | < 1 second |
| FSK classification accuracy | > 85% on 5 known files |
| PSK classification accuracy | > 75% on 5 known files |
| FSK demod → correct bit stream | Verified on 3 files |
| Viterbi decode | Works with known K on 1 test signal |

---

## Known Risks

| Challenge | Risk Level | Mitigation |
|-----------|-----------|-----------|
| ML classifier underperforms on real signals | High | GUI shows confidence + constellation; analyst can override |
| Timing recovery (symbol sync) is fragile | Medium | Gardner/M&M with manual symbol rate input as fallback |
| GUI integration takes longer than expected | Medium | GUI track starts Day 1 in parallel with backend |
| Large `.IQ` files (>1 GB) cause memory issues | Low | Process in chunks; load only visible window into RAM |

---

## Key Libraries & Their Roles

| Library | Role | Notes |
|---------|------|-------|
| `numpy` | Core math, array operations, file parsing | `np.fromfile` for IQ, `np.correlate` for sync search |
| `scipy` | Welch PSD, Hilbert transform, signal processing | `scipy.io.wavfile`, `scipy.signal.welch` |
| `matplotlib` | Spectrum + constellation plots | Embedded via `FigureCanvasQTAgg` |
| `pyqtgraph` | Interactive waterfall | Better performance than Matplotlib for real-time-like display |
| `PyQt6` | Desktop GUI framework | `QThread` for non-blocking ops |
| `scikit-learn` | Random Forest classifier | `joblib.dump/load` for model persistence |
| `commpy` | Viterbi decoder, RS decoder, RRC filter | `commpy.channelcoding.convcode`, `commpy.filters.rrcosfilter` |
| `reedsolo` | Reed-Solomon alternative | Fallback if commpy RS is insufficient |
| `joblib` | Model serialization | Save/load `rf_classifier.pkl` |

---

## References

1. **RadioML 2018.01A** — DeepSig Inc. — https://www.deepsig.ai/datasets
2. O'Shea et al. — _"Convolutional Radio Modulation Recognition Networks"_ (2016) — https://arxiv.org/abs/1602.04105
3. Nandi & Azzouz — _"Algorithms for Automatic Modulation Recognition"_ (1998) — DOI: 10.1109/26.660505
4. West & O'Shea — _"Deep Architectures for Modulation Recognition"_ (2017) — https://arxiv.org/abs/1712.00443
5. **CommPy** — https://github.com/veeresht/CommPy
6. **SigMF** (IQ file best practices) — https://github.com/sigmf/SigMF
