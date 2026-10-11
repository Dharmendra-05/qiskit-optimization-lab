# Demonstration Video Presentation Script & Recording Guide

**Event:** Qiskit Fall Fest 2026 — Track 2: Open-Domain Optimization  
**Project:** Quantum Resource Optimizer: Constrained Green Energy Asset Allocation  
**Target Duration:** 7:30 to 8:30 minutes (Strict limit: under 10:00 minutes)  
**Presenter:** Dharmendra P.

---

## 1. Video Recording Checklist & Scene Schedule

| Timestamp | Segment Title | Visual Display on Screen | Key Spoken Points & Objective |
| :---: | :--- | :--- | :--- |
| **00:00 – 01:15** | Problem Motivation & Dilemma | Title slide / Clean Energy Infographic / Problem overview | Introduce the real-world clean energy capital allocation dilemma under a strict budget constraint. |
| **01:15 – 02:45** | Mathematical Formulation & QUBO | `docs/mathematical-formulation.md` & equations | Explain binary variables $x_i$, Markowitz utility, quadratic budget penalty $\lambda(\sum x_i - B)^2$, and Ising mapping $x_i = \frac{I - Z_i}{2}$. |
| **02:45 – 04:15** | Live Execution: CLI & Benchmarks | Terminal running `python src/main.py --num-assets 5 --budget 2 --p 1 --shots 2048` | **LIVE DEMO:** Show real terminal run executing classical brute force, greedy heuristic, and QAOA in 1.4 seconds. |
| **04:15 – 05:45** | Jupyter Notebook Walkthrough | Browser displaying `notebooks/solution.ipynb` with executed cells and rendered plots | Walk through interactive cells: asset catalog, SparsePauliOp inspection, Hamiltonian equivalence verification, and bitstring sampling distribution. |
| **05:45 – 07:00** | Visual Results & Empirical Analysis | Displaying `outputs/plots/depth_scaling_comparison.png` and `penalty_sweep_analysis.png` | Highlight key findings: Feasibility yield jumping from 41.6% to 77.0% with depth $p=2$; Approximation ratio of 1.0000; optimal penalty calibration. |
| **07:00 – 08:00** | Unit Testing & Scientific Limitations | Terminal running `pytest -v tests/` followed by `docs/limitations.md` | Demonstrate 12 passing unit tests; critically discuss NISQ noise, gate errors, SWAP routing, and explain why this does not prove quantum advantage. |
| **08:00 – 08:30** | Conclusion & Submission Wrap-up | Repository GitHub page / Architecture diagram | Conclude with project summary, acknowledgments to Qiskit and IIIT Kottayam organizers. |

---

## 2. Word-for-Word Spoken Script

### Segment 1: Motivation & Problem Statement (00:00 – 01:15)
> "Hello everyone! Welcome to our project presentation for Qiskit Fall Fest 2026 Track 2: Open-Domain Optimization. I am Dharmendra P., and today I am excited to present the **Quantum Resource Optimizer**, an end-to-end quantum solver for constrained green energy asset and portfolio allocation using QAOA.
> 
> As governments and clean-energy funds transition toward net-zero, they face a high-stakes dilemma: how do you allocate a limited budget across competing renewable energy assets—such as Solar PV, Offshore Wind, Battery Storage, Biomass, and Geothermal—to maximize clean power generation and carbon offsets, while balancing intermittency risk and strictly obeying capital budget constraints? 
> 
> This is a constrained combinatorial optimization problem. Classical brute-force enumeration scales exponentially as $2^N$. Our goal is to formulate this dilemma as a Quadratic Unconstrained Binary Optimization model and solve it using modern Qiskit algorithms."

### Segment 2: Mathematical Formulation (01:15 – 02:45)
> "Let's examine our mathematical formulation. For $N$ candidate projects, we define binary decision variables $x_i \in \{0, 1\}$, where $x_i = 1$ denotes a funded project.
> 
> Our economic objective follows the Markowitz Mean-Variance framework: we maximize total expected yield $r^T x$, penalized by generation covariance volatility $\frac{q}{2} x^T \Sigma x$.
> 
> However, real-world problems require constraints. We have a strict capital expenditure budget requiring us to select exactly $B$ assets. On gate-model quantum computers, constraints are incorporated as quadratic penalties:
> $$C(x) = -\text{Utility}(x) + \lambda \left(\sum_{i=0}^{N-1} x_i - B\right)^2$$
> 
> By substituting $x_i = \frac{I - Z_i}{2}$, pairwise terms become two-qubit $ZZ$ interactions, and linear terms become single-qubit $Z$ rotations. This maps our dilemma into a diagonal Ising Cost Hamiltonian $\hat{H}_C = \sum J_{ij} Z_i Z_j + \sum h_i Z_i + c_0 I$. We formally proved that for all computational basis states, the expectation value $\langle x | \hat{H}_C | x \rangle$ exactly equals the classical cost function."

### Segment 3: Live Terminal Demonstration (02:45 – 04:15)
> *(Switch screen to Terminal)*
> "Now let us run the live system from our command line interface. I will execute:
> `python src/main.py --num-assets 5 --budget 2 --p 1 --shots 2048 --save-plots`
> 
> Notice how rapidly the pipeline executes:
> First, it generates our 5-asset renewable portfolio.
> Second, our classical benchmarks execute: exact brute-force search evaluates all 32 combinations in 0.8 milliseconds, identifying the global optimum as `[0, 1, 0, 0, 1]`—funding Offshore Wind and Geothermal with a utility of 1.7044. Our classical greedy heuristic selects `[1, 0, 0, 0, 1]` with utility 1.6445.
> Third, Qiskit's `StatevectorEstimator` tunes the variational parameters $\gamma$ and $\beta$ via COBYLA, and `StatevectorSampler` measures 2048 shots in 1.4 seconds.
> 
> The best sampled bitstring is `[0, 1, 0, 0, 1]`—recovering the exact global optimum with an **Approximation Ratio of 1.0000** and a **Feasibility Yield of 43.0%**!"

### Segment 4: Jupyter Notebook Walkthrough (04:15 – 05:45)
> *(Switch screen to Browser showing `notebooks/solution.ipynb`)*
> "Here is our accompanying Jupyter Notebook, `solution.ipynb`, completely executed with all cell outputs and diagrams preserved.
> 
> In Cell 4, we inspect the physical asset catalog.
> In Cell 8, we construct the `SparsePauliOp` and run our automated mathematical verification, confirming that ground state equivalence holds with zero tolerance error.
> In Cell 10, the QAOA ansatz circuit is executed, and in Cell 14, we render the parameter convergence curve and the sampled bitstring probability histogram. Notice how the green bars represent budget-compliant portfolios, with the gold star marking our optimal solution dominating the feasible distribution."

### Segment 5: Visual Results & Empirical Analysis (05:45 – 07:00)
> *(Switch screen to `outputs/plots/depth_scaling_comparison.png`)*
> "Let us look at our depth scaling analysis across QAOA depths $p=1, 2, 3$.
> At depth $p=1$, our feasibility yield is $41.65\%$. When we increase circuit depth to $p=2$, the feasibility yield dramatically jumps to $77.00\%$! This demonstrates constructive quantum interference concentrating probability amplitude directly onto the budget-satisfying subspace $\binom{5}{2}$.
> 
> In our penalty multiplier sweep across $\lambda \in [0.5, 5.0]$, we discovered that setting $\lambda$ too low ($< 1.0$) causes feasibility yield to drop below $35\%$, while setting $\lambda$ excessively high ($5.0$) creates steep energy walls that trap classical optimizers into suboptimal local minima. A calibrated penalty of $\lambda = 2.5$ provides the ideal balance."

### Segment 6: Tests & Critical Reflection on Limitations (07:00 – 08:00)
> *(Switch screen to Terminal, run `pytest -v tests/`)*
> "To ensure rigorous software quality, our test suite contains 12 unit tests verifying analytical hand calculations, matrix symmetry, little-endian bitstring decoding, Hamiltonian equivalence, and deterministic reproducibility. All 12 tests pass cleanly in under 2 seconds.
> 
> Finally, we must be scientifically candid about limitations. This project does not claim quantum advantage. A 5-qubit problem is trivial for classical computers. 
> On real physical NISQ hardware, deeper circuits suffer from two-qubit gate errors ($0.5-1\%$ per CNOT) and finite decoherence ($T_1, T_2$). Furthermore, mapping dense covariance graphs onto sparse heavy-hex IBM topologies requires inserting SWAP gates, tripling circuit depth. To achieve true industrial quantum advantage at 100+ qubits, future implementations will require constraint-preserving XY mixers, zero-noise extrapolation, and ultimately fault-tolerant error correction."

### Segment 7: Conclusion & Wrap-Up (08:00 – 08:30)
> "In summary, we have built a complete, reproducible, and verifiable quantum optimization solution for Track 2, bridging real-world sustainability dilemmas to Qiskit 1.0+ and 2.0+ primitives. All source code, documentation, benchmarks, and notebooks are available in our GitHub repository under the MIT license.
> 
> Thank you to IBM Quantum, BasQ, and IIIT Kottayam for organizing this wonderful hackathon!"

---

## 3. Screen Setup & Recording Checklist

Before starting screen recording (using OBS Studio or Loom):
- [ ] Display resolution: 1080p (1920x1080) at 30 or 60 fps.
- [ ] Terminal font size enlarged (>= 16pt) with high-contrast theme.
- [ ] Virtual environment activated: `.venv\Scripts\activate`.
- [ ] Browser window open with `notebooks/solution.ipynb` scrolled to top.
- [ ] Image viewer open with `outputs/plots/depth_scaling_comparison.png` and `penalty_sweep_analysis.png`.
- [ ] Test audio input levels to ensure clear voice recording without background hiss.
