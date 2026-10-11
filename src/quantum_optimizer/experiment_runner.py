"""Reproducible Experiment Runner for Quantum Resource Optimizer.

Executes systematic benchmark sweeps, records machine-readable JSON/CSV logs,
and generates publication-quality plots in accordance with Hackathon Directive §11.
"""

from datetime import datetime
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List
import matplotlib.pyplot as plt
import numpy as np
import qiskit

import sys
import os

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from quantum_optimizer.problem import ProblemInstance
    from quantum_optimizer.classical_solvers import BruteForceSolver, GreedySolver
    from quantum_optimizer.hamiltonian import verify_hamiltonian_ground_state, build_cost_hamiltonian
    from quantum_optimizer.qaoa_solver import QAOASolver
    from quantum_optimizer.visualization import (
        plot_convergence,
        plot_sampled_distribution,
        plot_depth_comparison,
        plot_penalty_sweep,
    )
else:
    from .problem import ProblemInstance
    from .classical_solvers import BruteForceSolver, GreedySolver
    from .hamiltonian import verify_hamiltonian_ground_state, build_cost_hamiltonian
    from .qaoa_solver import QAOASolver
    from .visualization import (
        plot_convergence,
        plot_sampled_distribution,
        plot_depth_comparison,
        plot_penalty_sweep,
    )


def get_git_commit_hash() -> str:
    """Retrieves the current Git commit hash if available."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "uncommitted_workspace"


def run_comprehensive_benchmarks(
    num_assets: int = 5,
    budget: int = 2,
    seed: int = 42,
    output_base: str = "outputs",
) -> Dict[str, Any]:
    """Runs a full benchmark suite: depth sweep, penalty sweep, and baseline comparisons."""
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"{timestamp_str}_qaoa_n{num_assets}_seed{seed}"
    run_dir = os.path.join(output_base, "runs", run_id)
    plots_dir = os.path.join(output_base, "plots")
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    print(f"Starting Benchmark Run: {run_id}")
    print(f"Environment: Python {sys.version.split()[0]} | Qiskit {qiskit.__version__}")

    # 1. Instantiate problem
    problem = ProblemInstance.create_benchmark_instance(
        num_assets=num_assets,
        budget=budget,
        risk_factor=0.5,
        penalty_multiplier=2.5,
        seed=seed,
    )

    # 2. Verify Hamiltonian mathematical ground state equivalence
    hamiltonian, offset = build_cost_hamiltonian(problem)
    hamiltonian_valid = verify_hamiltonian_ground_state(problem, hamiltonian)
    print(f"Hamiltonian Ground State Verification: {'PASSED' if hamiltonian_valid else 'FAILED'}")

    # 3. Classical Baselines
    print("Running classical benchmarks...")
    bf_solver = BruteForceSolver(problem)
    bf_res = bf_solver.solve()

    gr_solver = GreedySolver(problem)
    gr_res = gr_solver.solve()

    # 4. QAOA Depth Scaling Sweep (p = 1, 2, 3)
    print("Running QAOA depth scaling sweep (p=1, 2, 3)...")
    depths = [1, 2, 3]
    depth_results = []
    approx_ratios = []
    feasibility_yields = []
    primary_qaoa_res = None

    for p in depths:
        q_solver = QAOASolver(problem, reps=p, seed=seed)
        q_res = q_solver.solve(maxiter=120, shots=4096)
        if p == 1:
            primary_qaoa_res = q_res

        depth_results.append({
            "p": p,
            "approx_ratio": q_res.approximation_ratio,
            "feasibility_yield": q_res.feasibility_yield,
            "min_cost": q_res.best_sampled_cost,
            "utility": q_res.best_sampled_utility,
            "best_assignment": q_res.best_sampled_assignment,
            "runtime_seconds": q_res.runtime_seconds,
        })
        approx_ratios.append(q_res.approximation_ratio)
        feasibility_yields.append(q_res.feasibility_yield)
        print(f"  p={p}: Approx Ratio = {q_res.approximation_ratio:.4f}, Feasibility Yield = {q_res.feasibility_yield:.2f}%, Best = {q_res.best_sampled_assignment}")

    # 5. Penalty Sweep at p=1 (lambda = 0.5 to 5.0)
    print("Running constraint penalty multiplier sweep...")
    lambdas = [0.5, 1.0, 1.5, 2.0, 2.5, 3.5, 5.0]
    penalty_results = []
    penalty_yields = []
    penalty_ar = []

    for lam in lambdas:
        prob_lam = ProblemInstance.create_benchmark_instance(
            num_assets=num_assets,
            budget=budget,
            risk_factor=0.5,
            penalty_multiplier=lam,
            seed=seed,
        )
        q_solver_lam = QAOASolver(prob_lam, reps=1, seed=seed)
        q_res_lam = q_solver_lam.solve(maxiter=80, shots=2048)

        penalty_results.append({
            "lambda": lam,
            "feasibility_yield": q_res_lam.feasibility_yield,
            "approx_ratio": q_res_lam.approximation_ratio,
            "best_feasible": q_res_lam.best_sampled_feasible,
        })
        penalty_yields.append(q_res_lam.feasibility_yield)
        penalty_ar.append(q_res_lam.approximation_ratio)

    # 6. Generate Plots
    print("Generating benchmark plots...")
    # Convergence plot
    plot_convergence(
        primary_qaoa_res.convergence_history,
        output_path=os.path.join(plots_dir, "convergence_trajectory.png"),
    )
    # Distribution plot
    plot_sampled_distribution(
        primary_qaoa_res,
        output_path=os.path.join(plots_dir, "solution_distribution.png"),
    )
    # Depth scaling plot
    plot_depth_comparison(
        depths,
        approx_ratios,
        feasibility_yields,
        output_path=os.path.join(plots_dir, "depth_scaling_comparison.png"),
    )
    # Penalty sweep plot
    plot_penalty_sweep(
        lambdas,
        penalty_yields,
        penalty_ar,
        output_path=os.path.join(plots_dir, "penalty_sweep_analysis.png"),
    )

    # Algorithm Comparison Bar Plot
    fig_comp, ax_comp = plt.subplots(figsize=(7, 4.5), dpi=150)
    solvers = ["Exact Brute-Force", "Greedy Heuristic", "QAOA (p=1)", "QAOA (p=2)", "QAOA (p=3)"]
    utilities = [
        bf_res.best_utility,
        gr_res.best_utility,
        depth_results[0]["utility"],
        depth_results[1]["utility"],
        depth_results[2]["utility"],
    ]
    bar_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#2ca02c", "#2ca02c"]
    bars = ax_comp.bar(solvers, utilities, color=bar_colors, edgecolor="black", alpha=0.85)
    ax_comp.set_ylabel("Portfolio Utility Score U(x)", fontsize=11, fontweight="bold")
    ax_comp.set_title("Solver Utility Comparison on 5-Asset Renewable Portfolio", fontsize=12, fontweight="bold", pad=12)
    ax_comp.set_xticks(range(len(solvers)))
    ax_comp.set_xticklabels(solvers, rotation=25, ha="right")
    ax_comp.grid(axis="y", linestyle=":", alpha=0.6)
    for bar in bars:
        ax_comp.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 0.02, f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    fig_comp.tight_layout()
    comp_plot_path = os.path.join(plots_dir, "solver_utility_comparison.png")
    fig_comp.savefig(comp_plot_path, dpi=300)

    # 7. Write Experiment Run Artifacts (JSON and CSV)
    experiment_record = {
        "experiment_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "git_commit": get_git_commit_hash(),
        "problem_parameters": {
            "num_assets": num_assets,
            "budget": budget,
            "risk_factor": 0.5,
            "penalty_multiplier": 2.5,
            "random_seed": seed,
        },
        "environment": {
            "python_version": sys.version,
            "qiskit_version": qiskit.__version__,
            "simulator": "StatevectorEstimator / StatevectorSampler (Qiskit reference primitives)",
        },
        "hamiltonian_verification": {
            "verified": hamiltonian_valid,
            "tolerance": 1e-6,
        },
        "classical_benchmarks": {
            "brute_force": {
                "assignment": bf_res.best_assignment,
                "utility": bf_res.best_utility,
                "cost": bf_res.best_cost,
                "evaluations": bf_res.num_evaluations,
                "runtime_seconds": bf_res.runtime_seconds,
            },
            "greedy_heuristic": {
                "assignment": gr_res.best_assignment,
                "utility": gr_res.best_utility,
                "cost": gr_res.best_cost,
                "runtime_seconds": gr_res.runtime_seconds,
            },
        },
        "qaoa_depth_sweep": depth_results,
        "penalty_sweep": penalty_results,
        "metric_formulas": {
            "approximation_ratio": "C_qaoa_utility / C_opt_utility",
            "feasibility_yield": "(N_feasible_shots / N_total_shots) * 100",
            "utility": "r^T x - 0.5 * q * x^T Sigma x",
            "cost": "-U(x) + lambda * (sum(x) - B)^2",
        },
        "plot_artifacts": [
            "outputs/plots/convergence_trajectory.png",
            "outputs/plots/solution_distribution.png",
            "outputs/plots/depth_scaling_comparison.png",
            "outputs/plots/penalty_sweep_analysis.png",
            "outputs/plots/solver_utility_comparison.png",
        ],
    }

    json_path = os.path.join(run_dir, "experiment_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(experiment_record, f, indent=2)

    # Summary CSV
    csv_path = os.path.join(run_dir, "depth_sweep_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("depth_p,approx_ratio,feasibility_yield_pct,best_cost,utility,runtime_seconds\n")
        for row in depth_results:
            f.write(f"{row['p']},{row['approx_ratio']:.4f},{row['feasibility_yield']:.2f},{row['min_cost']:.4f},{row['utility']:.4f},{row['runtime_seconds']:.4f}\n")

    print(f"\nExperiment complete. Metrics and artifacts recorded in:\n  * {json_path}\n  * {csv_path}")
    return experiment_record


if __name__ == "__main__":
    run_comprehensive_benchmarks()
