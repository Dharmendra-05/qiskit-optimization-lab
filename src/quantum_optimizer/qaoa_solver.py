"""QAOA Solver implementation using modern Qiskit 1.0+ / 2.0+ primitives."""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import minimize

from qiskit.circuit.library import QAOAAnsatz
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

from .problem import ProblemInstance
from .hamiltonian import build_cost_hamiltonian
from .classical_solvers import BruteForceSolver


@dataclass
class QAOAResult:
    """Encapsulates the complete results of a QAOA execution."""
    optimal_parameters: np.ndarray
    minimum_expected_energy: float
    best_sampled_assignment: List[int]
    best_sampled_cost: float
    best_sampled_utility: float
    best_sampled_feasible: bool
    sampled_bitstrings: List[Tuple[List[int], int, float, float, bool]]  # (assignment, count, cost, utility, feasible)
    counts: Dict[str, int]
    shots: int
    reps: int
    convergence_history: List[float]
    approximation_ratio: float
    feasibility_yield: float  # Percentage of sampled shots that satisfy the budget constraint
    optimizer_iterations: int
    runtime_seconds: float
    known_optimal_assignment: Optional[List[int]] = None
    known_optimal_cost: Optional[float] = None
    known_optimal_utility: Optional[float] = None


class QAOASolver:
    """Solves the Constrained Resource Optimization problem using QAOA."""

    def __init__(
        self,
        problem: ProblemInstance,
        reps: int = 1,
        seed: int = 42,
    ) -> None:
        self.problem = problem
        self.reps = int(reps)
        self.seed = int(seed)
        self.cost_hamiltonian, self.energy_offset = build_cost_hamiltonian(problem, include_offset=True)

        # Build parameterized ansatz (unmeasured for Estimator, measured for Sampler)
        self.ansatz = QAOAAnsatz(cost_operator=self.cost_hamiltonian, reps=self.reps)
        self.measured_ansatz = self.ansatz.copy()
        self.measured_ansatz.measure_all()

    @staticmethod
    def key_to_assignment(key: str, num_qubits: int) -> List[int]:
        """Converts a little-endian Qiskit bitstring into node/asset assignments.

        In Qiskit, the rightmost bit is qubit 0.
        Reversing gives index 0 as asset 0.
        """
        clean_key = key.replace(" ", "")
        reversed_bits = clean_key[::-1]
        return [int(reversed_bits[i]) for i in range(num_qubits)]

    def optimize(
        self,
        maxiter: int = 200,
        initial_params: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, float, List[float], int]:
        """Optimizes QAOA variational parameters using StatevectorEstimator and COBYLA.

        Returns:
            Tuple of (optimal_parameters, minimum_energy, convergence_history, total_evaluations).
        """
        estimator = StatevectorEstimator()
        convergence_history: List[float] = []

        def cost_function(params: np.ndarray) -> float:
            pub = (self.ansatz, self.cost_hamiltonian, params)
            energy = float(estimator.run([pub]).result()[0].data.evs)
            convergence_history.append(energy)
            return energy

        if initial_params is None:
            rng = np.random.default_rng(self.seed)
            # 2*p parameters: p gammas, p betas
            initial_params = rng.uniform(0, np.pi, size=self.ansatz.num_parameters)

        opt_res = minimize(
            cost_function,
            initial_params,
            method="COBYLA",
            options={"maxiter": maxiter},
        )

        return opt_res.x, float(opt_res.fun), convergence_history, len(convergence_history)

    def sample(
        self,
        params: np.ndarray,
        shots: int = 4096,
    ) -> Tuple[Dict[str, int], List[Tuple[List[int], int, float, float, bool]]]:
        """Samples bitstrings from the parameterized circuit using StatevectorSampler.

        Returns:
            Tuple of (counts_dict, scored_assignments_list).
        """
        sampler = StatevectorSampler()
        pub = (self.measured_ansatz, params)
        sampler_res = sampler.run([pub], shots=shots).result()[0]
        counts = sampler_res.data.meas.get_counts()

        scored: List[Tuple[List[int], int, float, float, bool]] = []
        n = self.problem.num_assets

        for key, count in counts.items():
            assignment = self.key_to_assignment(key, n)
            cost = self.problem.evaluate_cost(assignment)
            utility = self.problem.evaluate_utility(assignment)
            feasible = self.problem.is_feasible(assignment)
            scored.append((assignment, int(count), cost, utility, feasible))

        # Sort descending by sample count (most probable first)
        scored.sort(key=lambda item: item[1], reverse=True)
        return counts, scored

    def solve(
        self,
        maxiter: int = 200,
        shots: int = 4096,
        initial_params: Optional[np.ndarray] = None,
    ) -> QAOAResult:
        """Executes the complete QAOA workflow: optimization, sampling, and benchmark comparison."""
        start_time = time.perf_counter()

        # Step 1: Classical parameter optimization
        opt_params, min_energy, history, iters = self.optimize(
            maxiter=maxiter,
            initial_params=initial_params,
        )

        # Step 2: Sampling candidate bitstrings
        counts, scored_assignments = self.sample(params=opt_params, shots=shots)

        # Step 3: Identify best feasible solution found in samples
        feasible_samples = [s for s in scored_assignments if s[4]]
        if feasible_samples:
            # Best feasible solution minimizes cost / maximizes utility
            best_sample = min(feasible_samples, key=lambda s: s[2])
        else:
            # If no sample is strictly feasible, pick best overall
            best_sample = min(scored_assignments, key=lambda s: s[2])

        best_assignment, best_count, best_cost, best_utility, best_feasible = best_sample

        # Step 4: Feasibility yield calculation
        feasible_shots = sum(item[1] for item in scored_assignments if item[4])
        feasibility_yield = (feasible_shots / float(shots)) * 100.0

        # Step 5: Benchmark against exact classical optimum
        exact_solver = BruteForceSolver(self.problem)
        exact_res = exact_solver.solve()

        # Approximation ratio calculation:
        # Standard definition: C_qaoa_utility / C_opt_utility
        # For utilities > 0: ratio in [0, 1]
        if exact_res.best_utility > 1e-6:
            approx_ratio = max(0.0, min(1.0, best_utility / exact_res.best_utility))
        else:
            # Shift utilities if non-positive
            shift = abs(exact_res.best_utility) + 1.0
            approx_ratio = max(0.0, min(1.0, (best_utility + shift) / (exact_res.best_utility + shift)))

        runtime = time.perf_counter() - start_time

        return QAOAResult(
            optimal_parameters=opt_params,
            minimum_expected_energy=min_energy,
            best_sampled_assignment=best_assignment,
            best_sampled_cost=best_cost,
            best_sampled_utility=best_utility,
            best_sampled_feasible=best_feasible,
            sampled_bitstrings=scored_assignments,
            counts=counts,
            shots=shots,
            reps=self.reps,
            convergence_history=history,
            approximation_ratio=approx_ratio,
            feasibility_yield=feasibility_yield,
            optimizer_iterations=iters,
            runtime_seconds=runtime,
            known_optimal_assignment=exact_res.best_assignment,
            known_optimal_cost=exact_res.best_cost,
            known_optimal_utility=exact_res.best_utility,
        )
