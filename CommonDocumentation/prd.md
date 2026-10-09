# SignalForge — Product Requirements Document (PRD)

---

## 1. Product Overview

**Product Name**: SignalForge  
**Version**: 1.0 (SIH 2026 submission)  
**Type**: Desktop GUI application (offline, standalone)  
**Platform**: Windows / Linux (Python 3.10+)  
**Organization**: NTRO (National Technical Research Organisation)  
**Problem ID**: SIH 2026 — 26147

---

## 2. Problem Statement

Signal analysts at NTRO manually analyze `.IQ` and `.wav` files from HF, VHF, and UHF band recordings. This manual process is:

- **Slow** (30–60 min per file for spectrum + modulation ID)
- **Error-prone** (different analysts produce different results)
- **Insufficiently detailed** (misses fine-grain parameters like modulation type, FEC, interleaving)
- **Tool-fragmented** (no single tool handles .IQ parsing, visualization, demodulation, and FEC)

---

## 3. Goals & Non-Goals

### Goals

- Automate signal analysis workflow for `.IQ` and `.wav` files
- Provide rich visualization: spectrum, waterfall, constellation
- ML-based modulation classification with analyst-verifiable output
- Demodulation of FSK, BPSK, QPSK signals to bit stream
- Library-based FEC decoding (Viterbi, Reed-Solomon) with user-provided parameters
- User-assisted de-interleaving (Block, Convolutional, Diagonal, Pseudo-Random)
- Sync word / header search in decoded bit stream
- Fully offline, no network or cloud dependency

### Non-Goals

- ❌ Live SDR (Software Defined Radio) stream processing
- ❌ Automatic `.IQ` format detection
- ❌ Automatic interleaving type/parameter detection
- ❌ Automatic FEC parameter detection
- ❌ QAM blind equalization in MVP
- ❌ Web or mobile interface
- ❌ 90%+ ML accuracy claims

---

## 4. Users & Stakeholders

| Role | Description | Primary Need |
|------|------------|-------------|
| **Signal Analyst** | NTRO operator analyzing recorded signals | Fast spectrum view, modulation ID, demodulation |
| **Senior Analyst** | Reviews analyst findings | Reproducible results, reliable visualization |
| **Training Instructor** | Teaches junior analysts | Educational step-by-step pipeline view |
| **NTRO IT** | Deploys and maintains the tool | No external dependencies, pip-installable |

---

## 5. Functional Requirements

### FR-1: File Ingestion

| ID | Requirement | Priority |
|----|------------|---------|
| FR-1.1 | Load `.wav` files and auto-parse sample rate from header | P0 |
| FR-1.2 | Load `.IQ` files with user-selected format (float32, int16, complex64) | P0 |
| FR-1.3 | For `.IQ` files: require user to input sample rate (no auto-detect) | P0 |
| FR-1.4 | Show preview of first ~500 samples before confirming `.IQ` format | P1 |
| FR-1.5 | Apply Hilbert transform to real-valued `.wav` signals to produce complex baseband | P0 |
| FR-1.6 | Output a `complex64` NumPy array with metadata: `{sample_rate, duration, n_samples}` | P0 |

---

### FR-2: Signal Visualization

| ID | Requirement | Priority |
|----|------------|---------|
| FR-2.1 | Display FFT Power Spectral Density (Welch method) as spectrum plot | P0 |
| FR-2.2 | Display spectrogram (time vs frequency) as waterfall plot | P0 |
| FR-2.3 | Show signal statistics: duration, sample count, estimated bandwidth (−3 dB) | P0 |
| FR-2.4 | Display constellation diagram (I vs Q scatter) after timing recovery | P0 |
| FR-2.5 | Spectrum plot: label frequency axis; show bandwidth markers | P1 |
| FR-2.6 | Waterfall: support zoom and pan | P1 |

---

### FR-3: Modulation Classification

| ID | Requirement | Priority |
|----|------------|---------|
| FR-3.1 | Extract 6 statistical features from the signal | P0 |
| FR-3.2 | Run pre-trained Random Forest classifier on features | P0 |
| FR-3.3 | Display predicted modulation type with confidence score | P0 |
| FR-3.4 | Support classification for: BPSK, QPSK, 2FSK, 4FSK, AM-DSB, FM, 8PSK | P0 |
| FR-3.5 | Allow analyst to manually override the detected modulation type | P0 |
| FR-3.6 | Show warning if confidence < 50% | P1 |
| FR-3.7 | Classification must complete in < 1 second | P0 |

---

### FR-4: Demodulation

| ID | Requirement | Priority |
|----|------------|---------|
| FR-4.1 | Demodulate 2FSK using frequency discriminator method | P0 |
| FR-4.2 | Demodulate 4FSK using frequency discriminator with 4-level slicer | P1 |
| FR-4.3 | Demodulate BPSK using Costas loop + RRC filter + M&M timing recovery | P1 |
| FR-4.4 | Demodulate QPSK using same approach + phase ambiguity handling | P1 |
| FR-4.5 | Output hard-decision bit stream | P0 |
| FR-4.6 | Update constellation plot post-demodulation | P1 |
| FR-4.7 | Demodulate 16-QAM (CMA equalization) | P3 (stretch) |

---

### FR-5: De-Interleaving

| ID | Requirement | Priority |
|----|------------|---------|
| FR-5.1 | Apply Block de-interleaving with user-provided block size | P1 |
| FR-5.2 | Apply Convolutional de-interleaving with user-provided depth and span | P2 |
| FR-5.3 | Apply Diagonal de-interleaving | P2 |
| FR-5.4 | Apply Pseudo-Random de-interleaving with user-provided LFSR polynomial | P2 |
| FR-5.5 | User selects type and provides all parameters — no auto-detection | P0 (design constraint) |

---

### FR-6: FEC Decoding

| ID | Requirement | Priority |
|----|------------|---------|
| FR-6.1 | Viterbi decode with user-provided constraint length K (3–7) and code rate (1/2, 1/3) | P1 |
| FR-6.2 | Reed-Solomon decode with user-provided (n, k) parameters | P1 |
| FR-6.3 | LDPC decoding | P3 (stretch) |
| FR-6.4 | Concatenated code decoding | P4 (future scope) |
| FR-6.5 | Show number of uncorrected errors if FEC decode fails | P1 |

---

### FR-7: Bit Stream Viewer

| ID | Requirement | Priority |
|----|------------|---------|
| FR-7.1 | Display decoded bit stream as hex dump (16 bytes/row, offset + hex + ASCII) | P1 |
| FR-7.2 | Allow user to input sync word / header pattern | P1 |
| FR-7.3 | Highlight all matches of sync word in hex viewer using cross-correlation | P1 |

---

### FR-8: Non-Functional Requirements

| ID | Requirement | Priority |
|----|------------|---------|
| FR-8.1 | File load to spectrum display: < 3 seconds | P0 |
| FR-8.2 | Modulation classification: < 1 second | P0 |
| FR-8.3 | GUI must never freeze — all heavy operations run in QThread workers | P0 |
| FR-8.4 | No internet connection required at any point | P0 |
| FR-8.5 | No GPU required | P0 |
| FR-8.6 | Minimum hardware: Python 3.10+, 4 GB RAM | P0 |
| FR-8.7 | All dependencies installable via `pip install -r requirements.txt` | P0 |
| FR-8.8 | Runs on Windows and Linux | P1 |

---

## 6. Technical Constraints

- **Language**: Python 3.10+
- **GUI**: PyQt6
- **No GPU**: scikit-learn RF runs on CPU only
- **No SDR hardware**: file-based analysis only
- **No network**: fully air-gapped compatible
- **Dependencies**: numpy, scipy, matplotlib, pyqtgraph, PyQt6, scikit-learn, commpy, reedsolo

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| File load → spectrum display | < 3 seconds |
| Modulation classification time | < 1 second |
| FSK classification accuracy (test set) | > 85% |
| PSK classification accuracy (test set) | > 75% |
| FSK demod → verified correct bit stream | 3 of 3 test files |
| Viterbi decode | Correct on 1 known convolutional-coded signal |
| Zero GUI freezes during demo | All operations non-blocking |

---

## 8. Scope by Priority (P0 = Must Have, P3 = Stretch)

| Priority | Features |
|----------|---------|
| **P0** | File load (.wav + .IQ), spectrum + waterfall, signal stats, ML classification + confidence, FSK demodulation, bit stream output |
| **P1** | BPSK/QPSK demodulation, constellation plot, Viterbi decoder, RS decoder, block de-interleaving, hex viewer + sync word search |
| **P2** | Convolutional/diagonal/pseudo-random de-interleaving, 4FSK, 8PSK improved handling |
| **P3** | 16-QAM demodulation, LDPC decoding, PDF report export |
| **P4** | Concatenated codes, real-time SDR stream support |

---

## 9. Existing Tools Comparison

| Tool | What It Does | What SignalForge Adds |
|------|--------------|-----------------------|
| **Baudline** | Spectrum analyzer (proprietary) | Open-source + ML classification + demodulation |
| **Inspectrum** | `.IQ` visualizer (view only) | Adds classification + demod + FEC decode |
| **Universal Radio Hacker** | Protocol analysis | Adds ML modulation ID + spectral analysis |
| **GNU Radio Companion** | SDR flowgraph builder | Simpler GUI for file analysis, no flowgraphs needed |

---

## 10. Out of Scope

- Classified signal protocol databases
- Live spectrum monitoring
- Automatic signal acquisition from SDR hardware
- Network-based collaboration features
- Mobile or web interface
