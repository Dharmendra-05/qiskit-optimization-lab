"""Quantum Resource Optimizer package.

Solves constrained green energy portfolio and resource allocation using QAOA,
benchmarked against classical exact and heuristic solvers.
"""

from .problem import Asset, ProblemInstance
from .classical_solvers import BruteForceSolver, GreedySolver, ClassicalBenchmarkResult
from .hamiltonian import build_cost_hamiltonian, verify_hamiltonian_ground_state
from .qaoa_solver import QAOASolver, QAOAResult

__all__ = [
    "Asset",
    "ProblemInstance",
    "BruteForceSolver",
    "GreedySolver",
    "ClassicalBenchmarkResult",
    "build_cost_hamiltonian",
    "verify_hamiltonian_ground_state",
    "QAOASolver",
    "QAOAResult",
]
