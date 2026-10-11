"""Code excerpt: Little-endian bitstring decoding and assignment scoring.
From src/quantum_optimizer/qaoa_solver.py
"""

from typing import Dict, List, Tuple
from qiskit.primitives import StatevectorSampler
from quantum_optimizer.problem import ProblemInstance


def decode_qiskit_bitstring(key: str, num_qubits: int) -> List[int]:
    """Converts a little-endian Qiskit bitstring into node/asset assignments.

    In Qiskit, the rightmost character corresponds to qubit 0 (least significant bit).
    Reversing the bitstring aligns index i with asset i (qubit i).
    """
    clean_key = key.replace(" ", "")
    reversed_bits = clean_key[::-1]
    return [int(reversed_bits[i]) for i in range(num_qubits)]


def sample_and_score_assignments(
    sampler: StatevectorSampler,
    measured_ansatz,
    optimal_params,
    problem: ProblemInstance,
    shots: int = 4096,
) -> Tuple[Dict[str, int], List[Tuple[List[int], int, float, float, bool]]]:
    """Executes statevector sampling and scores all unique computational basis states."""
    pub = (measured_ansatz, optimal_params)
    sampler_res = sampler.run([pub], shots=shots).result()[0]
    counts = sampler_res.data.meas.get_counts()

    scored = []
    n = problem.num_assets
    for key, count in counts.items():
        assignment = decode_qiskit_bitstring(key, n)
        cost = problem.evaluate_cost(assignment)
        utility = problem.evaluate_utility(assignment)
        feasible = problem.is_feasible(assignment)
        scored.append((assignment, int(count), cost, utility, feasible))

    scored.sort(key=lambda item: item[1], reverse=True)
    return counts, scored
