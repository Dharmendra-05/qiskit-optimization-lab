"""Tests for Hamiltonian mapping and ground-state equivalence."""

import numpy as np
import pytest

from quantum_optimizer.problem import ProblemInstance
from quantum_optimizer.hamiltonian import (
    build_qubo_matrix,
    build_cost_hamiltonian,
    verify_hamiltonian_ground_state,
)


def test_qubo_matrix_construction():
    """Tests the QUBO matrix construction against hand-calculated values."""
    p = ProblemInstance.create_benchmark_instance(num_assets=3, budget=1, risk_factor=1.0, penalty_multiplier=2.0)
    Q_matrix, Q_diag, const_offset = build_qubo_matrix(p)

    assert Q_matrix.shape == (3, 3)
    assert Q_diag.shape == (3,)
    assert const_offset == 2.0 * (1 ** 2)

    # Check that diagonal elements match Q_diag
    for i in range(3):
        assert np.isclose(Q_matrix[i, i], Q_diag[i])


def test_hamiltonian_ground_state_exact_equivalence():
    """Rigorously proves <x|H_C|x> == C(x) for all 2^N states on multiple instance sizes."""
    # 2-asset instance
    p2 = ProblemInstance.create_benchmark_instance(num_assets=2, budget=1, seed=10)
    h2, _ = build_cost_hamiltonian(p2)
    assert verify_hamiltonian_ground_state(p2, h2) is True

    # 3-asset instance
    p3 = ProblemInstance.create_benchmark_instance(num_assets=3, budget=2, seed=20)
    h3, _ = build_cost_hamiltonian(p3)
    assert verify_hamiltonian_ground_state(p3, h3) is True

    # 4-asset instance
    p4 = ProblemInstance.create_benchmark_instance(num_assets=4, budget=2, seed=30)
    h4, _ = build_cost_hamiltonian(p4)
    assert verify_hamiltonian_ground_state(p4, h4) is True


def test_pauli_terms_format():
    """Verifies that generated SparsePauliOp terms have correct length and characters."""
    n = 4
    p = ProblemInstance.create_benchmark_instance(num_assets=n, budget=2, seed=42)
    hamiltonian, offset = build_cost_hamiltonian(p)

    assert hamiltonian.num_qubits == n
    pauli_list = hamiltonian.paulis.to_labels()
    for label in pauli_list:
        assert len(label) == n
        # Check only Z and I characters are present
        assert set(label).issubset({"I", "Z"})
