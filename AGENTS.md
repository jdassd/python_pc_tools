# Repository Guidelines

## Project Structure & Module Organization
- Entry point: `main.py` (launches the PyQt6 app, orchestrates tools/windows).
- UI windows: `*_window.py` (e.g., `audio_window.py`, `system_window.py`).
- Utilities: `*_utils.py` for domain logic, `utils.py` for shared helpers.
- Managers: `data_manager.py` (persistence), `update_manager.py` (app updates).
- Styling & assets: `styles.qss`, images (`*.png`), optional data in `data/`.
- Packaging artifacts: `main.spec`, build outputs in `build/` and `dist/`.

## Build, Run, and Development
- Create env and install deps: `pip install -r requirements.txt`
- Run locally: `python main.py`
- Package (PyInstaller): `pyinstaller -y main.spec` → binaries in `dist/`
- Tip: avoid editing files in `build/` or `dist/`; they are generated.

## Coding Style & Naming Conventions
- Follow PEP 8 (4‑space indent, 88–120 col soft limit).
- Modules/files: `lower_snake_case.py`; classes: `CamelCase`; functions/vars: `snake_case`; constants: `UPPER_SNAKE_CASE`.
- Keep UI in `*_window.py` and logic in `*_utils.py`; prefer small, focused modules.
- Add type hints where practical and docstrings for public functions.

## Testing Guidelines
- This repo has no formal test suite yet. If you add tests:
  - Use `pytest` with files named `tests/test_*.py`.
  - Favor fast, deterministic unit tests for `*_utils.py`; GUI tests may include minimal smoke checks.
  - Example: `pytest -q` (add `pytest` to dev deps as needed).

## Commit & Pull Request Guidelines
- Commits: concise, imperative summaries (Chinese/English OK). Group related changes; avoid mixing refactors with features.
- Optional prefixes welcomed: `feat:`, `fix:`, `docs:`, `refactor:`, `build:`.
- PRs should include: clear description, rationale, steps to run, and screenshots/GIFs for UI changes. Reference related issues.
- Update `README.md` when behavior or usage changes; add release note hints if version-relevant.

## Security & Configuration Tips
- Do not hardcode secrets or tokens; use environment variables or local config ignored by Git.
- Be cautious with file/network operations in `network_utils.py` and `crypto_utils.py`; validate inputs and handle failures gracefully.
- Large binaries belong in releases, not in Git; keep `data/` small and sample‑oriented.
