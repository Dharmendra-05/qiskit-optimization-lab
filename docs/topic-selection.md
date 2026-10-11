# Topic Selection and Problem Justification Report
**Track:** Qiskit Fall Fest 2026 — Track 2: Open-Domain Optimization & Real-World Solvers  
**Author:** Dharmendra P. / Gemini 3.8 Flash High (Antigravity)  
**Status:** Approved & Selected

---

## 1. Candidate Comparison & Scoring Matrix

Three candidate optimization concepts were formulated and evaluated strictly against the 10 judging and execution criteria defined in the Hackathon Execution Directive. Each criterion is scored on a scale from 1 (Poor/Risky) to 10 (Excellent/Optimal).

| Evaluation Criterion | Weight | Candidate 1: Green Energy Portfolio & Resource Allocation | Candidate 2: Smart Campus Exam Scheduling | Candidate 3: Drone Hub Placement (Max-Cut) |
| :--- | :---: | :---: | :---: | :---: |
| **1. Compliance with Track 2** | 10% | **10** (Explicitly recommended in reference notebook §move & README) | **8** (Valid graph coloring problem) | **6** (Toy unconstrained example; discouraged by organizers) |
| **2. Implementation Time** | 10% | **10** (Clean $n$-qubit mapping, fits tight timeline) | **6** (Requires multi-qubit one-hot per node, high overhead) | **9** (Very quick, but too trivial) |
| **3. Mathematical Clarity** | 10% | **10** (Rigorous QUBO: linear yield, covariance risk, quadratic penalty) | **7** (Complex multi-index constraint penalties) | **8** (Simple edge-based cut Hamiltonian) |
| **4. Compatibility with Qiskit** | 10% | **10** (Seamless with `QAOAAnsatz`, `SparsePauliOp`, Estimator/Sampler) | **7** (Requires large Hilbert space transpilation) | **10** (Standard tutorial mapping) |
| **5. Classical Baseline Availability**| 10% | **10** (Exact $2^n$ brute-force + greedy heuristic + SciPy QP) | **8** (Classical DSatur heuristic) | **9** (Brute force + Goemans-Williamson) |
| **6. Ease of Testing** | 10% | **10** (Deterministic bitstring recalculation & constraint checks) | **7** (Constraint verification across time slots) | **8** (Cut edge count) |
| **7. Quality of Measurable Results** | 10% | **10** (Approximation ratio vs $p$, feasibility yield vs penalty $\lambda$) | **7** (Hard collision count) | **7** (Only cut ratio) |
| **8. Suitability for Video Demo** | 10% | **10** (Clear visual story: renewable projects, budget, clean energy trade-offs) | **8** (Conflict matrix visualization) | **7** (Abstract bipartite graph) |
| **9. Runtime & Dependency Risk** | 10% | **10** (Fast local simulation on 4–8 qubits in seconds; no external API) | **6** (Qubit explosion causes simulator timeouts) | **10** (Low qubit count) |
| **10. Explainability to Beginners** | 10% | **10** (Intuitive: "Pick $B$ green projects to maximize return & minimize risk") | **7** (Graph chromatic theory is abstract) | **7** (Graph partitioning) |
| **Total Weighted Score (out of 100)**| **100%** | **100 / 100** | **71 / 100** | **79 / 100** |

---

## 2. Selected Problem: Constrained Green Energy Resource & Portfolio Allocation

### 2.1. Why It Was Selected
1. **Official Endorsement:** In `qff26-reference/references/track-2-optimization/track2_optimization_QAOA.ipynb` section "Moving forward", the reference notebook explicitly states:
   > *"The challenge centres on a portfolio-selection problem: from a universe of assets, choose a subset that maximizes expected return while penalizing risk, subject to a budget constraint (for example, pick exactly K assets). This problem is a natural fit for QAOA... but it adds the essential ingredient of a constraint, which you must fold into the encoding (typically as a penalty term)."*
2. **Originality & Real-World Impact:** Rather than presenting an unmodified Max-Cut tutorial, this project models a vital global dilemma: allocating capital across clean energy resources (Solar PV, Offshore Wind, Battery Storage, Green Hydrogen, Biomass, Geothermal) to maximize clean energy output and carbon offsets while managing generation volatility covariance and adhering to a strict capital expenditure budget.
3. **Investigation of Quantum Constraint Penalties:** Real-world optimization requires constraints. By introducing a budget constraint penalty $\lambda (\sum x_i - B)^2$, we can analyze the interaction between penalty strength $\lambda$, circuit depth $p$, and the probability of measuring valid, feasible solutions (Feasibility Yield).

---

## 3. Problem Definition & Mathematical Formulation

### 3.1. Input Data & Assumptions
Let there be $n$ candidate renewable energy projects:
- $r = [r_0, r_1, \dots, r_{n-1}]^T$: Expected clean energy generation return / carbon offset score for each asset ($r_i > 0$).
- $\Sigma \in \mathbb{R}^{n \times n}$: Covariance matrix representing weather and generation volatility risk between assets (e.g. solar and wind may be negatively correlated, while two solar sites are positively correlated).
- $q \ge 0$: Risk aversion parameter balancing return versus covariance volatility.
- $B \in \{1, \dots, n-1\}$: Total budget constraint (number of projects to fund simultaneously).
- $\lambda > 0$: Penalty multiplier enforcing the budget constraint.

### 3.2. Binary Decision Variables
For each asset $i \in \{0, \dots, n-1\}$:
$$x_i \in \{0, 1\}$$
where $x_i = 1$ if asset $i$ is selected/funded, and $x_i = 0$ otherwise.

### 3.3. Objective Function (Markowitz Mean-Variance Model)
The classical objective to maximize is:
$$\text{Maximize } \mathcal{U}(x) = \sum_{i=0}^{n-1} r_i x_i - \frac{q}{2} \sum_{i=0}^{n-1} \sum_{j=0}^{n-1} \Sigma_{ij} x_i x_j$$
Subject to the hard budget constraint:
$$\sum_{i=0}^{n-1} x_i = B$$

### 3.4. QUBO Formulation
Converting to an unconstrained minimization problem with quadratic penalty multiplier $\lambda$:
$$C(x) = -\mathcal{U}(x) + \lambda \left(\sum_{i=0}^{n-1} x_i - B\right)^2$$
Expanding the penalty term:
$$\left(\sum_{i=0}^{n-1} x_i - B\right)^2 = \sum_{i=0}^{n-1} x_i^2 + 2 \sum_{i < j} x_i x_j - 2B \sum_{i=0}^{n-1} x_i + B^2$$
Since $x_i \in \{0, 1\}$, we have $x_i^2 = x_i$. Therefore:
$$C(x) = -\sum_{i} r_i x_i + \frac{q}{2} \sum_{i,j} \Sigma_{ij} x_i x_j + \lambda \left( (1 - 2B)\sum_{i} x_i + 2 \sum_{i < j} x_i x_j + B^2 \right)$$

### 3.5. Cost Hamiltonian Construction (Ising Mapping)
Using the transformation $x_i = \frac{I - Z_i}{2}$:
- Linear terms: $x_i \to \frac{1}{2} I - \frac{1}{2} Z_i$
- Quadratic terms: $x_i x_j \to \frac{1}{4} (I - Z_i - Z_j + Z_i Z_j)$
This produces a diagonal Cost Hamiltonian represented as a `SparsePauliOp`:
$$\hat{H}_C = \sum_{i < j} J_{ij} Z_i Z_j + \sum_i h_i Z_i + \text{offset} \cdot I$$
The ground state $|\psi_0\rangle$ of $\hat{H}_C$ corresponds to the optimal, constraint-satisfying energy allocation bitstring.

---

## 4. Expected Output & Evaluation Metrics

1. **Optimal Bitstring ($x^*$):** The binary assignment selecting exactly $B$ assets.
2. **Objective Value ($C(x)$):** The unconstrained cost value and the true economic utility $\mathcal{U}(x)$.
3. **Approximation Ratio ($\alpha$):**
   $$\alpha = \frac{\mathcal{U}(x_{\text{QAOA}})}{\mathcal{U}(x_{\text{opt}})} \quad \text{or} \quad \frac{C(x_{\text{QAOA}})}{C(x_{\text{opt}})}$$
4. **Feasibility Yield ($Y_{\text{feas}}$):**
   $$Y_{\text{feas}} = \frac{\sum_{x \in \mathcal{F}} \text{counts}(x)}{\sum_{x} \text{counts}(x)} \times 100\%$$
   where $\mathcal{F} = \{x \in \{0, 1\}^n \mid \sum x_i = B\}$.
5. **Convergence Trajectory:** Evolution of expected energy $\langle \hat{H}_C \rangle$ over COBYLA iterations.

---

## 5. Risks and Fallback Strategy

| Risk Identified | Impact | Mitigation / Fallback Plan |
| :--- | :--- | :--- |
| **High Penalty Multiplier ($\lambda$) suppresses search** | Low ground-state reach | Benchmark multiple values of $\lambda \in [0.5, 5.0]$ and visualize optimal tuning curve. |
| **COBYLA convergence gets trapped in local minima** | Suboptimal angles $(\gamma, \beta)$ | Seeded initialization + multi-start parameter search or depth-adaptive parameter transfer. |
| **Qiskit version deprecations** | Import errors | Strictly use Qiskit 1.0+ standard library classes (`qiskit.quantum_info.SparsePauliOp`, `qiskit.circuit.library.QAOAAnsatz`, `qiskit.primitives.StatevectorEstimator`). |
| **Execution time on large instances** | Slow test suite | Default unit tests and demo runs benchmark $n=4$ to $n=6$ qubits (executing in under 2 seconds), with optional scaling up to $n=10$. |

---

## 6. Primary References
1. **Markowitz, H.** (1952). *Portfolio Selection*. The Journal of Finance, 7(1), 77–91.
2. **Farhi, E., Goldstone, J., & Gutmann, S.** (2014). *A Quantum Approximate Optimization Algorithm*. arXiv:1411.4028.
3. **Lucas, A.** (2014). *Ising formulations of many NP problems*. Frontiers in Physics, 2, 5.
4. **Qiskit Finance & Optimization Community Guides:** *Portfolio Optimization using QAOA and VQE*.
