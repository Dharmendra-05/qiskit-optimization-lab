"""Hamiltonian construction and Ising mapping for portfolio optimization."""

from typing import Dict, List, Tuple
import numpy as np
from qiskit.quantum_info import SparsePauliOp

from .problem import ProblemInstance


def build_qubo_matrix(problem: ProblemInstance) -> Tuple[np.ndarray, np.ndarray, float]:
    """Constructs the QUBO coefficients for the problem instance.

    Returns:
        Q_matrix: (n, n) upper triangular matrix of pairwise and diagonal coefficients.
        Q_diag: (n,) array of linear diagonal coefficients Q_ii.
        constant_offset: Scalar constant term (lambda * B^2).
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
            # Sigma_ij is symmetric; covariance contribution is 0.5*q*(Sigma_ij + Sigma_ji) = q*Sigma_ij
            Q_matrix[i, j] = q * cov[i, j] + 2.0 * lam

    constant_offset = lam * (b ** 2)
    return Q_matrix, Q_diag, constant_offset


def build_cost_hamiltonian(
    problem: ProblemInstance,
    include_offset: bool = True,
) -> Tuple[SparsePauliOp, float]:
    """Maps the QUBO problem formulation into an Ising Cost Hamiltonian.

    Uses the affine substitution x_i = (I - Z_i) / 2.
    Produces a SparsePauliOp conforming to Qiskit's little-endian qubit ordering.

    Args:
        problem: The ProblemInstance specification.
        include_offset: Whether to add the identity (c0 * I) term directly into the operator.

    Returns:
        Tuple of (SparsePauliOp, total_offset_value).
    """
    n = problem.num_assets
    Q_matrix, Q_diag, base_const = build_qubo_matrix(problem)

    # 1. Two-qubit ZZ interaction terms J_ij = Q_ij / 4 for i < j
    # 2. Single-qubit Z field terms h_i = -Q_ii / 2 - sum_{j != i} Q_{min(i,j), max(i,j)} / 4
    # 3. Constant scalar offset c_0 = base_const + sum(Q_ii / 2) + sum_{i < j}(Q_ij / 4)

    terms: List[Tuple[str, float]] = []

    # Pairwise ZZ terms
    for i in range(n):
        for j in range(i + 1, n):
            J_ij = Q_matrix[i, j] / 4.0
            if abs(J_ij) > 1e-12:
                # Qiskit Pauli string: index 0 is rightmost (qubit 0).
                # String position for qubit k is (n - 1 - k).
                pauli_chars = ["I"] * n
                pauli_chars[n - 1 - i] = "Z"
                pauli_chars[n - 1 - j] = "Z"
                terms.append(("".join(pauli_chars), float(J_ij)))

    # Single-qubit Z terms
    h_fields = np.zeros(n, dtype=float)
    for i in range(n):
        h_i = -Q_diag[i] / 2.0
        for j in range(n):
            if i != j:
                i_min, i_max = min(i, j), max(i, j)
                h_i -= Q_matrix[i_min, i_max] / 4.0
        h_fields[i] = h_i
        if abs(h_i) > 1e-12:
            pauli_chars = ["I"] * n
            pauli_chars[n - 1 - i] = "Z"
            terms.append(("".join(pauli_chars), float(h_i)))

    # Constant identity offset
    total_offset = base_const + float(np.sum(Q_diag) / 2.0)
    for i in range(n):
        for j in range(i + 1, n):
            total_offset += float(Q_matrix[i, j] / 4.0)

    if include_offset and abs(total_offset) > 1e-12:
        terms.append(("I" * n, float(total_offset)))

    hamiltonian = SparsePauliOp.from_list(terms).simplify()
    return hamiltonian, total_offset


def verify_hamiltonian_ground_state(
    problem: ProblemInstance,
    hamiltonian: SparsePauliOp,
    atol: float = 1e-6,
) -> bool:
    """Verifies that for every 2^n basis state |x>, <x|H|x> equals the classical cost C(x).

    This provides formal proof of mathematical equivalence between the physical
    quantum operator and the classical QUBO.
    """
    n = problem.num_assets
    diag_elements = np.asarray(hamiltonian.to_matrix().diagonal().real, dtype=float)

    for int_val in range(2 ** n):
        # Basis state bitstring in little-endian order: qubit 0 is lowest bit
        bits = [(int_val >> i) & 1 for i in range(n)]
        expected_cost = problem.evaluate_cost(bits)

        # In Qiskit standard matrix representation, row index corresponds to
        # int_val where bit 0 is qubit 0 if big/little endian matching holds:
        # Standard Qiskit to_matrix() orders |q_{n-1} ... q_0> as standard integer binary.
        hamiltonian_energy = diag_elements[int_val]

        if not np.isclose(expected_cost, hamiltonian_energy, atol=atol):
            return False

    return True
