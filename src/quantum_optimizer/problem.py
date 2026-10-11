"""Problem definition for Constrained Green Energy Resource & Portfolio Allocation."""

from dataclasses import dataclass
from typing import List, Sequence, Tuple
import numpy as np


@dataclass(frozen=True)
class Asset:
    """Represents a candidate renewable energy project."""
    id: int
    name: str
    category: str
    expected_return: float
    carbon_offset: float


class ProblemInstance:
    """Encapsulates the data, parameters, and evaluation logic for a portfolio allocation dilemma."""

    def __init__(
        self,
        assets: List[Asset],
        returns: np.ndarray,
        covariance: np.ndarray,
        budget: int,
        risk_factor: float = 0.5,
        penalty_multiplier: float = 2.5,
    ) -> None:
        self.assets = assets
        self.returns = np.asarray(returns, dtype=float)
        self.covariance = np.asarray(covariance, dtype=float)
        self.budget = int(budget)
        self.risk_factor = float(risk_factor)
        self.penalty_multiplier = float(penalty_multiplier)
        self.validate()

    @property
    def num_assets(self) -> int:
        return len(self.assets)

    def validate(self) -> None:
        """Validates internal consistency and mathematical domain constraints."""
        n = len(self.assets)
        if n < 2:
            raise ValueError(f"Portfolio must contain at least 2 assets, got {n}")
        if self.returns.shape != (n,):
            raise ValueError(f"Returns vector shape {self.returns.shape} does not match asset count {n}")
        if self.covariance.shape != (n, n):
            raise ValueError(f"Covariance matrix shape {self.covariance.shape} must be ({n}, {n})")
        if not np.allclose(self.covariance, self.covariance.T, atol=1e-7):
            raise ValueError("Covariance matrix must be symmetric")
        if not (1 <= self.budget < n):
            raise ValueError(f"Budget B={self.budget} must be in the range [1, {n-1}]")
        if self.risk_factor < 0:
            raise ValueError(f"Risk factor q={self.risk_factor} must be non-negative")
        if self.penalty_multiplier <= 0:
            raise ValueError(f"Penalty multiplier lambda={self.penalty_multiplier} must be strictly positive")

    def evaluate_utility(self, assignment: Sequence[int]) -> float:
        """Computes classical Markowitz utility U(x) = r^T x - (q/2) x^T Sigma x.

        Higher values are better.
        """
        x = np.asarray(assignment, dtype=float)
        if len(x) != self.num_assets:
            raise ValueError(f"Assignment length {len(x)} does not match num_assets {self.num_assets}")
        ret = float(np.dot(self.returns, x))
        risk = 0.5 * self.risk_factor * float(x @ self.covariance @ x)
        return ret - risk

    def evaluate_constraint_penalty(self, assignment: Sequence[int]) -> float:
        """Computes quadratic constraint penalty: lambda * (sum(x) - B)^2."""
        x = np.asarray(assignment, dtype=float)
        violation = float(np.sum(x) - self.budget)
        return self.penalty_multiplier * (violation ** 2)

    def evaluate_cost(self, assignment: Sequence[int]) -> float:
        """Computes unconstrained minimization cost: C(x) = -U(x) + penalty(x).

        Lower values are better. The minimum corresponds to the optimal feasible portfolio.
        """
        return -self.evaluate_utility(assignment) + self.evaluate_constraint_penalty(assignment)

    def is_feasible(self, assignment: Sequence[int]) -> bool:
        """Returns True if the assignment strictly satisfies the budget constraint sum(x) == B."""
        return int(np.sum(assignment)) == self.budget

    @classmethod
    def create_benchmark_instance(
        cls,
        num_assets: int = 5,
        budget: int = 2,
        risk_factor: float = 0.5,
        penalty_multiplier: float = 2.5,
        seed: int = 42,
    ) -> "ProblemInstance":
        """Generates a realistic, calibrated renewable energy portfolio instance."""
        catalog = [
            ("Utility Solar Farm A", "Solar PV", 0.85, 95.0),
            ("Offshore Wind Array B", "Offshore Wind", 0.92, 120.0),
            ("Lithium-Ion BESS C", "Battery Storage", 0.65, 60.0),
            ("Biomass Cogen Plant D", "Biomass", 0.70, 75.0),
            ("Geothermal Plant E", "Geothermal", 0.88, 110.0),
            ("Rooftop Solar Cluster F", "Solar PV", 0.78, 80.0),
            ("Onshore Wind Park G", "Onshore Wind", 0.84, 90.0),
            ("Pumped Hydro Storage H", "Storage", 0.60, 50.0),
            ("Green Hydrogen Facility I", "Hydrogen", 0.75, 85.0),
            ("Tidal Energy Turbine J", "Marine", 0.68, 70.0),
        ]

        if num_assets > len(catalog):
            raise ValueError(f"Requested {num_assets} assets exceeds catalog size of {len(catalog)}")

        rng = np.random.default_rng(seed)
        selected_catalog = catalog[:num_assets]

        assets = [
            Asset(
                id=i,
                name=name,
                category=cat,
                expected_return=ret,
                carbon_offset=carb,
            )
            for i, (name, cat, ret, carb) in enumerate(selected_catalog)
        ]

        returns = np.array([a.expected_return for a in assets], dtype=float)

        # Generate a positive semi-definite covariance matrix with realistic correlation
        random_factors = rng.normal(0, 0.1, size=(num_assets, 3))
        cov = random_factors @ random_factors.T
        # Add diagonal self-variance between 0.1 and 0.2
        for i in range(num_assets):
            cov[i, i] += rng.uniform(0.12, 0.22)

        # Ensure exact symmetry
        cov = 0.5 * (cov + cov.T)

        return cls(
            assets=assets,
            returns=returns,
            covariance=cov,
            budget=budget,
            risk_factor=risk_factor,
            penalty_multiplier=penalty_multiplier,
        )
