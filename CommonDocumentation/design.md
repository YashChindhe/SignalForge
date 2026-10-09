# SignalForge — GUI Design & UX Specification

---

## Design Philosophy

SignalForge is a **guided automation workbench**, not a black-box AI tool. The design must:

1. **Show, don't guess** — every automated result (modulation type, bandwidth) is accompanied by a visual output (constellation, spectrum) so the analyst can confirm it.
2. **Be honest about uncertainty** — confidence scores are shown alongside ML predictions. User can override.
3. **Never silently fail** — if a parameter is needed that can't be auto-detected (e.g., IQ format, FEC params), the UI explicitly asks the user rather than making a silent guess.
4. **Fast first impression** — file load → spectrum/waterfall should appear in under 3 seconds. This is the key demo milestone.

---

## Application Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SignalForge                                          [─] [□] [✕]       │
├──────────────┬──────────────────────────────────────────────────────────┤
│  FILE PANEL  │  [Spectrum] [Waterfall] [Constellation] [Bit Stream]     │
│              ├──────────────────────────────────────────────────────────┤
│  [Load File] │                                                          │
│              │                  TAB CONTENT AREA                        │
│  Format:     │              (plots / hex viewer)                        │
│  [float32 ▼] │                                                          │
│              │                                                          │
│  Sample Rate:│                                                          │
│  [_______]   │                                                          │
│              │                                                          │
│  ─────────── │                                                          │
│  SIGNAL INFO │                                                          │
│  Duration: – │                                                          │
│  Samples:  – │                                                          │
│  Bandwidth:– │                                                          │
│              │                                                          │
│  ─────────── │                                                          │
│  MODULATION  │                                                          │
│  [Classify]  │                                                          │
│  Result: –   │                                                          │
│  Conf:    –  │                                                          │
│              │                                                          │
│  ─────────── │                                                          │
│  DEMODULATE  │                                                          │
│  Type: [▼]   │                                                          │
│  [Demod]     │                                                          │
│              │                                                          │
│  ─────────── │                                                          │
│  DE-INTERL.  │                                                          │
│  Type: [▼]   │                                                          │
│  Params: [_] │                                                          │
│  [Apply]     │                                                          │
│              │                                                          │
│  ─────────── │                                                          │
│  FEC DECODE  │                                                          │
│  Type: [▼]   │                                                          │
│  Params: [_] │                                                          │
│  [Decode]    │                                                          │
└──────────────┴──────────────────────────────────────────────────────────┘
```

---

## Panels & Tabs

### Left Sidebar — Control Panel

The left sidebar is persistent and drives the pipeline. It is divided into collapsible sections:

| Section | Contents | Notes |
|---------|---------|-------|
| **File Load** | `[Load File]` button, format dropdown (float32/int16/complex64, interleaved toggle), sample rate input | Dropdown + preview before confirming `.IQ` format |
| **Signal Info** | Duration, sample count, bandwidth estimate | Auto-populated after file load |
| **Modulation** | `[Classify Modulation]` button, result label, confidence % | ML result; analyst can manually override via dropdown |
| **Demodulate** | Modulation type dropdown, `[Demodulate]` button | Pre-filled from classifier; user can override |
| **De-Interleaving** | Type dropdown (Block/Conv/Diag/PR), parameter input fields, `[Apply]` button | All user-provided; no auto-detection |
| **FEC Decode** | Type dropdown (Viterbi/RS/LDPC), parameter fields (K, rate, n, k), `[Decode]` button | All user-provided |

---

### Main Tab Area — Visualization Tabs

#### Tab 1: Spectrum
- **FFT Power Spectral Density** (Welch method)
- X-axis: Frequency (Hz, centered at 0 for baseband)
- Y-axis: Power (dBm or dBFS)
- Peak frequency annotation
- Bandwidth markers (−3 dB, −10 dB)
- Library: **Matplotlib** embedded in PyQt6 canvas

#### Tab 2: Waterfall
- **Spectrogram** (time–frequency plot)
- X-axis: Frequency
- Y-axis: Time (scrolling or full-file view)
- Color map: viridis or plasma (high contrast for low SNR signals)
- Interactive: zoom, pan, time slice selection
- Library: **PyQtGraph** (for real-time-like interactive behavior)

#### Tab 3: Constellation
- **I vs Q scatter plot**
- Applied after timing recovery from demodulator
- Expected cluster patterns shown as reference overlays:
  - BPSK: 2 clusters on real axis
  - QPSK: 4 clusters at ±45°, ±135°
  - 8PSK: 8 clusters around unit circle
- Library: **Matplotlib**

#### Tab 4: Bit Stream / Hex Viewer
- Decoded bits shown as **hex dump** (16 bytes per row, offset + hex + ASCII columns)
- **Sync word search**: user inputs known header/sync bytes → highlighted in viewer
- Implemented using `numpy.correlate` for pattern matching
- Library: **PyQt6 QTextEdit** with custom monospace rendering or `QTableWidget`

---

## User Workflow (Exact UX Flow)

```
1. User opens SignalForge
        │
        ▼
2. Clicks "Load File" → file dialog opens → selects .wav or .IQ
        │
        ├── .wav → auto-parsed (sample rate read from header)
        │
        └── .IQ → format dropdown activates
                   user selects: float32 / int16 / complex64
                   user enters sample rate
                   "Preview" button shows first 500 samples as mini plot
                   User clicks "Confirm"
        │
        ▼
3. Spectrum + Waterfall tabs populate immediately (<3 seconds)
   Signal Info panel shows: duration, sample count, bandwidth estimate
        │
        ▼
4. User clicks "Classify Modulation"
   → ML classifier runs (<1 second)
   → Result: "QPSK (confidence: 78%)" shown in sidebar
   → Constellation tab updates with I/Q scatter
        │
        ▼
5. User clicks "Demodulate"
   → Modulation type pre-filled from classifier (user can override)
   → Demodulator runs → bit stream generated
   → Constellation tab shows post-demod scatter (confirms timing recovery)
        │
        ▼
6. (Optional) User selects de-interleaving type + enters parameters → [Apply]
        │
        ▼
7. (Optional) User selects FEC type + enters parameters → [Decode]
        │
        ▼
8. Bit Stream tab shows hex dump
   User enters sync word pattern → [Search] → matches highlighted
```

---

## Key UX Principles

### Honest Uncertainty Display
- ML result always shows **confidence score**: `"QPSK (78%)"` not just `"QPSK"`
- If confidence < 50%, show warning: `"⚠ Low confidence — verify with constellation"`
- Analyst can override modulation type at any point in the pipeline

### .IQ Format Preview
- Before committing to format, show a mini preview of the first ~500 samples as an amplitude-vs-time plot
- Bad format selection → signal looks like noise/garbage → user re-selects
- This prevents silent corrupt pipelines

### Error States
- If file cannot be parsed: clear error dialog with reason
- If demodulator fails (e.g., no signal found): show error in bit stream tab, not silent empty output
- If FEC decode fails: show number of uncorrected errors

### Progress Feedback
- Long operations (large file FFT, classification) show a **progress bar** or spinning indicator
- GUI never freezes — all heavy operations run in a `QThread` worker

---

## Visual Design Guidelines

| Element | Specification |
|---------|-------------|
| **Color theme** | Dark mode (dark gray background `#1e1e2e`, light text) |
| **Accent color** | Teal / cyan `#00d4aa` for active buttons and highlights |
| **Font** | Monospace for bit viewer (Courier New / Consolas); Sans-serif for labels (Segoe UI) |
| **Plot colors** | Spectrum: green on dark; Waterfall: plasma colormap; Constellation: white dots on black |
| **Button style** | Flat buttons with hover state; primary action buttons in accent color |
| **Layout** | Fixed-width sidebar (~280px); resizable main content area |

---

## GUI Component Library

| Component | PyQt6 Widget | Notes |
|-----------|-------------|-------|
| Main window | `QMainWindow` | With `QDockWidget` for sidebar |
| File dialog | `QFileDialog` | Filter: `*.wav *.iq *.IQ *.bin` |
| Format dropdown | `QComboBox` | Items: float32, int16, int8, complex64 |
| Sample rate input | `QLineEdit` with validator | Accepts numeric Hz values |
| Tab area | `QTabWidget` | Tabs: Spectrum, Waterfall, Constellation, Bit Stream |
| Spectrum plot | `FigureCanvasQTAgg` (Matplotlib) | Embedded MPL figure |
| Waterfall plot | `PyQtGraph ImageView` | Real-time-capable |
| Constellation plot | `FigureCanvasQTAgg` (Matplotlib) | Scatter plot |
| Hex viewer | `QTextEdit` (read-only, monospace) | Custom hex formatter |
| Progress bar | `QProgressBar` | Shown during long operations |
| Worker threads | `QThread` + `pyqtSignal` | Non-blocking heavy computation |
