"""Classical baseline solvers: Exact Brute-Force and Greedy Heuristic."""

from dataclasses import dataclass
from itertools import product
import time
from typing import Dict, List, Optional, Tuple
import numpy as np

from .problem import ProblemInstance


@dataclass
class ClassicalBenchmarkResult:
    """Encapsulates the output of a classical solver."""
    solver_name: str
    best_assignment: List[int]
    best_utility: float
    best_cost: float
    is_feasible: bool
    runtime_seconds: float
    num_evaluations: int
    all_feasible_count: Optional[int] = None
    all_assignments: Optional[List[Tuple[List[int], float, float, bool]]] = None


class BruteForceSolver:
    """Exact solver enumerating all 2^N candidate bitstrings.

    Used as the ground truth benchmark for problem sizes N <= 14.
    """

    def __init__(self, problem: ProblemInstance) -> None:
        self.problem = problem

    def solve(self) -> ClassicalBenchmarkResult:
        """Exhaustively evaluates all 2^N combinations to find the provable global optimum."""
        start_time = time.perf_counter()
        n = self.problem.num_assets

        best_cost = float("inf")
        best_assignment = None
        best_utility = float("-inf")
        feasible_count = 0
        all_results = []

        # Enumerate all 2^n bitstrings
        for bits in product([0, 1], repeat=n):
            assignment = list(bits)
            cost = self.problem.evaluate_cost(assignment)
            utility = self.problem.evaluate_utility(assignment)
            feasible = self.problem.is_feasible(assignment)

            if feasible:
                feasible_count += 1
                if cost < best_cost:
                    best_cost = cost
                    best_utility = utility
                    best_assignment = assignment

            all_results.append((assignment, cost, utility, feasible))

        # Fallback if no solution is strictly feasible (e.g. invalid budget)
        if best_assignment is None:
            min_entry = min(all_results, key=lambda t: t[1])
            best_assignment, best_cost, best_utility, _ = min_entry

        runtime = time.perf_counter() - start_time

        return ClassicalBenchmarkResult(
            solver_name="Exact Brute-Force",
            best_assignment=best_assignment,
            best_utility=best_utility,
            best_cost=best_cost,
            is_feasible=self.problem.is_feasible(best_assignment),
            runtime_seconds=runtime,
            num_evaluations=2 ** n,
            all_feasible_count=feasible_count,
            all_assignments=all_results,
        )


class GreedySolver:
    """Classical heuristic ranking assets by individual utility / risk score.

    Selects the top B assets sequentially to guarantee budget compliance.
    """

    def __init__(self, problem: ProblemInstance) -> None:
        self.problem = problem

    def solve(self) -> ClassicalBenchmarkResult:
        """Greedily picks the top B assets based on return-to-variance ratio."""
        start_time = time.perf_counter()
        n = self.problem.num_assets
        b = self.problem.budget

        # Score each asset individually: return / sqrt(variance)
        scores = []
        for i in range(n):
            var_i = max(self.problem.covariance[i, i], 1e-6)
            score = self.problem.returns[i] / np.sqrt(var_i)
            scores.append((i, score))

        # Sort descending by score
        scores.sort(key=lambda t: t[1], reverse=True)

        # Select top B assets
        selected_indices = {idx for idx, _ in scores[:b]}
        assignment = [1 if i in selected_indices else 0 for i in range(n)]

        cost = self.problem.evaluate_cost(assignment)
        utility = self.problem.evaluate_utility(assignment)
        runtime = time.perf_counter() - start_time

        return ClassicalBenchmarkResult(
            solver_name="Greedy Heuristic",
            best_assignment=assignment,
            best_utility=utility,
            best_cost=cost,
            is_feasible=self.problem.is_feasible(assignment),
            runtime_seconds=runtime,
            num_evaluations=n,
        )
