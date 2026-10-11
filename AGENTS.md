# AGENTS.md — Contributor & AI Agent Operating Instructions

Welcome to the **Quantum Resource Optimizer** project repository for the Qiskit Fall Fest 2026 (Track 2: Open-Domain Optimization & Real-World Solvers).

This document outlines strict operational rules, architectural conventions, tool responsibilities, and security policies for any AI agent or human contributor working within this codebase.

---

## 1. Role and Responsibility Split

- **Primary Planning, Implementation & Testing Agent:** Gemini 3.8 Flash High in Google Antigravity.
  - Responsible for requirements traceability, mathematical modeling, Qiskit implementation, automated testing, benchmarking experiments, research documentation, and demo scripts.
- **Git Commit Staging & Skill Maintenance Agent:** OpenCode.
  - Responsible for agent-skill creation/maintenance and staging Git commits strictly upon explicit user authorization.
  - OpenCode MUST NOT perform core Qiskit algorithm implementation.
- **Supplementary Review:** ChatGPT (external architectural review and debugging assistance).
- **Human User (Dharmendra P.):** Reviews code diffs, authorizes Git commits, and executes pushes to the remote GitHub repository.

---

## 2. Hard Security & Git Invariants

1. **Never Commit or Expose Secrets:**
   - No IBM Quantum API tokens, cloud credentials, passwords, or personal access tokens may ever appear in source code, notebooks, test logs, terminal outputs, or Git commits.
   - Credentials must only be loaded via environment variables or an untracked `.env` file (see `.gitignore`).
2. **No Unauthorized Commits or Pushes:**
   - AI agents must NEVER execute `git push`.
   - AI agents must NEVER run `git commit` autonomously unless the user explicitly requests a commit.
   - Staging must be selective (`git add <specific_path>`), never blanket (`git add .`).
3. **Preserve Repository Integrity:**
   - Do NOT delete the existing MIT `LICENSE`.
   - Do NOT delete or modify `.agents/skills/` without clear intent and user notice.
   - Respect `.gitignore` rules (cache, virtual environments, large transients).
4. **Official README Headings:**
   - The automated grading system for Qiskit Fall Fest 2026 relies on the exact Markdown structure from the official hackathon template.
   - Do NOT rename or remove template section headings (Sections 1 through 7) in `README.md`.

---

## 3. Technology Stack and Architecture

- **Language:** Python 3.10+ (Recommended: Python 3.12).
- **Quantum Core:** Qiskit 1.0+ (`qiskit.quantum_info.SparsePauliOp`, `qiskit.circuit.library.QAOAAnsatz`, `qiskit.primitives.StatevectorEstimator`, `qiskit.primitives.StatevectorSampler`).
- **Simulators:** Qiskit Aer (`qiskit_aer`) or built-in reference statevector primitives for deterministic, fast local execution without external API dependencies.
- **Graph & Math Utilities:** `rustworkx`, `scipy.optimize`, `numpy`, `matplotlib`.
- **Testing:** `pytest` in `tests/`.

---

## 4. Coding Standards

- **Modularity:** Keep functions focused with explicit docstrings and type annotations.
- **Determinism:** Seed all stochastic components (`numpy.random.seed`, initial parameters) in test suites.
- **End-to-End Traceability:** Every quantum solution sampled must be decoded from little-endian bitstrings and verified through independent classical objective recalculation.
- **No Placeholders:** All code committed must be functional, tested, and executable.

---

## 5. Development Workflow Commands

```bash
# Activate environment
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux / macOS

# Install dependencies
pip install -r requirements.txt

# Run automated tests
pytest -v tests/

# Execute CLI solver
python src/main.py --num-assets 5 --budget 2 --p 1 --shots 2048

# Run reproducible benchmarks
python -m quantum_optimizer.experiment_runner
```

---

## 6. Agent Skills — How They Fit Together

All published project skills live in `.agents/skills/<skill-id>/SKILL.md`.

> **Discovery note:** `.agents/skills/` (plural) **is** a native OpenCode project
> discovery path, so these skills load with no configuration entry. One local-only
> skill remains in `.agent/skills/` (singular) and is loaded through the
> `"skills": ["./.agent/skills"]` entry in the repository-root `opencode.json`; it
> is deliberately git-ignored and never published. OpenCode must be started **from
> the repository root** — config discovery walks *up* from the working directory,
> so launching from the parent workspace sees neither location. Run
> `opencode reload` after changing any `SKILL.md` or the config.

| Order | Skill | ID | Purpose |
| :--- | :--- | :--- | :--- |
| 1 | **Qiskit Optimization** | `qiskit-optimization` | Mathematical modeling, formulation choice, cost Hamiltonian, QAOA implementation review, honest result framing. |
| 2 | **Python Testing** | `python-testing` | Correctness of objective, penalties, encoding/decoding, and classical baselines. |
| 3 | **Experiment Reproducibility** | `experiment-reproducibility` | Repeatable runs, experiment IDs, seeds, and machine-readable run metadata. |
| 4 | **Technical Documentation** | `technical-documentation` | Verified project records: `README.md`, `docs/`, `research-log/`, `PROJECT_STATUS.md`. |
| 5 | **AI Commit** | `ai-commit` | Reviewed Git changes only. Defaults to plan-only; never self-authorized. |
| 6 | **AI Text Quality** | `ai-text-quality` | Writing quality and academic LaTeX document engineering. |
| — | *Text polishing* (local only) | `AI Water-mark Remover` | Local-only, git-ignored, not published. See `.agent/skills/`. |

**Suggested order of operations:** model the problem (1) → prove correctness (2) →
run and record the experiment (3) → document what actually happened (4) → stage
reviewed changes (5).

### Per-skill rules

1. **`qiskit-optimization`** — Use before writing quantum code and whenever a result
   is described as optimal or advantageous. Enforces: consult the official
   requirements first, check installed Qiskit versions rather than memory, simulate
   locally before reaching for hardware, keep CRNs and tokens out of source and Git,
   re-evaluate decoded solutions independently, and never present a *good candidate*
   as a *proven optimum* or *demonstrated quantum advantage*.
2. **`python-testing`** — Use whenever code under `src/` or `tests/` changes.
   Hand-check the maths, test edge cases, cross-check small instances against brute
   force, and verify feasibility independently of the penalty value. **Never claim
   tests passed without executing them** — report the exact command and its real
   outcome.
3. **`experiment-reproducibility`** — Use for every benchmark, sweep, or reported
   number. Assign an `EXP-NNN-slug` ID, record seeds, parameters, input sizes,
   dependency versions, backend, runtime, metrics, artifact paths, and errors in
   machine-readable JSON. Compare only across comparable instances, and never
   invent or interpolate results.
4. **`technical-documentation`** — Use for every documentation change. Keep
   documents consistent with the actual code, record design decisions with rationale
   and verification, cite only sources actually consulted, record AI/tool usage
   accurately, and separate implemented functionality from planned work. Keep
   `PROJECT_STATUS.md` current with verified progress and remaining blockers.
5. **`ai-commit`** — Defaults to **plan-only**: inspects `git status` and diffs,
   checks for secrets, unrelated files, and inappropriate generated artifacts,
   and writes a reviewable commit plan under `research-log/logs/commit-plans/`.
   It **must never commit or push without explicit user authorization**. Exiting
   plan-only mode requires the exact trigger `COMMIT-EXECUTE-AUTHORIZED`;
   reconstructing genuinely past uncommitted work requires
   `RECOVER-LEGITIMATE-HISTORY` plus separate authorization. It also enforces a
   Git identity and remote verification gate, because the owner uses multiple SSH
   identities and commits must not be attributed to the wrong account.
6. **`ai-text-quality`** — Technical writing quality plus academic LaTeX document
   engineering: six-stage workflow, protected content (code, equations, citations,
   cross-references, attribution, licenses, AI-use disclosures), modular LaTeX
   architecture, reproducible compilation, and PDF quality assurance. Defaults to
   real Times New Roman and requires `pdffonts` verification rather than trusting
   a successful compile. It must never fabricate results or citations, and never
   target AI-detector scores or remove required disclosure.

> `ai-commit`, `ai-text-quality`, and the local-only text-polishing skill are
> registered with `opencode/autoinvoke: false`, so they are never advertised
> automatically. They stay loadable by ID on explicit request only.

### Who does what

- **Gemini 3.8 Flash High (Antigravity)** owns project implementation: modeling,
  Qiskit code, tests, experiments, and research documentation.
- **OpenCode** owns skill maintenance and prepares commits *after* user review. It
  does not write core Qiskit algorithm implementations.
- **The user** reviews diffs, authorizes commits, and performs every `git push`.
