"""Tests for classical and quantum solvers."""

import numpy as np
import pytest

from quantum_optimizer.problem import ProblemInstance
from quantum_optimizer.classical_solvers import BruteForceSolver, GreedySolver
from quantum_optimizer.qaoa_solver import QAOASolver, QAOAResult


def test_classical_brute_force_solver():
    """Tests brute-force solver on known benchmark instance."""
    p = ProblemInstance.create_benchmark_instance(num_assets=4, budget=2, seed=42)
    solver = BruteForceSolver(p)
    res = solver.solve()

    assert res.solver_name == "Exact Brute-Force"
    assert len(res.best_assignment) == 4
    assert sum(res.best_assignment) == 2
    assert res.is_feasible is True
    assert res.num_evaluations == 16
    assert res.all_feasible_count == 6  # 4 choose 2 = 6


def test_classical_greedy_solver():
    """Tests greedy heuristic solver produces a feasible portfolio."""
    p = ProblemInstance.create_benchmark_instance(num_assets=5, budget=2, seed=42)
    solver = GreedySolver(p)
    res = solver.solve()

    assert res.solver_name == "Greedy Heuristic"
    assert len(res.best_assignment) == 5
    assert sum(res.best_assignment) == 2
    assert res.is_feasible is True
    assert res.num_evaluations == 5


def test_key_to_assignment_little_endian():
    """Verifies that Qiskit's little-endian strings are correctly reversed to asset indices."""
    # In Qiskit, key='100' means qubit 0 is 0, qubit 1 is 0, qubit 2 is 1
    # Reversed assignment should be [0, 0, 1]
    assignment = QAOASolver.key_to_assignment("100", 3)
    assert assignment == [0, 0, 1]
    assert assignment[0] == 0  # Asset 0 is qubit 0
    assert assignment[1] == 0  # Asset 1 is qubit 1
    assert assignment[2] == 1  # Asset 2 is qubit 2

    assignment_rev = QAOASolver.key_to_assignment("001", 3)
    assert assignment_rev == [1, 0, 0]
    assert assignment_rev[0] == 1


def test_qaoa_solver_execution_small_instance():
    """Tests end-to-end execution of QAOA on a 3-qubit instance."""
    p = ProblemInstance.create_benchmark_instance(num_assets=3, budget=1, seed=42)
    solver = QAOASolver(p, reps=1, seed=42)
    res = solver.solve(maxiter=30, shots=512)

    assert isinstance(res, QAOAResult)
    assert len(res.optimal_parameters) == 2  # 1 gamma, 1 beta
    assert res.shots == 512
    assert res.reps == 1
    assert 0.0 <= res.feasibility_yield <= 100.0
    assert 0.0 <= res.approximation_ratio <= 1.0
    assert len(res.best_sampled_assignment) == 3
    assert len(res.convergence_history) > 0


def test_qaoa_deterministic_reproducibility():
    """Verifies that fixing the random seed produces identical parameter outcomes."""
    p = ProblemInstance.create_benchmark_instance(num_assets=3, budget=1, seed=99)

    solver1 = QAOASolver(p, reps=1, seed=123)
    res1 = solver1.solve(maxiter=20, shots=256)

    solver2 = QAOASolver(p, reps=1, seed=123)
    res2 = solver2.solve(maxiter=20, shots=256)

    np.testing.assert_allclose(res1.optimal_parameters, res2.optimal_parameters, atol=1e-5)
    assert np.isclose(res1.minimum_expected_energy, res2.minimum_expected_energy, atol=1e-5)
