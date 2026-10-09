# SignalForge — Development Rules & Standards

> These rules govern how SignalForge is built. They are derived from the design philosophy in the SIH 26147 proposal and must be followed by all team members and AI agents contributing to this codebase.

---

## 1. Honesty Rules (Non-Negotiable)

These rules exist because NTRO is a technical organization that will ask hard questions. False confidence destroys credibility.

### R-H1: Never Auto-Detect `.IQ` Format
The `.IQ` file format has no standard header. Auto-detection from raw bytes cannot reliably distinguish float32 from int16. **Always require the user to select the format from a dropdown.** Provide a preview to help them verify.

### R-H2: Never Claim Auto-Detection of Interleaving Parameters
Blind detection of interleaving type and parameters from a raw bit stream is an open research problem. The de-interleaving module **always requires user-provided type and parameters**. Do not add any "detect" button.

### R-H3: Never Claim Auto-Detection of FEC Parameters
Viterbi and Reed-Solomon **cannot function without correct parameters** (K, code rate, n, k). Always require user input. Never guess.

### R-H4: Always Show ML Confidence Score
The ML classifier output must **always display a confidence percentage** alongside the predicted modulation type. Example: `"QPSK (78%)"` — never just `"QPSK"`.

### R-H5: Show Low-Confidence Warning
If classifier confidence < 50%, display a warning indicator: `"⚠ Low confidence — verify with constellation diagram"`. Do not suppress uncertainty.

### R-H6: Never Claim > 85% Accuracy in Marketing or Comments
The ML classifier achieves ~75–85% at SNR ≥ 5 dB. Never write code comments, docstrings, or UI text claiming higher accuracy. The locked accuracy table is in `memory.md`.

---

## 2. Architecture Rules

### R-A1: Offline-First — No Network Calls
Zero network calls are permitted anywhere in the codebase. No `requests`, no `urllib`, no cloud API clients. The tool must work in a fully air-gapped environment.

### R-A2: No GPU Dependencies
Do not introduce PyTorch, TensorFlow, CUDA, or any GPU-dependent library. All computation must run on CPU. The Random Forest classifier runs in milliseconds on CPU — no GPU is needed.

### R-A3: Non-Blocking GUI — Always Use QThread
All operations that take > 100ms (file loading, FFT, ML classification, demodulation, FEC decoding) **must run in a `QThread` worker** with `pyqtSignal` callbacks. The main GUI thread must never be blocked.

### R-A4: Normalize to complex64 at Ingest
Both `.wav` and `.IQ` ingestion paths must normalize their output to a **NumPy `complex64` array**. All downstream modules (DSP, ML, demod) receive this format — they must not know or care about the source format.

### R-A5: Modular Backend — No GUI Code in Backend
Backend modules (`backend/`) must not import any `PyQt6` symbols. The GUI imports from backend, never the reverse. Backend functions must be independently testable.

### R-A6: No GNU Radio
GNU Radio is not part of this project. Do not add GR dependencies or GR flowgraph files. Use NumPy + SciPy + commpy instead.

---

## 3. Code Quality Rules

### R-C1: Type Hints Required
All public functions must have Python type hints. Example:
```python
def extract_features(signal: np.ndarray) -> list[float]:
```

### R-C2: Docstrings for All Public Functions
Every public function must have a docstring explaining: what it does, parameters, and return value.

### R-C3: No Magic Numbers
Signal processing constants (sample rates, threshold values, filter cutoffs) must be **named constants** or function parameters — never bare numeric literals buried in code.

### R-C4: Feature Extraction Must Match Training
The 6 features extracted at inference time **must exactly match** the features used during training. Any change to feature extraction requires retraining the model. These features are:
1. `std(abs(signal))` — std dev of instantaneous amplitude
2. `kurtosis(abs(signal))` — kurtosis of instantaneous amplitude
3. `std(unwrap(angle(signal)))` — std dev of instantaneous phase
4. `std(diff(unwrap(angle(signal))))` — std dev of instantaneous frequency
5. `max(abs(fft(signal))**2)` — max spectral power density
6. `zero_crossing_rate(abs(signal))` — zero-crossing rate

### R-C5: Model File Location
The pre-trained Random Forest model must always be loaded from `models/rf_classifier.pkl`. Do not hardcode absolute paths. Use `Path(__file__).parent.parent / 'models' / 'rf_classifier.pkl'`.

### R-C6: Error Handling — No Silent Failures
- File parse errors: raise a descriptive exception caught by the GUI and shown in a `QMessageBox`
- Demodulator failures: return an empty bit stream with an error string, display in bit stream tab
- FEC decode failures: display number of uncorrected errors, do not silently return garbage

---

## 4. UI/UX Rules

### R-U1: File Dialog Filter
The file dialog must filter by: `*.wav *.iq *.IQ *.bin` — users should not be able to accidentally load unrelated file types.

### R-U2: Sample Rate Display
The currently loaded sample rate must always be visible in the sidebar. It should update immediately after file load and be labeled clearly.

### R-U3: Pipeline State Indicators
Each pipeline stage must have a visual state indicator (e.g., a status label or icon):
- Gray = not yet run
- Green = completed successfully
- Orange = completed with warnings (e.g., low confidence)
- Red = failed

### R-U4: Dark Mode
The application uses a **dark color theme** (dark gray background). Do not use PyQt6's default light theme. Apply a dark QStyleSheet at startup.

### R-U5: Monospace Font in Bit Viewer
The hex dump viewer must use a **monospace font** (Courier New or Consolas). This is mandatory for alignment.

### R-U6: Override is Always Available
At any stage where automation is used (modulation classification → demod type selection), the user must be able to **override the automated choice** via a dropdown. Never lock the user into an automated decision.

---

## 5. DSP Rules

### R-D1: FSK Demodulation Method
FSK demodulation uses the **frequency discriminator** approach: instantaneous frequency = `diff(unwrap(angle(signal))) * fs / (2*pi)`. Do not use PLL-based FM discriminators — the simple diff approach is sufficient and much simpler.

### R-D2: BPSK/QPSK Demodulation Method
PSK demodulation follows: Costas loop (carrier recovery) → RRC matched filter (`commpy.filters.rrcosfilter`) → Mueller & Müller timing recovery → hard-decision mapping.

### R-D3: Welch PSD Parameters
Use `scipy.signal.welch` with:
- `nperseg = min(1024, len(signal)//8)`
- `window = 'hann'`
- `return_onesided = False` (for complex signals)

### R-D4: Bandwidth Estimation
Bandwidth is estimated as the −3 dB (or −10 dB) width from the PSD. The threshold method: find the peak, then find the frequencies where PSD drops below `peak − 3 dB` on both sides.

### R-D5: Waterfall Window Size
The waterfall spectrogram uses a sliding window. Default window size: 256 samples, overlap: 50%. Configurable via a slider in the waterfall tab.

---

## 6. ML Rules

### R-M1: Training Dataset
The Random Forest classifier is trained **exclusively on RadioML 2018.01A**. Do not mix training data from other datasets without documenting it in `memory.md`.

### R-M2: Classifier is Pre-Trained
The classifier is trained pre-hackathon and loaded as `rf_classifier.pkl`. It is **not retrained at runtime**. Training code lives in `scripts/train_classifier.py` (offline use only).

### R-M3: Random Forest Parameters
- `n_estimators = 100`
- `max_depth = 20`
- `random_state = 42`
- `n_jobs = -1` (use all CPU cores for training)

### R-M4: No CNN in MVP
Do not add CNN-based classifiers to the main pipeline. If a CNN is implemented as a stretch goal, it must be in `backend/classifier_cnn.py` and used only if explicitly enabled. The RF classifier is always the primary path.

---

## 7. Testing Rules

### R-T1: Minimum Test Signals (Must Be Available Before Demo)
- 5 known FSK recordings (labeled with ground-truth modulation type + params)
- 5 known PSK recordings (labeled)
- 1 known convolutionally-coded signal (K=7, rate=1/2) for Viterbi test
- 1 known RS-coded signal (n=255, k=223) for RS test

### R-T2: Demo Accuracy Targets (Must Be Validated Pre-Demo)
| Signal Type | Required Accuracy |
|------------|-----------------|
| FSK classification | > 85% on 5 test files |
| PSK classification | > 75% on 5 test files |
| FSK demod → bit stream | Correct on 3 of 3 test files |
| Viterbi decode | Correct on 1 test signal |

### R-T3: Performance Targets (Must Be Validated Pre-Demo)
| Operation | Target |
|-----------|--------|
| File load → spectrum display | < 3 seconds |
| ML classification | < 1 second |
| GUI thread blocking | Zero (verified by UI responsiveness during computation) |

---

## 8. Dependency Rules

### R-DEP1: Approved Dependencies Only
Only the following packages are approved for use:

```
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
PyQt6>=6.5
pyqtgraph>=0.13
scikit-learn>=1.3
commpy>=0.7
reedsolo>=1.7
joblib  (included with scikit-learn)
```

Adding new dependencies requires team consensus and updating `requirements.txt`.

### R-DEP2: No Compilation Required
All dependencies must be installable via `pip install -r requirements.txt` with no compilation step. No C extensions that require a compiler.

### R-DEP3: requirements.txt Must Be Complete
`requirements.txt` must list all direct dependencies with minimum version pins. Running `pip install -r requirements.txt` on a fresh Python 3.10 environment must produce a fully working application.
