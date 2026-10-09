# SignalForge — Development Phases & Hackathon Timeline

---

## Overview

Development is split into **two phases**:

1. **Pre-Hackathon Preparation** — ML model training, environment setup, codebase scaffolding
2. **Hackathon Execution** — 36 hours, 3 parallel tracks, 3 demo checkpoints

---

## Phase 0 — Pre-Hackathon Preparation (Before Day 1)

This phase is **critical**. The ML model must be trained before the hackathon begins — there is no time to train during the event.

### Tasks

| Task | Owner | Details |
|------|-------|---------|
| Download RadioML 2018.01A | ML Track | ~2.5 GB HDF5 file from https://www.deepsig.ai/datasets |
| Extract 6 statistical features | ML Track | σ(amp), κ(amp), σ(phase), σ(freq), γ_max, R_zc per sample |
| Train Random Forest | ML Track | 100 trees, max_depth=20, scikit-learn; ~5 min on laptop |
| Export model | ML Track | `joblib.dump(model, 'models/rf_classifier.pkl')` |
| Validate on held-out set | ML Track | Record confusion matrix; expected accuracy table |
| Prepare test signals | All | 5 FSK recordings, 5 PSK recordings, 1 Viterbi test signal |
| Environment setup | All | `pip install -r requirements.txt` on all team laptops |
| PyQt6 main window scaffold | GUI Track | Basic `QMainWindow` with sidebar + tab area (empty tabs OK) |
| Repo & folder structure | All | Create module structure: `gui/`, `backend/`, `models/` |

### Feature Extraction Details

```python
import numpy as np
from scipy.stats import kurtosis

def extract_features(iq_signal):
    amp = np.abs(iq_signal)
    phase = np.unwrap(np.angle(iq_signal))
    freq = np.diff(phase)
    fft = np.abs(np.fft.fft(iq_signal))
    psd = fft ** 2

    return [
        np.std(amp),          # σ(|a(t)|)
        kurtosis(amp),        # κ(|a(t)|)
        np.std(phase),        # σ(φ(t))
        np.std(freq),         # σ(f(t))
        np.max(psd),          # γ_max
        zero_crossing_rate(amp)  # R_zc
    ]
```

### Expected ML Accuracy (Locked — Do Not Over-Promise)

| SNR Range | Expected Accuracy |
|-----------|-----------------|
| ≥ 10 dB | ~80–85% |
| 5–10 dB | ~70–75% |
| 0–5 dB | ~55–65% |
| < 0 dB | ~35–45% |

---

## Phase 1 — Hackathon Hours 0–12 (Foundation)

**Goal**: First demo-able checkpoint — load a file and see spectrum + waterfall.

### Track Assignments

| Track | Members | Tasks |
|-------|---------|-------|
| **GUI** | 2 | File loader panel, spectrum plot tab (Matplotlib), waterfall tab (PyQtGraph) |
| **DSP** | 2 | `.wav` parser (`scipy.io.wavfile`), `.IQ` parser (`np.fromfile`), Welch PSD, bandwidth estimation |
| **ML+FEC** | 2 | Feature extraction pipeline, RF classifier load + inference, integrate classifier into sidebar |

### Milestone: Hour 12 Checkpoint ✅

> **Can load a `.wav` or `.IQ` file, display FFT spectrum + waterfall, and show signal statistics in the sidebar.**

Deliverables:
- [ ] File load dialog opens and reads `.wav` files correctly
- [ ] File load dialog handles `.IQ` with format dropdown + preview
- [ ] Spectrum tab shows PSD plot with frequency axis and bandwidth markers
- [ ] Waterfall tab shows spectrogram (time vs frequency, colored)
- [ ] Signal info panel shows: duration, sample count, estimated bandwidth
- [ ] ML `[Classify Modulation]` button runs classifier and shows result + confidence

---

## Phase 2 — Hackathon Hours 12–24 (Core Value)

**Goal**: Core value delivered — can classify modulation and demodulate FSK/BPSK.

### Track Assignments

| Track | Members | Tasks |
|-------|---------|-------|
| **GUI** | 2 | Constellation plot tab, parameter panel polish, modulation override dropdown |
| **DSP** | 2 | FSK demodulator (frequency discriminator + zero-crossing), BPSK demodulator (Costas loop + M&M) |
| **ML+FEC** | 2 | Integrate classifier output into demodulator selection, begin Viterbi wrapper |

### FSK Demodulator (DSP Track)

```python
import numpy as np

def demodulate_fsk(iq_signal, symbol_rate, sample_rate):
    # Instantaneous frequency via phase difference
    inst_freq = np.diff(np.unwrap(np.angle(iq_signal))) * sample_rate / (2 * np.pi)
    # Low-pass filter
    # Symbol timing recovery (zero-crossing)
    # Bit slicer
    ...
```

### BPSK Demodulator (DSP Track)

```python
# Costas loop → carrier recovery
# commpy.filters.rrcosfilter → matched filter
# Mueller & Müller → symbol timing
# Hard-decision mapping
```

### Milestone: Hour 24 Checkpoint ✅

> **Can classify modulation (RF model) and demodulate FSK and BPSK to produce a bit stream.**

Deliverables:
- [ ] `[Classify Modulation]` runs < 1 second, shows type + confidence
- [ ] Constellation tab updates after demodulation
- [ ] FSK demodulation produces bit stream (verified on test file)
- [ ] BPSK demodulation produces bit stream (verified on test file)
- [ ] Modulation type override dropdown works

---

## Phase 3 — Hackathon Hours 24–36 (Full Pipeline + Polish)

**Goal**: Full pipeline — FEC, de-interleaving, bit stream viewer. Final demo ready.

### Track Assignments

| Track | Members | Tasks |
|-------|---------|-------|
| **GUI** | 2 | Bit stream hex viewer, sync word search UI, overall polish + testing |
| **DSP** | 2 | QPSK demodulation, block de-interleaving module |
| **ML+FEC** | 2 | Viterbi decoder wrapper, Reed-Solomon decoder wrapper, demo prep |

### Viterbi Wrapper (ML+FEC Track)

```python
from commpy.channelcoding import convcode

def viterbi_decode(bits, constraint_length, code_rate):
    # commpy.channelcoding.viterbi_decode
    # User provides K (3–7) and rate (1/2 or 1/3)
    ...
```

### Block De-Interleaver (DSP Track)

```python
import numpy as np

def block_deinterleave(bits, block_size):
    rows = len(bits) // block_size
    matrix = np.array(bits[:rows * block_size]).reshape(rows, block_size)
    return matrix.T.flatten()
```

### Milestone: Hour 36 — Final Demo ✅

> **Full pipeline: file load → classify → demodulate → de-interleave → FEC decode → bit stream viewer with sync word search.**

Deliverables:
- [ ] QPSK demodulation working
- [ ] Viterbi decode (user-provided K and rate) working on test signal
- [ ] Reed-Solomon decode (user-provided n, k) working
- [ ] Block de-interleaving working
- [ ] Hex bit stream viewer displays decoded bits
- [ ] Sync word search highlights matches
- [ ] No GUI freezes during any operation (QThread workers in place)
- [ ] Demo script rehearsed on all Tier 1 + Tier 2 features

---

## Demo Script (Hour 36)

1. Open SignalForge
2. Load `test_qpsk.wav` → spectrum + waterfall appear
3. Click Classify → shows "QPSK (82%)" → constellation shows 4 clusters
4. Click Demodulate → bit stream generated
5. Load `test_fsk.iq` (float32, 1 MHz sample rate) → classify → "2FSK (91%)"
6. Demodulate → bit stream
7. Apply Block de-interleaving (block size = 64) → de-interleaved stream
8. Apply Viterbi decode (K=7, rate=1/2) → decoded payload
9. Show hex viewer → enter sync word `0xAA 0xBB` → highlight match
10. Show performance: classification < 1s, load < 3s

---

## Stretch Goals (If Time Permits After Hour 36)

| Feature | Effort | Value |
|---------|--------|-------|
| 16-QAM demodulation (CMA) | High | Medium |
| Convolutional de-interleaving | Medium | High |
| Pseudo-random de-interleaving | Medium | Medium |
| LDPC decoding | High | Low (complex, marginal gain) |
| PDF report export | Low | High (impressive demo feature) |

---

## Risk Mitigation During Hackathon

| Risk | Trigger | Action |
|------|---------|--------|
| ML accuracy is low on real signals | Confidence < 60% on test files | Emphasize GUI visual tools + analyst override; mention this is by design |
| Timing recovery fails | Demod produces garbage | Fall back to manual symbol rate input |
| GUI freezes | Heavy operation on main thread | Move to QThread worker immediately |
| Large `.IQ` file causes OOM | File > 500 MB | Implement chunked reading (`np.memmap`) |
| commpy install issues | Import error | Fall back to custom Viterbi (< 50 lines) |
