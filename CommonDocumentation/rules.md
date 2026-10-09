# Rules & Project Standards

## 1. Git Workflow
- The `main` branch is locked. No direct commits.
- Use feature branches prefixed by track: `feat/gui-*`, `feat/dsp-*`, `feat/ml-*`.
- Pull Requests require at least one approving review from a member of a different track.
- Commit messages must follow the format: `[Track] Description of change` (e.g., `[DSP] Implement BPSK Costas Loop`).

## 2. Python Coding Standards
- **Typing**: Use standard Python type hinting (`typing` module) for all function arguments and return types.
- **Docstrings**: All core engine functions and classes must have Google-style docstrings.
- **Data Types**: Enforce NumPy `np.complex64` for all core IQ signal arrays. Avoid implicit upcasting to `complex128` to save memory.
- **Formatting**: Adhere to PEP 8.

## 3. UI/UX Rules
- **No blocking**: Any operation expected to take more than 100ms must run in a `QThread`. The UI must remain responsive.
- **Graceful Failure**: Never crash to terminal. Catch `Exception` in QThreads and emit an error signal to display a `QMessageBox` to the user.

## 4. Dependencies
- New dependencies must be approved by the lead.
- We must remain completely independent of vendor-specific APIs and proprietary hardware libraries. 
- Only pure Python / pip-installable binary wheels are allowed (no complex C++ compilation steps during install).
