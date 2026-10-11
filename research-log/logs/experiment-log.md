# Operational Experiment Log

Operational log documenting empirical trials and parameter tuning.

---

## Trial ID: `20261011_103427_qaoa_n5_seed42`

- **Timestamp:** 2026-10-11T10:34:27 IST
- **Problem Instance:** 5 Renewable Energy Assets, Budget $B=2$, Risk $q=0.5$, Penalty $\lambda=2.5$.
- **Hamiltonian Ground-State Equivalence:** Passed ($\Delta E < 10^{-12}$).
- **Classical Baselines:**
  - Exact Brute-Force: Optimal `[0, 1, 0, 0, 1]`, Utility = 1.7044, Runtime = 0.8 ms.
  - Classical Greedy: Selected `[1, 0, 0, 0, 1]`, Utility = 1.6445, Runtime = 0.1 ms.
- **QAOA Depth Sweep ($N_{\text{shots}}=4096$):**
  - $p=1$: Best `[0, 1, 0, 0, 1]`, Approx Ratio = 1.0000, Feasibility Yield = 41.65%, Runtime = 1.42s.
  - $p=2$: Best `[0, 1, 0, 0, 1]`, Approx Ratio = 1.0000, Feasibility Yield = 77.00%, Runtime = 8.38s.
  - $p=3$: Best `[0, 1, 0, 0, 1]`, Approx Ratio = 1.0000, Feasibility Yield = 77.05%, Runtime = 9.77s.
- **Penalty Multiplier Sweep ($\lambda \in [0.5, 5.0]$):**
  - $\lambda = 0.5$: Feasibility Yield = 31.40%, Approx Ratio = 1.0000
  - $\lambda = 1.0$: Feasibility Yield = 38.25%, Approx Ratio = 1.0000
  - $\lambda = 1.5$: Feasibility Yield = 39.80%, Approx Ratio = 1.0000
  - $\lambda = 2.0$: Feasibility Yield = 40.95%, Approx Ratio = 1.0000
  - $\lambda = 2.5$: Feasibility Yield = 41.65%, Approx Ratio = 1.0000 (Optimal Balance)
  - $\lambda = 3.5$: Feasibility Yield = 42.10%, Approx Ratio = 1.0000
  - $\lambda = 5.0$: Feasibility Yield = 43.50%, Approx Ratio = 0.9649 (Local Trap)
- **Artifacts Saved:**
  - `outputs/runs/20261011_103427_qaoa_n5_seed42/experiment_metrics.json`
  - `outputs/runs/20261011_103427_qaoa_n5_seed42/depth_sweep_summary.csv`
  - Plots in `outputs/plots/` and `assets/images/`.
