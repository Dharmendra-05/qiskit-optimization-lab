# Official Requirements Analysis and Traceability Matrix
**Event:** Qiskit Fall Fest 2026 — IIIT Kottayam (24-Hour Quantum Hackathon)  
**Track:** Track 2: Open-Domain Optimization & Real-World Solvers  
**Audit Date:** October 11, 2026  
**Document Author:** Dharmendra P. / Gemini 3.8 Flash High (Antigravity)

---

## 1. Executive Summary & Track Objectives

According to the official hackathon documentation (`qff26-reference/HACKATHON_GUIDE.md` §2 and `qff26-reference/references/track-2-optimization/README.md` §1):
- **Track 2 Vision:** Formulate and solve a real-world dilemma from logistics, scheduling, finance, or sustainability using quantum combinatorial optimization.
- **Quantum Core Mandate:** The optimization workflow must translate the real-world dilemma into binary decision variables, formulate an objective with constraints (QUBO/penalty formulation), map to an Ising Cost Hamiltonian ($H_C$), and execute using Qiskit algorithms/primitives (QAOA, VQE, or parameterized circuits via `StatevectorSampler` / `StatevectorEstimator`).
- **Benchmarking Requirement:** Compare quantum solutions against classical baselines (brute-force exact search for small instances, classical greedy heuristics), analyzing **Approximation Ratio** and **Feasibility Yield**.

---

## 2. Requirements Traceability Matrix

| ID | Requirement | Source File & Section | Planned Implementation | Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Track 2 Objective: Formulate real-world dilemma as binary optimization/QUBO | `HACKATHON_GUIDE.md` §2 (Track 2) | Green Energy Asset Selection ($n$ assets, budget $B$, return, covariance risk, carbon impact) | Mathematical model review & test checks | Verified |
| **REQ-02** | Qiskit Quantum Core: Qiskit must power the quantum circuit, gates, Hamiltonian, and state evolution | `HACKATHON_GUIDE.md` §2 ("The Golden Rule") | `qiskit.quantum_info.SparsePauliOp`, `QAOAAnsatz`, `StatevectorEstimator`, `StatevectorSampler` | Unit tests importing Qiskit 1.0+ | Verified |
| **REQ-03** | Use Official Hackathon Template Structure | `HACKATHON_GUIDE.md` §3, `README.md` §1-7 | Submission repository preserves and populates template sections 1 to 7 without altering headings | Markdown lint / manual section audit | Verified |
| **REQ-04** | Commit Window Compliance: Commits strictly between Oct 10, 2026 7:05 PM and Oct 11, 2026 7:05 PM | `HACKATHON_GUIDE.md` §1, §3, §6 | Git commit logs strictly audited; commits authored within window; staged carefully | Git history inspection (`git log`) | Verified |
| **REQ-05** | Jupyter Notebook Deliverable: Runnable notebooks with outputs displayed | `README.md` line 8, `HACKATHON_GUIDE.md` §3 | `notebooks/solution.ipynb` executed end-to-end with generated plots, tables, and stdout saved | JSON cell inspection (`outputs` non-empty) | Verified |
| **REQ-06** | Classical Baseline Comparison | `HACKATHON_GUIDE.md` §2, `track-2-optimization/README.md` §3 | Classical brute-force enumeration ($2^n$) + classical greedy heuristic | Unit tests & comparison benchmark logs | Verified |
| **REQ-07** | Performance Metrics: Approximation Ratio ($C_{\text{QAOA}}/C_{\text{opt}}$) & Feasibility Yield | `track-2-optimization/README.md` §3 | Metric functions computed in `qaoa_solver.py` across depth $p$ and penalty $\lambda$ | Automated experiment runner & plotted curves | Verified |
| **REQ-08** | Video Presentation Deliverable: <= 10 min, public/unlisted link, >= 3-4 min live demo | `HACKATHON_GUIDE.md` §4 | Comprehensive video demo script and recording checklist in `docs/demo-script.md` | Script audit & timing checklist | Verified |
| **REQ-09** | Hardware & Simulator Restrictions: Local simulation permitted | `track2_optimization_QAOA.ipynb` §move, `requirements.txt` | Local noiseless statevector simulation (`StatevectorEstimator`, `StatevectorSampler`) | Unit tests execute locally without API key | Verified |
| **REQ-10** | No Secrets / API Keys in Git | Master Directive §6, §16, `.gitignore` §3 | `.gitignore` excludes tokens/keys; local simulator used; no hardcoded credentials | Git status check and grep scan for keys | Verified |
| **REQ-11** | Critical Reflection on Limitations & NISQ Reality | `README.md` §6, `HACKATHON_GUIDE.md` §5 | Dedicated `docs/limitations.md` and README §6 covering noise, depth, SWAP gates, and scalability | Document review | Verified |
| **REQ-12** | Dependency Configuration | `qff26-reference/requirements.txt` | `qiskit>=1.0.0`, `qiskit-aer>=0.14.0`, `rustworkx`, `scipy`, `numpy`, `matplotlib`, `pytest` | Virtual environment validation | Verified |

---

## 3. Detailed Scope & Constraints Evaluation

### 3.1. Technical Stack Rules
- **Permitted Tools:** Qiskit 1.0+, SciPy, NumPy, Matplotlib, Rustworkx, NetworkX.
- **Quantum Mechanics:** Superposition via Hadamard / $|+\rangle^{\otimes n}$, Entanglement via $ZZ$ cost gates, Interference via $X$ mixer gates, Measurement collapse into classical bitstrings.
- **Evaluation Criteria:**
  1. *Quantum Rigor & Authenticity:* Circuit must construct true quantum operators, not mock pseudo-random numbers.
  2. *Working Implementation & Live Demo:* Runnable CLI, modular library, reproducible scripts, and verified notebook.
  3. *Problem Formulation & Originality:* Must go beyond basic Max-Cut to solve a constrained real-world selection dilemma.
  4. *Presentation Clarity & Critical Understanding:* Clear mathematical derivations and candid discussion of NISQ hardware limits.

---

## 4. External References Cited

1. **Farhi, E., Goldstone, J., & Gutmann, S.** (2014). *A Quantum Approximate Optimization Algorithm*. arXiv:1411.4028 [quant-ph].
2. **IBM Quantum Documentation:** *Quantum Approximate Optimization Algorithm Tutorial* (Accessed Oct 11, 2026). URL: https://quantum.cloud.ibm.com/docs/tutorials/quantum-approximate-optimization-algorithm
3. **Qiskit Optimization Documentation:** *Converters for Quadratic Programs & Portfolio Optimization* (Accessed Oct 11, 2026). URL: https://qiskit-community.github.io/qiskit-optimization/
4. **Sachdeva et al.** (2024). *Quantum optimization on a 127-qubit gate-model IBM quantum computer*. arXiv:2406.01743 [quant-ph].
