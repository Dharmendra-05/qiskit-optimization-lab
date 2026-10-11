# AI Model & Tooling Provenance Log

This log records all AI model usage, tasks performed, and human oversight in accordance with Hackathon Directive §12.

---

## Tooling Configuration

| Tool / Agent | Display Name | Primary Role in Project | Verification & Oversight |
| :--- | :--- | :--- | :--- |
| **Primary Implementation Agent** | Gemini 3.8 Flash High (in Google Antigravity) | Requirements analysis, architecture, math derivations, Qiskit coding, testing, benchmarks, documentation drafting | Reviewed and verified via automated test suite and manual human audit. |
| **Git Staging Agent** | OpenCode | Local agent-skill maintenance and preparing Git commit stages | Invoked only upon explicit human review and authorization. |
| **Supplementary Review** | ChatGPT | External architectural review and sanity checks | Conceptual suggestions cross-checked against official Qiskit documentation. |
| **Human Reviewer** | Dharmendra P. | Code review, commit authorization, and GitHub push | Ultimate authority over repository changes. |

---

## Operation Sessions Log

### Session 1: Requirements Audit & Architecture (2026-10-11 10:15 IST)
- **Model:** Gemini 3.8 Flash High
- **Task:** Comprehensive inspection of `qff26-reference` (README, Hackathon Guide, starter notebooks, requirements).
- **Files Affected:** `docs/requirements-analysis.md`, `docs/topic-selection.md`, `AGENTS.md`, `METADATA.md`.
- **Outcome:** Generated 12-item requirements traceability matrix; evaluated 3 candidate topics; selected Green Energy Portfolio Selection with 100/100 score.

### Session 2: Environment & Core Qiskit Implementation (2026-10-11 10:25 IST)
- **Model:** Gemini 3.8 Flash High
- **Task:** Virtual environment setup (`.venv` via `uv` with Python 3.12, Qiskit 2.5.2, Qiskit Aer 0.17.2). Implementation of `problem.py`, `classical_solvers.py`, `hamiltonian.py`, and `qaoa_solver.py`.
- **Files Affected:** `src/quantum_optimizer/*`, `src/main.py`, `requirements.txt`, `pyproject.toml`.
- **Outcome:** Formulated QUBO and mapped to Ising Hamiltonian. Ground-state equivalence verified mathematically.

### Session 3: Testing, Experiments & Visualizations (2026-10-11 10:33 IST)
- **Model:** Gemini 3.8 Flash High
- **Task:** Authored 12 unit tests across `tests/`. Implemented `experiment_runner.py` and `visualization.py`. Executed multi-parameter sweeps (depth $p=1, 2, 3$ and penalty $\lambda \in [0.5, 5.0]$). Generated `notebooks/solution.ipynb` with all outputs rendered.
- **Files Affected:** `tests/*`, `outputs/*`, `assets/images/*`, `notebooks/solution.ipynb`.
- **Outcome:** 12/12 unit tests passed. Reached Approximation Ratio 1.0000 and 77.00% Feasibility Yield at $p=2$.

### Session 4: Comprehensive Documentation & LaTeX Research Journal (2026-10-11 10:50 IST)
- **Model:** Gemini 3.8 Flash High
- **Task:** Standardized `README.md` following exact hackathon headings. Authored complete documentation (`fundamentals.md`, `mathematical-formulation.md`, `algorithm.md`, `limitations.md`, `demo-script.md`) and complete LaTeX monograph in `research-log/`.
- **Files Affected:** `README.md`, `docs/*`, `research-log/*`.
- **Outcome:** All deliverables ready for hackathon submission.
