"""Command-line interface for the Quantum Resource Optimizer."""

import argparse
import os
import sys
import numpy as np

from .problem import ProblemInstance
from .classical_solvers import BruteForceSolver, GreedySolver
from .qaoa_solver import QAOASolver
from .visualization import plot_convergence, plot_sampled_distribution


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Quantum Resource Optimizer: Constrained Green Energy Asset Allocation using QAOA"
    )
    parser.add_argument("--num-assets", type=int, default=5, help="Number of candidate energy assets (default: 5)")
    parser.add_argument("--budget", type=int, default=2, help="Exact number of assets to select (default: 2)")
    parser.add_argument("--risk-factor", type=float, default=0.5, help="Risk aversion factor q (default: 0.5)")
    parser.add_argument("--penalty", type=float, default=2.5, help="Constraint penalty multiplier lambda (default: 2.5)")
    parser.add_argument("--p", type=int, default=1, help="QAOA circuit depth / layers p (default: 1)")
    parser.add_argument("--shots", type=int, default=2048, help="Number of measurement shots (default: 2048)")
    parser.add_argument("--maxiter", type=int, default=100, help="Optimizer max iterations (default: 100)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--save-plots", action="store_true", help="Save generated visualization plots to outputs/plots")
    return parser.parse_args(args)


def main(args=None):
    opts = parse_args(args)
    print("=" * 70)
    print("      QUANTUM RESOURCE OPTIMIZER: GREEN ENERGY ALLOCATION")
    print("      Qiskit Fall Fest 2026 -- Track 2 Optimization Solver")
    print("=" * 70)
    print(f"Configuration: Assets={opts.num_assets}, Budget={opts.budget}, p={opts.p}, Shots={opts.shots}, Seed={opts.seed}")

    # Step 1: Initialize Problem Instance
    print("\n[1/4] Generating renewable energy asset portfolio...")
    problem = ProblemInstance.create_benchmark_instance(
        num_assets=opts.num_assets,
        budget=opts.budget,
        risk_factor=opts.risk_factor,
        penalty_multiplier=opts.penalty,
        seed=opts.seed,
    )
    for asset in problem.assets:
        print(f"  * Asset {asset.id}: {asset.name:<25} ({asset.category}) Expected Yield={asset.expected_return:.2f}, CO2={asset.carbon_offset:.0f}t")

    # Step 2: Classical Baselines
    print("\n[2/4] Executing Classical Benchmarks...")
    bf_solver = BruteForceSolver(problem)
    bf_res = bf_solver.solve()
    print(f"  [Exact Brute-Force] Optimal: {bf_res.best_assignment} | Utility: {bf_res.best_utility:.4f} | Cost: {bf_res.best_cost:.4f} (Time: {bf_res.runtime_seconds*1000:.1f}ms)")

    gr_solver = GreedySolver(problem)
    gr_res = gr_solver.solve()
    print(f"  [Greedy Heuristic]  Picked:  {gr_res.best_assignment} | Utility: {gr_res.best_utility:.4f} | Cost: {gr_res.best_cost:.4f} (Time: {gr_res.runtime_seconds*1000:.1f}ms)")

    # Step 3: QAOA Solver
    print(f"\n[3/4] Solving via QAOA (depth p={opts.p}, shots={opts.shots})...")
    qaoa_solver = QAOASolver(problem, reps=opts.p, seed=opts.seed)
    qaoa_res = qaoa_solver.solve(maxiter=opts.maxiter, shots=opts.shots)

    print(f"  Optimal QAOA angles: gamma={np.round(qaoa_res.optimal_parameters[:opts.p], 4)}, beta={np.round(qaoa_res.optimal_parameters[opts.p:], 4)}")
    print(f"  Minimum expected cost: {qaoa_res.minimum_expected_energy:.4f}")
    print(f"  Best sampled assignment: {qaoa_res.best_sampled_assignment} (Feasible: {qaoa_res.best_sampled_feasible})")
    print(f"  Best sampled utility:    {qaoa_res.best_sampled_utility:.4f}")
    print(f"  Approximation Ratio:     {qaoa_res.approximation_ratio:.4f}")
    print(f"  Feasibility Yield:       {qaoa_res.feasibility_yield:.2f}%")
    print(f"  Execution Runtime:       {qaoa_res.runtime_seconds:.2f}s")

    # Step 4: Top Sampled Bitstrings
    print("\n[4/4] Top 5 Sampled Candidate Portfolios:")
    for assignment, count, cost, utility, feasible in qaoa_res.sampled_bitstrings[:5]:
        feas_str = "FEASIBLE" if feasible else "INFEASIBLE"
        is_opt = "★ OPTIMAL" if assignment == bf_res.best_assignment else ""
        print(f"  {assignment}  count={count:4d} ({count/opts.shots*100:5.1f}%)  utility={utility:6.3f}  [{feas_str}] {is_opt}")

    # Optional plot saving
    if opts.save_plots:
        os.makedirs("outputs/plots", exist_ok=True)
        conv_path = f"outputs/plots/convergence_p{opts.p}_n{opts.num_assets}.png"
        dist_path = f"outputs/plots/distribution_p{opts.p}_n{opts.num_assets}.png"
        plot_convergence(qaoa_res.convergence_history, output_path=conv_path)
        plot_sampled_distribution(qaoa_res, output_path=dist_path)
        print(f"\nSaved plots to:\n  * {conv_path}\n  * {dist_path}")

    print("\nOptimization completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
