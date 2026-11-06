# System Design & UI/UX

## 1. UI Layout
The main window of SignalForge is built with a two-pane layout using `QSplitter`:
- **Left Panel (Controls)**: A vertical, scrollable panel containing:
  - File Loader (Dialog trigger, IQ format dropdown).
  - Signal Stats (Sample rate, duration, bandwidth).
  - Modulation Result (ML prediction + confidence bar).
  - Demodulation & De-interleave parameter overrides.
- **Right Panel (Visualization)**: A tabbed interface (`QTabWidget`):
  - **Tab 1: Spectrum/PSD**: Embedded Matplotlib canvas showing FFT and Power Spectral Density.
  - **Tab 2: Waterfall**: PyQtGraph high-performance heatmap.
  - **Tab 3: Constellation**: I/Q scatter plot updated dynamically post-timing recovery.
  - **Tab 4: Bit Stream**: Hex dump viewer with sync-word search highlighting.

## 2. Aesthetics & Styling
- **Theme**: A professional, high-contrast dark theme (via QSS stylesheet) tailored for prolonged usage by intelligence analysts.
- **Colors**: Deep navy/charcoal backgrounds (`#1a1a2e`), vibrant accents for interactive elements (`#e94560`), and high-readability text (`#eaeaea`).

## 3. User Journey
1. **Load**: User selects a file. If `.wav`, auto-parsed. If `.IQ`, user selects data type and sample rate.
2. **Observe**: Waterfall and Spectrum render instantly.
3. **Classify**: User clicks "Classify". ML runs and suggests a modulation type (e.g., QPSK 78%).
4. **Demodulate**: User executes demodulation. The constellation diagram updates.
5. **Decode**: User provides known FEC parameters to decode and view hex data, then searches for known sync words.
