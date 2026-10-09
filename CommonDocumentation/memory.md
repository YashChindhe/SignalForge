# Project Memory, Context & Risks

## 1. Technology Choices Rationale
- **Why PyQt6?** Native desktop feel, stable, easy integration with Matplotlib.
- **Why Random Forest over Deep Learning?** Training a CNN on raw IQ takes hours/days and requires a GPU. A Random Forest on 6 hand-crafted statistical features trains in minutes on a CPU, runs instantly, and hits ~80% accuracy for standard modulations.
- **Why User-Assisted De-interleaving/FEC?** Blind detection of interleaving depths and FEC parameters is a highly complex open research problem. Implementing user-configurable parameters is honest, reliable, and practically useful.

## 2. Known Risks & Mitigations
| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| IQ Format Auto-detect Failure | High | Don't auto-detect. Provide a dropdown for user selection and a preview pane. |
| Timing Recovery Instability | High | Implement Gardner/M&M loops but allow manual symbol rate overrides. |
| GUI Freezing on large files | Med | Run all DSP processing inside `QThread` workers. Chunk large files. |
| ML underperforms | Med | The GUI shows ML confidence + Constellation plot. Analyst acts as final judge. |

## 3. Testing & Validation Strategy
- **Unit Testing**: `pytest` covering individual DSP components (e.g., verifying Costas loop convergence).
- **Ground Truth Testing**: Generating synthetic signals via script with a known pseudo-random bit sequence, injecting noise, running it through the app, and comparing BER (Bit Error Rate). Target: < 1% BER at 15dB SNR for BPSK.
