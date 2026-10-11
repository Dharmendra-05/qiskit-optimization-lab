# Quantum Resource Optimizer: Constrained Green Energy Asset & Portfolio Allocation with QAOA

## Project Metadata

* **Project Title:** Quantum Resource Optimizer: Constrained Green Energy Asset & Portfolio Allocation with QAOA
* **Team Name:** Quantum Grid Innovators
* **Chosen Track:** Track 2: Open-Domain Optimization & Real-World Solvers
* **Video Presentation Link:** `https://youtu.be/PLACEHOLDER_QFF26_TRACK2` *(Update with final unlisted YouTube / Loom video URL prior to form submission)*
* **Live Demo Timestamp in Video:** `02:45` *(Terminal CLI execution and live solution convergence starts at 02:45)*

### Team Members (Max 4 members)
| Name | Email | GitHub Username |
| :--- | :--- | :--- |
| Dharmendra P. | dharmendrapradhan737@gmail.com | `@Dharmendra-05` |

---

## 1. Project Overview & Motivation

* **Summary (3–4 sentences):**  
  The Quantum Resource Optimizer solves the critical real-world challenge of capital allocation across competing clean energy infrastructure projects under strict budgetary and risk constraints. We translate the Markowitz mean-variance portfolio selection problem into a Quadratic Unconstrained Binary Optimization (QUBO) model with an exact quadratic budget penalty. Using modern Qiskit 1.0+ and 2.0+ primitives (`QAOAAnsatz`, `StatevectorEstimator`, and `StatevectorSampler`), the system searches the combinatorial space of renewable energy assets (Solar PV, Offshore Wind, Battery Storage, Biomass, Geothermal) to identify the optimal budget-compliant portfolio.

* **Why this problem / game?**  
  As the global clean-energy transition accelerates, energy investment authorities face the multi-billion dollar dilemma of selecting which renewable projects to fund from a large catalog under fixed capital expenditure limits. Renewable assets suffer from weather intermittency and generation volatility that must be balanced through covariance modeling. This problem directly addresses the official Track 2 portfolio-selection challenge from the hackathon reference materials, providing a rigorous, pedagogical vehicle to study how quantum algorithms handle hard combinatorial constraints through variational penalty multipliers.

---

## 2. Quantum Architecture & Mechanics

* **Core Quantum Principles Used:**  
  * **Quantum Superposition:** All $N$ qubits are initialized into the equal superposition state $|+\rangle^{\otimes N} = \frac{1}{\sqrt{2^N}} \sum_{x \in \{0, 1\}^N} |x\rangle$ using single-qubit Hadamard ($H$) gates, exploring all $2^N$ candidate project portfolios simultaneously.
  * **Entanglement via Cost Hamiltonian:** Two-qubit $ZZ$ rotations synthesize the pairwise asset covariance interactions and quadratic budget penalty terms, creating quantum entanglement across candidate asset selections.
  * **Quantum Interference:** The transverse-field mixer Hamiltonian ($\sum X_i$) induces transitions between states, creating constructive interference on low-energy feasible configurations and destructive interference on high-penalty infeasible states.
  * **Measurement Collapse:** Projective measurement in the computational basis collapses the optimized variational quantum state into classical bitstrings representing specific portfolio funding allocations.

* **How the Quantum Circuit is Integrated:**  
  The classical problem minimizes $C(x) = -\text{Utility}(x) + \lambda (\sum x_i - B)^2$. Using the affine spin mapping $x_i = \frac{I - Z_i}{2}$, this problem maps to a diagonal Cost Hamiltonian $\hat{H}_C = \sum_{i < j} J_{ij} Z_i Z_j + \sum_i h_i Z_i + c_0 I$.
  We construct the parameterized quantum trial state using Qiskit's `QAOAAnsatz(cost_operator=H_C, reps=p)`. A classical optimizer (COBYLA) iteratively queries the Qiskit `StatevectorEstimator` to compute the expected energy $\langle \hat{H}_C \rangle$ and tune rotation angles $(\vec{\gamma}, \vec{\beta})$. The optimized circuit is then sampled using `StatevectorSampler` to extract candidate portfolios.

* **Circuit Details:**  
  * **Number of Qubits:** 5 qubits (configurable from 4 to 10 qubits).
  * **Key Gates Used:** $H$ (superposition), $RZ$ (single-qubit cost phase), $\text{CNOT} \to RZ \to \text{CNOT}$ (two-qubit $ZZ$ entangling cost gates), $RX$ (transverse mixer), and computational basis Measurement.
  * **Primitives Used:** Qiskit `StatevectorEstimator` (for noiseless expectation value tuning) and `StatevectorSampler` (for 4096-shot projective bitstring sampling).
  * **Other Technologies Used:** Python 3.12, SciPy (`scipy.optimize.minimize` with COBYLA), NumPy, Matplotlib, Rustworkx, and Pytest.

```python
from qiskit.circuit.library import QAOAAnsatz
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from scipy.optimize import minimize
from quantum_optimizer.hamiltonian import build_cost_hamiltonian

# Construct diagonal Cost Hamiltonian from problem instance
hamiltonian, offset = build_cost_hamiltonian(problem, include_offset=True)

# Build parameterized QAOA circuit
ansatz = QAOAAnsatz(cost_operator=hamiltonian, reps=1)
estimator = StatevectorEstimator()

# Classical optimization loop with COBYLA
def cost_func(params):
    return float(estimator.run([(ansatz, hamiltonian, params)]).result()[0].data.evs)

result = minimize(cost_func, x0=[0.5, 0.5], method="COBYLA", options={"maxiter": 100})

# Sample candidate bitstrings from optimal circuit
measured_circuit = ansatz.copy()
measured_circuit.measure_all()
sampler = StatevectorSampler()
counts = sampler.run([(measured_circuit, result.x)], shots=4096).result()[0].data.meas.get_counts()
```

---

## 3. Repository Structure & How to Run

### Project Structure
```text
quantum-resource-optimizer/
├── README.md               # Standardized hackathon submission document
├── pyproject.toml          # Package configuration and test settings
├── requirements.txt        # Python dependency manifest
├── LICENSE                 # MIT License
├── AGENTS.md               # Multi-agent operating guidelines and security policy
├── METADATA.md             # Project, track, team, and model metadata
├── PROJECT_STATUS.md       # Operational milestone tracking document
├── src/                    # Core source code package
│   ├── main.py             # Top-level executable CLI entry point
│   └── quantum_optimizer/  # Modular Python package
│       ├── __init__.py     # Package exports
│       ├── problem.py      # Renewable asset & constrained problem definition
│       ├── hamiltonian.py  # QUBO matrix & SparsePauliOp Ising mapping
│       ├── classical_solvers.py # Exact brute-force and greedy baselines
│       ├── qaoa_solver.py  # Qiskit QAOA optimization and sampling engine
│       ├── experiment_runner.py # Reproducible benchmark sweep runner
│       └── visualization.py# Matplotlib figures and plotting routines
├── tests/                  # Automated pytest verification test suite
│   ├── test_problem.py     # Analytical hand calculations & input validation
│   ├── test_hamiltonian.py # Hamiltonian equivalence mathematical proofs
│   └── test_solvers.py     # Classical, greedy, and QAOA execution tests
├── notebooks/              # Jupyter notebook deliverables with executed outputs
│   └── solution.ipynb      # Complete runnable notebook with rich figures
├── docs/                   # Exhaustive research documentation
│   ├── requirements-analysis.md # Traceability matrix of hackathon requirements
│   ├── topic-selection.md  # 10-criteria topic scoring & problem justification
│   ├── fundamentals.md     # Plain-language guide with equations and metrics
│   ├── architecture.md     # Component diagrams and data flow design
│   ├── mathematical-formulation.md # Full algebraic derivations and proofs
│   ├── algorithm.md        # QAOA operator details and parameter tuning
│   ├── experiment-log.md   # Systematic run logs, CSV data, and depth sweeps
│   ├── limitations.md      # Scientific reflection on NISQ noise & scaling
│   └── demo-script.md      # 8-minute presentation video recording script
├── research-log/           # 36-page modular academic LaTeX research monograph
│   ├── main.tex            # Master XeLaTeX document (Times New Roman typography)
│   ├── README.md           # Reproducible build instructions (xelatex + bibtex)
│   ├── frontmatter/        # Title page and abstract
│   ├── chapters/           # 9 academic chapters (background, math, results, NISQ realities)
│   ├── appendices/         # Verified code excerpts and reproducibility commands
│   ├── tables/             # LaTeX tables (asset catalog, benchmark summary, sweeps)
│   ├── code/               # Exact Python code listings for Hamiltonian & decoding
│   ├── figures/            # Vector and high-resolution monograph figures
│   └── references/         # Primary literature BibTeX database (13 verified entries)
├── outputs/                # Experiment artifacts
│   ├── plots/              # High-resolution benchmark figures
│   ├── runs/               # Timestamped run logs (JSON metrics + CSV summaries)
│   └── circuits/           # Decomposed QAOA quantum circuit diagrams
└── references/             # Hackathon reference guides and BibTeX sources
    ├── README.md           # Curated literature catalog
    └── sources.bib         # BibTeX citations
```

### Installation & Execution Instructions

> 💡 **Environment Recommendation:** We recommend Python 3.10 to 3.12:
> ```bash
> python -m venv .venv
> .venv\Scripts\activate      # On Windows
> # source .venv/bin/activate  # On Linux / macOS
> pip install -r requirements.txt
> ```

1. **Clone the repository:**
   ```bash
   git clone git@github.com:Dharmendra-05/qiskit-optimization-lab.git
   cd quantum-resource-optimizer
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the project / demo:**
   ```bash
   # Run the CLI solver on a 5-asset renewable portfolio:
   python src/main.py --num-assets 5 --budget 2 --p 1 --shots 2048 --save-plots

   # Run automated unit tests:
   pytest -v tests/

   # Run the comprehensive benchmark experiment runner:
   python -m quantum_optimizer.experiment_runner

   # Or open the executed Jupyter Notebook:
   jupyter notebook notebooks/solution.ipynb
   ```

---

## 4. Implementation Walkthrough & Live Demo

* **Walkthrough of Optimization Pipeline:**  
  1. **Asset Universe Generation:** A 5-asset portfolio is instantiated with realistic generation yields ($r_i$) and a positive semi-definite intermittency covariance matrix ($\Sigma$).
  2. **Ground Truth Computation:** The classical brute-force solver exhaustively evaluates all $2^5 = 32$ configurations, identifying the exact optimum `[0, 1, 0, 0, 1]` (Offshore Wind + Geothermal) with optimal utility $\mathcal{U}^* = 1.7044$.
  3. **Hamiltonian Synthesis & Verification:** The QUBO problem is converted into a 5-qubit `SparsePauliOp` Cost Hamiltonian. An automated mathematical proof verifies that $\langle x | \hat{H}_C | x \rangle == C(x)$ with zero error tolerance.
  4. **QAOA Variational Optimization:** `QAOAAnsatz` is instantiated with depth $p=1$. Classical COBYLA minimizes expected energy across $\sim 50$ iterations via `StatevectorEstimator`.
  5. **Sampling & Little-Endian Readout:** 2048 measurement shots are acquired via `StatevectorSampler`. Bitstrings are reversed from Qiskit's little-endian convention and evaluated for feasibility ($\sum x_i == 2$).
  6. **Candidate Output:** QAOA returns `[0, 1, 0, 0, 1]`, achieving an **Approximation Ratio of 1.0000** and a **Feasibility Yield of 43.0%** (for this 2048-shot interactive CLI execution; 41.65% under the 4096-shot systematic benchmark suite in Section 5).

* **Key Screenshots / Terminal Output:**  
  ```text
  ======================================================================
        QUANTUM RESOURCE OPTIMIZER: GREEN ENERGY ALLOCATION
        Qiskit Fall Fest 2026 -- Track 2 Optimization Solver
  ======================================================================
  Configuration: Assets=5, Budget=2, p=1, Shots=2048, Seed=42

  [1/4] Generating renewable energy asset portfolio...
    * Asset 0: Utility Solar Farm A      (Solar PV) Expected Yield=0.85, CO2=95t
    * Asset 1: Offshore Wind Array B     (Offshore Wind) Expected Yield=0.92, CO2=120t
    * Asset 2: Lithium-Ion BESS C        (Battery Storage) Expected Yield=0.65, CO2=60t
    * Asset 3: Biomass Cogen Plant D     (Biomass) Expected Yield=0.70, CO2=75t
    * Asset 4: Geothermal Plant E        (Geothermal) Expected Yield=0.88, CO2=110t

  [2/4] Executing Classical Benchmarks...
    [Exact Brute-Force] Optimal: [0, 1, 0, 0, 1] | Utility: 1.7044 | Cost: -1.7044 (Time: 0.8ms)
    [Greedy Heuristic]  Picked:  [1, 0, 0, 0, 1] | Utility: 1.6445 | Cost: -1.6445 (Time: 0.0ms)

  [3/4] Solving via QAOA (depth p=1, shots=2048)...
    Optimal QAOA angles: gamma=[2.978], beta=[1.1314]
    Minimum expected cost: 0.9042
    Best sampled assignment: [0, 1, 0, 0, 1] (Feasible: True)
    Best sampled utility:    1.7044
    Approximation Ratio:     1.0000
    Feasibility Yield:       43.02%
    Execution Runtime:       1.39s
  ```

---

## 5. Classical vs. Quantum Comparison

* **Classical Baseline / Counterpart:**  
  We implemented two distinct classical baselines:
  1. **Exact Brute-Force Solver:** Evaluates all $2^N$ bitstrings to determine the provable global optimum $\mathcal{U}^* = 1.7044$ (`[0, 1, 0, 0, 1]`).
  2. **Classical Greedy Heuristic:** Ranks assets by their individual return-to-volatility ratio ($r_i / \sqrt{\Sigma_{ii}}$) and selects the top $B$ assets. It selects `[1, 0, 0, 0, 1]` with utility $\mathcal{U} = 1.6445$ (missing the global optimum due to ignoring cross-asset covariance interactions).

* **Comparative Analysis:**  
  | Metric / Solver | Exact Brute-Force | Classical Greedy | QAOA ($p=1$) | QAOA ($p=2$) | QAOA ($p=3$) |
  | :--- | :---: | :---: | :---: | :---: | :---: |
  | **Best Portfolio** | `[0, 1, 0, 0, 1]` | `[1, 0, 0, 0, 1]` | `[0, 1, 0, 0, 1]` | `[0, 1, 0, 0, 1]` | `[0, 1, 0, 0, 1]` |
  | **Utility Score $\mathcal{U}(x)$** | **1.7044** | 1.6445 | **1.7044** | **1.7044** | **1.7044** |
  | **Approximation Ratio ($\alpha$)** | **1.0000** | 0.9649 | **1.0000** | **1.0000** | **1.0000** |
  | **Feasibility Yield ($Y_{\text{feas}}$)** | 100.0% | 100.0% | **41.65%** | **77.00%** | **77.05%** |
  | **Runtime** | 0.8 ms | 0.1 ms | 1.42 s | 8.38 s | 9.77 s |

  *Takeaway:* The classical greedy heuristic fails to find the global optimum because it ignores pairwise covariance coupling. QAOA successfully accounts for full two-qubit covariance entanglement and recovers the exact global optimum. As circuit depth increases from $p=1$ to $p=2$, the feasibility yield dramatically jumps from **41.65% to 77.00%**, concentrating quantum probability amplitude squarely on the budget-satisfying subspace $\binom{5}{2}$.

---

## 6. Performance, Results & Limitations

* **Key Results & Observations:**  
  1. **Depth Scaling Benefit:** Increasing circuit depth from $p=1$ to $p=2$ nearly doubles the feasibility yield (from $41.65\%$ to $77.00\%$), demonstrating constructive quantum interference on constrained subspaces.
  2. **Penalty Multiplier ($\lambda$) Dynamics:** When $\lambda < 1.0$, feasibility yields drop below $35\%$ due to insufficient constraint punishment. When $\lambda = 5.0$, steep penalty gradients trap COBYLA in suboptimal local states. A calibrated value of $\lambda = 2.5$ yields optimal balance.
  3. **High-Fidelity Convergence:** Across all depths, the most probable feasible state measured is identically the true global optimum.

* **Critical Reflection on Limitations:**  
  * **No Quantum Advantage on Small Instances:** Classical brute force solves $N=5$ in under 1 millisecond. Statevector simulation takes 1.4 seconds. Simulating small quantum circuits classically demonstrates algorithmic correctness, not commercial speedup.
  * **Physical Quantum Noise & Gate Fidelity:** Real transmon QPUs suffer from gate errors ($\approx 1\%$ per CNOT) and finite decoherence times ($T_1, T_2 \sim 200\,\mu\text{s}$). For an all-to-all connected $N$-qubit covariance graph, each QAOA layer requires $\binom{N}{2}$ two-qubit gates. On larger systems, gate error accumulation will rapidly decohere the circuit unless error suppression (dynamical decoupling, Pauli twirling) is applied.
  * **Hardware Topology & SWAP Routing:** Real IBM hardware (Heavy-Hex layout) lacks all-to-all connectivity. Compiling non-local $ZZ$ interactions requires inserting SWAP gates, tripling physical CNOT depth.
  * **Trainability & Barren Plateaus:** Variational landscapes can exhibit vanishing gradients at large qubit counts, demanding smarter parameter heuristics or warm-starting.

---

## 7. References & Acknowledgments

* **References:**
  * Farhi, E., Goldstone, J., & Gutmann, S. (2014). *A Quantum Approximate Optimization Algorithm*. [arXiv:1411.4028](https://arxiv.org/abs/1411.4028).
  * Markowitz, H. (1952). *Portfolio Selection*. *The Journal of Finance*, 7(1), 77–91.
  * Lucas, A. (2014). *Ising formulations of many NP problems*. *Frontiers in Physics*, 2, 5.
  * Sachdeva et al. (2024). *Quantum optimization on a 127-qubit gate-model IBM quantum computer*. [arXiv:2406.01743](https://arxiv.org/abs/2406.01743).
  * IBM Quantum Documentation: [QAOA End-to-End Tutorial](https://quantum.cloud.ibm.com/docs/tutorials/quantum-approximate-optimization-algorithm).
  * Tirado, Benjamin (2026). *Combinatorial Optimization with QAOA: Max-Cut*, BasQ Qiskit Fall Fest 2026 Starter Notebook.

* **Acknowledgments & Tooling:**  
  * Developed for **Qiskit Fall Fest 2026**, hosted by **IIIT Kottayam**.
  * Primary research, implementation, and benchmarking assisted by **Gemini 3.8 Flash High in Google Antigravity**.
  * Git staging and repository skill workflow prepared via **OpenCode**.
  * Project open-sourced under the **MIT License**.
