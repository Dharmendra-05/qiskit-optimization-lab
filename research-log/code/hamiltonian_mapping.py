"""Code excerpt: QUBO to Ising Cost Hamiltonian mapping and verification.
From src/quantum_optimizer/hamiltonian.py
"""

from typing import List, Tuple
import numpy as np
from qiskit.quantum_info import SparsePauliOp
from quantum_optimizer.problem import ProblemInstance


def build_cost_hamiltonian(
    problem: ProblemInstance,
    include_offset: bool = True,
) -> Tuple[SparsePauliOp, float]:
    """Maps the QUBO problem formulation into an Ising Cost Hamiltonian.

    Uses the affine substitution x_i = (I - Z_i) / 2.
    Produces a SparsePauliOp conforming to Qiskit's little-endian qubit ordering.
    """
    n = problem.num_assets
    q = problem.risk_factor
    lam = problem.penalty_multiplier
    b = problem.budget
    ret = problem.returns
    cov = problem.covariance

    # Diagonal linear terms: Q_ii = -r_i + 0.5 * q * Sigma_ii + lambda * (1 - 2B)
    Q_diag = np.zeros(n, dtype=float)
    for i in range(n):
        Q_diag[i] = -ret[i] + 0.5 * q * cov[i, i] + lam * (1.0 - 2.0 * b)

    # Upper triangular pairwise terms: Q_ij = q * Sigma_ij + 2 * lambda (for i < j)
    Q_matrix = np.zeros((n, n), dtype=float)
    for i in range(n):
        Q_matrix[i, i] = Q_diag[i]
        for j in range(i + 1, n):
            Q_matrix[i, j] = q * cov[i, j] + 2.0 * lam

    base_const = lam * (b ** 2)
    terms: List[Tuple[str, float]] = []

    # Pairwise ZZ terms: J_ij = Q_ij / 4
    for i in range(n):
        for j in range(i + 1, n):
            J_ij = Q_matrix[i, j] / 4.0
            if abs(J_ij) > 1e-12:
                pauli_chars = ["I"] * n
                pauli_chars[n - 1 - i] = "Z"
                pauli_chars[n - 1 - j] = "Z"
                terms.append(("".join(pauli_chars), float(J_ij)))

    # Single-qubit Z field terms: h_i = -Q_ii / 2 - sum_{j != i} Q_{min(i,j), max(i,j)} / 4
    for i in range(n):
        h_i = -Q_diag[i] / 2.0
        for j in range(n):
            if i != j:
                i_min, i_max = min(i, j), max(i, j)
                h_i -= Q_matrix[i_min, i_max] / 4.0
        if abs(h_i) > 1e-12:
            pauli_chars = ["I"] * n
            pauli_chars[n - 1 - i] = "Z"
            terms.append(("".join(pauli_chars), float(h_i)))

    # Constant scalar identity offset c_0
    total_offset = base_const + float(np.sum(Q_diag) / 2.0)
    for i in range(n):
        for j in range(i + 1, n):
            total_offset += float(Q_matrix[i, j] / 4.0)

    if include_offset and abs(total_offset) > 1e-12:
        terms.append(("I" * n, float(total_offset)))

    hamiltonian = SparsePauliOp.from_list(terms).simplify()
    return hamiltonian, total_offset
