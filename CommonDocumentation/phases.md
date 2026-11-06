# Development Phases & Roadmap

## 1. Pre-Hackathon Preparation (Week -2 to Day 0)
- **Dataset Prep**: Download RadioML 2018.01A dataset.
- **ML Training**: Extract 6 statistical features, train the Random Forest model, and save as `.pkl` artifacts.
- **Test Data**: Generate known synthetic signals (BPSK, QPSK, FSK) with ground-truth bit arrays for live demonstrations.

## 2. 36-Hour Hackathon Timeline (MVP)

**Track 1: GUI (2 members) | Track 2: DSP (2 members) | Track 3: ML+FEC (2 members)**

- **Hours 0–12 (Foundation)**: 
  - GUI: Skeleton app, Matplotlib/PyQtGraph embed, File Loader.
  - DSP: `.wav`/`.IQ` ingest, FFT/PSD logic, FSK demodulator.
  - ML: Load `.pkl`, basic classification wrapper.
  - *Milestone*: Load file, view spectrum, get ML classification.
- **Hours 12–24 (Core Value)**:
  - GUI: Constellation tab, Demod controls, QThread integration.
  - DSP: BPSK/QPSK demodulators, Costas loops, Block de-interleaving.
  - ML+FEC: Viterbi + RS decoder wrappers, hex bitstream output.
  - *Milestone*: Demodulate FSK/BPSK and view bit stream.
- **Hours 24–36 (Polish & Demo)**:
  - GUI: Sync word search highlight, splash screen, error handling.
  - DSP: Edge cases, performance tuning (vectorization).
  - ML: Demo script rehearsal, accuracy verification.
  - *Milestone*: Full pipeline demonstration ready.

## 3. Post-Hackathon Roadmap
- **Weeks 1-4**: Stabilization, 80%+ test coverage, PyInstaller packaging.
- **Weeks 5-12**: Advanced DSP (16-QAM CMA, Polyphase filterbanks, Multi-signal detection).
- **Weeks 13-20**: Deep Learning Upgrade (1D-CNN on raw IQ, Transfer Learning).
- **Months 6+**: Enterprise scale (Batch processing, Protocol identification, Plugin ecosystem).
