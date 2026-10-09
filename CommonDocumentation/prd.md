# Product Requirements Document (PRD)

## 1. Project Overview
**Name**: SignalForge — Automated Signal Analysis Workbench  
**SIH ID**: 26147  
**Organization**: National Technical Research Organisation (NTRO)  
**Objective**: Develop an automated, GUI-based desktop application to analyze .IQ and .wav files, extract signal parameters, and demodulate signals.

## 2. Background
Currently, the raw data from off-the-air signal collection (ranging from KHz to GHz) is analyzed manually to identify parameters like sampling rate, modulation, and error correction codes. This manual process is slow, error-prone, and often insufficient for detailed analysis. 

## 3. Core Requirements
The expected GUI-based system must:
1. **Unified File Ingest**: Load both .IQ and .wav files.
2. **Spectral Analysis**: Display time-frequency waterfall and constellation plots.
3. **Signal Parameter Extraction**: Identify sampling frequency, bandwidth, and modulation type automatically using Machine Learning.
4. **Demodulation**: Demodulate FSK, BPSK, and QPSK signals.
5. **De-Interleaving**: Support Block, Convolutional, Diagonal, and Pseudo-Random de-interleaving.
6. **FEC Decoding**: Support Viterbi, Reed-Solomon, Concatenated, and LDPC decoding.
7. **Bit Stream Correlation**: Correlate bit streams to identify headers and payloads via sync word matching.

## 4. Scope & Constraints
- **Offline Capability**: Must run locally without internet/cloud dependencies for security.
- **Assisted Automation**: Where blind automation is unreliable (e.g., de-interleaving and FEC), provide user-guided parameter selection.
- **Tech Stack**: Python 3.10+, PyQt6, scikit-learn, NumPy, SciPy.

## 5. Success Metrics
- File load to spectrum display: < 3 seconds.
- Modulation classification time: < 1 second.
- Classification accuracy: > 80% for SNR >= 10dB.
- Zero GUI freezes during DSP execution.
