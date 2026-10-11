# Mathematical Formulation: Constrained Green Energy Asset Allocation

This document derives the exact equations, matrix representations, and Pauli operator transformations implemented in the `quantum-resource-optimizer` codebase.

---

## 1. Classical Formulation: Constrained Portfolio Selection

Consider an investment authority tasked with selecting a subset of $n$ available renewable energy initiatives (e.g. Solar PV Farms, Offshore Wind, Battery Storage Systems, Geothermal Plants, Biomass Facilities).

### Parameters:
- $n \in \mathbb{N}$: Number of candidate energy assets.
- $r = (r_0, r_1, \dots, r_{n-1})^T \in \mathbb{R}^n$: Vector of expected returns (clean generation capacity / carbon offset score).
- $\Sigma \in \mathbb{R}^{n \times n}$: Symmetric, positive semi-definite covariance matrix representing volatility and intermittency correlation between assets.
- $q \ge 0$: Risk aversion parameter.
- $B \in \{1, \dots, n-1\}$: Fixed asset budget constraint (number of assets that must be selected).
- $\lambda > 0$: Constraint penalty multiplier.

### Binary Decision Variables:
$$x = (x_0, x_1, \dots, x_{n-1})^T \in \{0, 1\}^n$$
where $x_i = 1$ if asset $i$ is chosen, and $0$ otherwise.

### Constrained Markowitz Problem:
$$\max_{x \in \{0, 1\}^n} \quad \mathcal{U}(x) = \sum_{i=0}^{n-1} r_i x_i - \frac{q}{2} \sum_{i=0}^{n-1} \sum_{j=0}^{n-1} \Sigma_{ij} x_i x_j$$
$$\text{subject to} \quad \sum_{i=0}^{n-1} x_i = B$$

---

## 2. QUBO Representation

To represent the problem without constraints, we convert the maximization of $\mathcal{U}(x)$ into the minimization of $-\mathcal{U}(x)$, and penalize violations of the budget constraint:

$$C(x) = -\mathcal{U}(x) + \lambda \left(\sum_{i=0}^{n-1} x_i - B\right)^2$$

### Expansion of the Penalty Term:
$$\left(\sum_{i=0}^{n-1} x_i - B\right)^2 = \left(\sum_{i=0}^{n-1} x_i\right)^2 - 2B \left(\sum_{i=0}^{n-1} x_i\right) + B^2$$

Since $x_i \in \{0, 1\}$, the property $x_i^2 = x_i$ holds. Expanding the squared sum:
$$\left(\sum_{i=0}^{n-1} x_i\right)^2 = \sum_{i=0}^{n-1} x_i^2 + 2 \sum_{i < j} x_i x_j = \sum_{i=0}^{n-1} x_i + 2 \sum_{i < j} x_i x_j$$

Substituting this back into the penalty term:
$$\left(\sum_{i=0}^{n-1} x_i - B\right)^2 = (1 - 2B)\sum_{i=0}^{n-1} x_i + 2 \sum_{i < j} x_i x_j + B^2$$

### Combined QUBO Cost Function:
$$C(x) = \sum_{i < j} Q_{ij} x_i x_j + \sum_{i=0}^{n-1} Q_{ii} x_i + \text{const}$$

where the coefficients are given by:
- **Pairwise Terms ($i < j$):**
  $$Q_{ij} = q \, \Sigma_{ij} + 2\lambda$$
  *(since $\Sigma_{ij} = \Sigma_{ji}$ by symmetry)*
- **Linear Diagonal Terms ($i = i$):**
  $$Q_{ii} = -r_i + \frac{q}{2} \Sigma_{ii} + \lambda (1 - 2B)$$
- **Constant Offset:**
  $$\text{const} = \lambda B^2$$

---

## 3. Mapping to Ising Cost Hamiltonian

Quantum computers natively represent problems using spin Hamiltonians (Pauli-$Z$ operators).
We apply the affine mapping from binary variables $x_i \in \{0, 1\}$ to Pauli-$Z$ operators $Z_i \in \{+1, -1\}$:
$$x_i = \frac{I - Z_i}{2}$$

### Substituting into Linear Terms:
$$Q_{ii} x_i = Q_{ii} \left(\frac{I - Z_i}{2}\right) = \frac{Q_{ii}}{2} I - \frac{Q_{ii}}{2} Z_i$$

### Substituting into Quadratic Terms ($i < j$):
$$Q_{ij} x_i x_j = Q_{ij} \left(\frac{I - Z_i}{2}\right)\left(\frac{I - Z_j}{2}\right) = \frac{Q_{ij}}{4} \left( I - Z_i - Z_j + Z_i Z_j \right)$$

### Resulting Cost Hamiltonian:
Summing all terms yields the diagonal Cost Hamiltonian:
$$\hat{H}_C = \sum_{i < j} J_{ij} Z_i Z_j + \sum_{i=0}^{n-1} h_i Z_i + c_0 \cdot I$$

where:
1. **Coupling Coefficients ($J_{ij}$ for $i < j$):**
   $$J_{ij} = \frac{Q_{ij}}{4} = \frac{q \Sigma_{ij} + 2\lambda}{4}$$

2. **Local Longitudinal Fields ($h_i$):**
   $$h_i = -\frac{Q_{ii}}{2} - \sum_{j \neq i} \frac{Q_{ij}}{4}$$
   where $Q_{ij} = Q_{ji}$ for $j \neq i$.

3. **Global Constant Energy Offset ($c_0$):**
   $$c_0 = \text{const} + \sum_{i=0}^{n-1} \frac{Q_{ii}}{2} + \sum_{i < j} \frac{Q_{ij}}{4}$$

---

## 4. Ground State Equivalence Proof

For any classical binary state $x \in \{0, 1\}^n$, the corresponding computational basis quantum state is $|x\rangle = |x_{n-1} \dots x_0\rangle$.
Because $Z_i |x\rangle = (-1)^{x_i} |x\rangle = (1 - 2x_i) |x\rangle$:
$$\langle x | \hat{H}_C | x \rangle = C(x)$$

Therefore:
$$\min_{|\psi\rangle} \langle \psi | \hat{H}_C | \psi \rangle = \min_{x \in \{0, 1\}^n} C(x)$$

The ground state $|\psi_0\rangle$ of $\hat{H}_C$ has energy exactly equal to the minimum cost $C(x^*)$, and measuring $|\psi_0\rangle$ in the computational basis yields the optimal portfolio $x^*$ with probability 1.

---

## 5. QAOA Circuit Architecture

The QAOA ansatz circuit at depth $p$ implements:
$$|\psi(\vec{\gamma}, \vec{\beta})\rangle = U_M(\beta_p) U_C(\gamma_p) \dots U_M(\beta_1) U_C(\gamma_1) |+\rangle^{\otimes n}$$

1. **State Initialization:**
   $$|+\rangle^{\otimes n} = \bigotimes_{i=0}^{n-1} H |0\rangle$$
2. **Cost Unitary ($U_C(\gamma_k)$):**
   $$U_C(\gamma_k) = \exp(-i \gamma_k \hat{H}_C) = \prod_{i < j} \exp(-i \gamma_k J_{ij} Z_i Z_j) \prod_{i} \exp(-i \gamma_k h_i Z_i)$$
   - Two-qubit term $\exp(-i \theta Z_i Z_j)$ is synthesized as: $\text{CNOT}(i, j) \to RZ(2\theta) \to \text{CNOT}(i, j)$.
   - Single-qubit term $\exp(-i \theta Z_i)$ is synthesized as: $RZ(2\theta)$.
3. **Mixer Unitary ($U_M(\beta_k)$):**
   $$U_M(\beta_k) = \exp(-i \beta_k \sum_{i} X_i) = \prod_{i=0}^{n-1} RX(2\beta_k)$$

In modern Qiskit, this entire circuit is constructed natively using `qiskit.circuit.library.QAOAAnsatz(cost_operator=H_C, reps=p)`.
