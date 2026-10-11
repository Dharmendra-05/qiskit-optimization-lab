# Comprehensive Experiment Log & Benchmark Analysis

**Run ID:** `20261011_103427_qaoa_n5_seed42`  
**Execution Timestamp:** October 11, 2026 10:34:27 IST  
**Environment:** Python 3.12.13 | Qiskit 2.5.2 | Qiskit Aer 0.17.2 | SciPy 1.18.1  
**Execution Backend:** Local Statevector Simulation (`StatevectorEstimator` & `StatevectorSampler`)  
**Hardware:** Local x86_64 Workstation (Deterministic seeded execution, `seed=42`)

---

## 1. Problem Instance Specification

The primary benchmark evaluates a 5-qubit constrained renewable energy portfolio dilemma:
- **Number of Candidate Assets ($n$):** 5
- **Budget Target ($B$):** 2 assets (strictly $\sum_{i=0}^4 x_i = 2$)
- **Risk Aversion Factor ($q$):** 0.5
- **Default Penalty Multiplier ($\lambda$):** 2.5
- **Classical Search Space ($2^n$):** 32 total bitstrings
- **Feasible Solution Subspace ($\binom{5}{2}$):** 10 feasible bitstrings

### Asset Universe:
| Asset ID | Asset Name | Energy Category | Expected Yield ($r_i$) | CO2 Offset ($t/\text{yr}$) |
| :---: | :--- | :--- | :---: | :---: |
| 0 | Utility Solar Farm A | Solar PV | 0.85 | 95.0 |
| 1 | Offshore Wind Array B | Offshore Wind | 0.92 | 120.0 |
| 2 | Lithium-Ion BESS C | Battery Storage | 0.65 | 60.0 |
| 3 | Biomass Cogen Plant D | Biomass | 0.70 | 75.0 |
| 4 | Geothermal Plant E | Geothermal | 0.88 | 110.0 |

---

## 2. Hamiltonian Construction & Mathematical Proof

The upper-triangular QUBO matrix was constructed and mapped via $x_i = \frac{I - Z_i}{2}$ to an Ising Cost Hamiltonian:
- **Operator Structure:** 5 qubits, 15 Pauli strings (10 pairwise $ZZ$ terms, 5 single-qubit $Z$ terms, and 1 scalar identity offset $c_0 \cdot I$).
- **Formal Verification:** Diagonal operator elements were compared against all $2^5 = 32$ classical state costs:
  $$\max_{x \in \{0, 1\}^5} |\langle x | \hat{H}_C | x \rangle - C(x)| < 1.0 \times 10^{-12}$$
  **Status: PASSED (Exact numerical equivalence established).**

---

## 3. Benchmark Comparison: Classical vs. Quantum

| Solver Method | Selected Portfolio Bitstring | Assets Funded | Markowitz Utility $\mathcal{U}(x)$ | QUBO Cost $C(x)$ | Approximation Ratio ($\alpha$) | Feasibility Yield ($Y_{\text{feas}}$) | Runtime (seconds) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Exact Brute-Force** | `[0, 1, 0, 0, 1]` | Offshore Wind + Geothermal | **1.7044** | **-1.7044** | **1.0000** | 100.0% (Exhaustive) | 0.0008 s |
| **Greedy Heuristic** | `[1, 0, 0, 0, 1]` | Solar PV + Geothermal | 1.6445 | -1.6445 | 0.9649 | 100.0% (Enforced) | 0.0001 s |
| **QAOA ($p=1$)** | `[0, 1, 0, 0, 1]` | Offshore Wind + Geothermal | **1.7044** | **-1.7044** | **1.0000** | **41.65%** | 1.4218 s |
| **QAOA ($p=2$)** | `[0, 1, 0, 0, 1]` | Offshore Wind + Geothermal | **1.7044** | **-1.7044** | **1.0000** | **77.00%** | 8.3765 s |
| **QAOA ($p=3$)** | `[0, 1, 0, 0, 1]` | Offshore Wind + Geothermal | **1.7044** | **-1.7044** | **1.0000** | **77.05%** | 9.7670 s |

---

## 4. Systematic Depth Scaling Analysis ($p \in \{1, 2, 3\}$)

```
Depth (p)   Approximation Ratio   Feasibility Yield (%)   COBYLA Iterations   Runtime (s)
   1              1.0000                 41.65%                  52             1.42 s
   2              1.0000                 77.00%                 104             8.38 s
   3              1.0000                 77.05%                 120             9.77 s
```

### Key Analytical Takeaways:
1. **Dramatic Jump in Feasibility:** Increasing depth from $p=1$ to $p=2$ nearly doubles the feasibility yield (from $41.65\%$ to $77.00\%$), demonstrating that a 2-layer alternating unitary allows constructive interference to strongly concentrate probability mass onto the budget-satisfying subspace $\binom{5}{2}$.
2. **Optimum Preservation:** In all three circuit depths, the most probable feasible candidate solution is identically the global optimum `[0, 1, 0, 0, 1]`, matching the brute-force ground truth.
3. **Diminishing Returns at $p=3$:** Moving from $p=2$ to $p=3$ increases classical simulation time without a commensurate increase in feasibility yield on this 5-qubit instance, identifying $p=2$ as the Pareto-optimal operating point.

---

## 5. Constraint Penalty Multiplier ($\lambda$) Sweep Analysis

Conducted at fixed depth $p=1$, 2048 shots, with $\lambda \in [0.5, 5.0]$:

| Penalty Multiplier ($\lambda$) | Feasibility Yield (%) | Approximation Ratio ($\alpha$) | Best Feasible Sample Found | Feasibility Status |
| :---: | :---: | :---: | :---: | :---: |
| **0.5** | 31.40% | 1.0000 | `[0, 1, 0, 0, 1]` | True |
| **1.0** | 38.25% | 1.0000 | `[0, 1, 0, 0, 1]` | True |
| **1.5** | 39.80% | 1.0000 | `[0, 1, 0, 0, 1]` | True |
| **2.0** | 40.95% | 1.0000 | `[0, 1, 0, 0, 1]` | True |
| **2.5** | **41.65%** | **1.0000** | `[0, 1, 0, 0, 1]` | **True (Optimal)** |
| **3.5** | 42.10% | 1.0000 | `[0, 1, 0, 0, 1]` | True |
| **5.0** | 43.50% | 0.9649 | `[1, 0, 0, 0, 1]` | True (Suboptimal local trap) |

### Observation:
When $\lambda$ is too small ($\lambda \le 1.0$), infeasible states have insufficient energy penalties, leading to lower feasibility yields ($< 38\%$). Conversely, when $\lambda$ is excessively high ($\lambda = 5.0$), the penalty term overwhelms the underlying Markowitz utility function, creating steep energy barriers that can trap gradient-free optimizers into suboptimal local minima (`[1, 0, 0, 0, 1]` with $\alpha = 0.9649$). The calibrated operating range $\lambda \in [2.0, 3.5]$ delivers the best balance of constraint enforcement and objective fidelity.

---

## 6. Generated Visual Artifacts

The following figures were generated from the actual run metrics and are archived in `outputs/plots/` and `assets/images/`:
1. `convergence_trajectory.png`: COBYLA expected energy minimization curve.
2. `solution_distribution.png`: Histogram of sampled candidate bitstrings with feasible/infeasible color coding.
3. `depth_scaling_comparison.png`: Dual-axis plot of Approximation Ratio and Feasibility Yield vs circuit depth $p$.
4. `penalty_sweep_analysis.png`: Feasibility Yield vs constraint penalty weight $\lambda$.
5. `solver_utility_comparison.png`: Comparative bar chart of portfolio utility across all solvers.
6. `outputs/circuits/qaoa_circuit_p1.png`: Gate-level decomposed circuit diagram.
