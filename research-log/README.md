# Research Monograph & Technical Report

## Quantum Resource Optimizer: Constrained Green Energy Asset Allocation via QAOA
**Qiskit Fall Fest 2026 — Track 2: Open-Domain Optimization & Real-World Solvers**  
**Author:** Dharmendra P. (Indian Institute of Information Technology Kottayam)

---

## 1. Overview
This directory contains the modular LaTeX source project and compiled research report for the **Quantum Resource Optimizer**. The report provides an academic treatment of the constrained Markowitz portfolio allocation problem mapped to an Ising Cost Hamiltonian and solved using the Quantum Approximate Optimization Algorithm (QAOA) with Qiskit 2.5 primitives.

---

## 2. Document Structure

```text
research-log/
├── main.tex                    # Master LaTeX entry point
├── README.md                   # Build and reproduction instructions
├── frontmatter/
│   ├── titlepage.tex           # Formal title page
│   └── abstract.tex            # Abstract and keywords
├── chapters/
│   ├── introduction.tex        # Problem motivation, societal dilemma, research questions
│   ├── background.tex          # MPT, QUBO, Ising spin model, QAOA foundations
│   ├── problem-formulation.tex # Detailed mathematical derivation and equivalence proof
│   ├── methodology.tex         # Variational loop, Qiskit primitives, metrics
│   ├── implementation.tex      # Software architecture, classical baselines, tests
│   ├── experimental-setup.tex  # 5-asset benchmark instance, parameters, environment
│   ├── results-and-discussion.tex # Empirical benchmarks, depth scaling, penalty sweeps
│   ├── limitations.tex         # NISQ noise, gate errors, heavy-hex SWAP routing, plateaus
│   └── conclusion.tex          # Findings and strategic roadmap (XY mixers, QEM)
├── appendices/
│   └── implementation-details.tex # Code listings, CLI usage, environment disclosures
├── references/
│   └── references.bib          # Verified academic bibliography database
├── tables/
│   ├── asset_catalog.tex       # 5-asset renewable candidate catalog
│   ├── benchmark_summary.tex   # Comparative cross-solver benchmark table
│   ├── depth_sweep.tex         # QAOA depth scaling metrics (p=1, 2, 3)
│   └── penalty_sweep.tex       # Constraint penalty sensitivity sweep (lambda in [0.5, 5.0])
├── code/
│   ├── hamiltonian_mapping.py  # QUBO to SparsePauliOp mapping excerpt
│   └── endianness_decoding.py  # Little-endian bitstring decoding excerpt
└── figures/
    ├── qaoa_circuit_p1.png     # p=1 QAOA circuit diagram
    ├── convergence_trajectory.png # COBYLA energy minimization trajectory
    ├── solution_distribution.png  # Basis state measurement probability distribution
    ├── depth_scaling_comparison.png # Feasibility yield & runtime vs circuit depth
    ├── penalty_sweep_analysis.png # Sensitivity of feasibility yield across penalty weights
    └── solver_utility_comparison.png # Cross-solver utility comparisons
```

---

## 3. Toolchain Prerequisites

To compile the report with the required **Times New Roman** typography:

1. **TeX Engine:** `xelatex` (MiKTeX-XeTeX 4.10 or TeX Live XeLaTeX).
2. **Bibliography Backend:** `bibtex` (MiKTeX 24.1 or compatible).
3. **System Font:** TrueType font **Times New Roman** (`times.ttf`, `timesbd.ttf`, `timesbi.ttf`, `timesi.ttf` on Windows or Linux system font directories). Accessible via the `fontspec` package.
4. **PDF Inspection Tool (Optional):** `pdffonts` (Poppler utilities) to inspect embedded font metadata.

---

## 4. Reproducible Build Commands

Navigate into the `research-log` directory and execute the following multi-pass compilation:

```powershell
# In PowerShell or Command Prompt:
cd research-log

# Pass 1: Parse structure and generate auxiliary cross-reference files
xelatex -interaction=nonstopmode -halt-on-error main.tex

# Pass 2: Compile bibliography citations
bibtex main

# Pass 3: Resolve citations and table of contents
xelatex -interaction=nonstopmode -halt-on-error main.tex

# Pass 4: Finalize cross-references and page numbers
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

Alternatively, if `latexmk` is configured:
```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

---

## 5. Output Verification & Font Validation

After successful compilation, the compiled document will be generated at:
`research-log/main.pdf`

To verify that **Times New Roman** is strictly embedded without silent font substitution, run:
```powershell
pdffonts main.pdf
```
Expected output confirms embedded font names such as `TimesNewRomanPSMT` and `TimesNewRomanPS-BoldMT` with encoding `Identity-H`.

---

## 6. Experimental Data Provenance

All empirical numbers reported in the monograph are traceable to serialized run files under:
`outputs/runs/20261011_103427_qaoa_n5_seed42/`
- `experiment_metrics.json`: Full configuration, classical baselines, depth sweeps, penalty sweeps.
- `depth_sweep_summary.csv`: Tabular depth scaling summary.
