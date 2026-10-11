"""Tests for problem instance definition, input validation, and objective evaluation."""

import numpy as np
import pytest

from quantum_optimizer.problem import Asset, ProblemInstance


def test_asset_dataclass():
    """Verifies Asset dataclass attributes."""
    asset = Asset(id=0, name="Solar PV", category="Solar", expected_return=0.8, carbon_offset=90.0)
    assert asset.id == 0
    assert asset.name == "Solar PV"
    assert asset.category == "Solar"
    assert asset.expected_return == 0.8
    assert asset.carbon_offset == 90.0


def test_problem_instance_validation_errors():
    """Verifies that invalid configurations raise descriptive ValueErrors."""
    assets = [
        Asset(0, "A", "Solar", 0.8, 90.0),
        Asset(1, "B", "Wind", 0.9, 100.0),
    ]
    ret = np.array([0.8, 0.9])
    cov = np.array([[0.2, 0.05], [0.05, 0.3]])

    # Invalid asset count < 2
    with pytest.raises(ValueError, match="at least 2 assets"):
        ProblemInstance([assets[0]], np.array([0.8]), np.array([[0.2]]), budget=1)

    # Mismatched returns length
    with pytest.raises(ValueError, match="Returns vector shape"):
        ProblemInstance(assets, np.array([0.8]), cov, budget=1)

    # Non-symmetric covariance
    bad_cov = np.array([[0.2, 0.1], [0.0, 0.3]])
    with pytest.raises(ValueError, match="must be symmetric"):
        ProblemInstance(assets, ret, bad_cov, budget=1)

    # Budget out of range (B >= n or B < 1)
    with pytest.raises(ValueError, match="Budget B=2 must be in the range"):
        ProblemInstance(assets, ret, cov, budget=2)

    with pytest.raises(ValueError, match="Budget B=0 must be in the range"):
        ProblemInstance(assets, ret, cov, budget=0)

    # Negative penalty
    with pytest.raises(ValueError, match="strictly positive"):
        ProblemInstance(assets, ret, cov, budget=1, penalty_multiplier=-1.0)


def test_hand_calculated_evaluation():
    """Verifies exact analytical objective and penalty calculations against hand-computed values.

    Analytical Instance:
        n = 2 assets, budget B = 1, q = 1.0, lambda = 2.0
        r = [1.0, 2.0]
        Sigma = [[0.2, 0.0], [0.0, 0.4]]

    Calculations:
        - [1, 0]: return = 1.0, risk = 0.5 * 1.0 * 0.2 = 0.1, utility = 0.9
                  penalty = 2.0 * (1 - 1)^2 = 0.0 -> cost = -0.9 + 0 = -0.9 (feasible)
        - [0, 1]: return = 2.0, risk = 0.5 * 1.0 * 0.4 = 0.2, utility = 1.8
                  penalty = 2.0 * (1 - 1)^2 = 0.0 -> cost = -1.8 + 0 = -1.8 (feasible, best!)
        - [0, 0]: return = 0.0, risk = 0.0, utility = 0.0
                  penalty = 2.0 * (0 - 1)^2 = 2.0 -> cost = 2.0 (infeasible)
        - [1, 1]: return = 3.0, risk = 0.5 * (0.2 + 0.4) = 0.3, utility = 2.7
                  penalty = 2.0 * (2 - 1)^2 = 2.0 -> cost = -2.7 + 2.0 = -0.7 (infeasible)
    """
    assets = [
        Asset(0, "A", "Solar", 1.0, 50.0),
        Asset(1, "B", "Wind", 2.0, 80.0),
    ]
    ret = np.array([1.0, 2.0])
    cov = np.array([[0.2, 0.0], [0.0, 0.4]])
    p = ProblemInstance(assets, ret, cov, budget=1, risk_factor=1.0, penalty_multiplier=2.0)

    # Test [1, 0]
    assert np.isclose(p.evaluate_utility([1, 0]), 0.9)
    assert np.isclose(p.evaluate_constraint_penalty([1, 0]), 0.0)
    assert np.isclose(p.evaluate_cost([1, 0]), -0.9)
    assert p.is_feasible([1, 0]) is True

    # Test [0, 1]
    assert np.isclose(p.evaluate_utility([0, 1]), 1.8)
    assert np.isclose(p.evaluate_constraint_penalty([0, 1]), 0.0)
    assert np.isclose(p.evaluate_cost([0, 1]), -1.8)
    assert p.is_feasible([0, 1]) is True

    # Test [0, 0]
    assert np.isclose(p.evaluate_utility([0, 0]), 0.0)
    assert np.isclose(p.evaluate_constraint_penalty([0, 0]), 2.0)
    assert np.isclose(p.evaluate_cost([0, 0]), 2.0)
    assert p.is_feasible([0, 0]) is False

    # Test [1, 1]
    assert np.isclose(p.evaluate_utility([1, 1]), 2.7)
    assert np.isclose(p.evaluate_constraint_penalty([1, 1]), 2.0)
    assert np.isclose(p.evaluate_cost([1, 1]), -0.7)
    assert p.is_feasible([1, 1]) is False


def test_create_benchmark_instance():
    """Verifies creation of calibrated benchmark instances."""
    inst = ProblemInstance.create_benchmark_instance(num_assets=5, budget=2, seed=42)
    assert inst.num_assets == 5
    assert inst.budget == 2
    assert inst.returns.shape == (5,)
    assert inst.covariance.shape == (5, 5)
    assert np.allclose(inst.covariance, inst.covariance.T)
    # Check that diagonal variance is positive
    assert np.all(np.diag(inst.covariance) > 0)
