# Algorithmic Specification: QAOA for Constrained Optimization

This document specifies the exact algorithmic steps, state preparation protocols, and mathematical operators utilized in the Quantum Approximate Optimization Algorithm (QAOA) implementation.

---

## 1. Algorithmic Overview

QAOA (Farhi, Goldstone, Gutmann, 2014) is a variational hybrid quantum-classical algorithm designed to identify high-quality approximate solutions to combinatorial optimization problems.

### Workflow Summary:
1. **Hamiltonian Encoding:** Transform the constrained optimization problem into a diagonal Cost Hamiltonian $\hat{H}_C$.
2. **Quantum Trial State Preparation:** Evolve an initial uniform superposition state $|+\rangle^{\otimes n}$ through $p$ alternating layers of cost unitaries $U_C(\gamma_k)$ and mixer unitaries $U_M(\beta_k)$.
3. **Classical Parameter Optimization:** Use a classical optimizer (COBYLA) to tune the $2p$ parameters $(\vec{\gamma}, \vec{\beta}) \in \mathbb{R}^{2p}$ to minimize the expectation value $E(\vec{\gamma}, \vec{\beta}) = \langle \psi(\vec{\gamma}, \vec{\beta}) | \hat{H}_C | \psi(\vec{\gamma}, \vec{\beta}) \rangle$.
4. **Computational Basis Sampling:** Perform projective measurements on the optimized statevector across multiple shots to sample candidate bitstrings.
5. **Classical Decoding & Validation:** Convert little-endian measurement keys to asset selections, evaluate feasibility, and compute the approximation ratio.

---

## 2. Mathematical Definition of Quantum Operators

### 2.1. Initial State
The algorithm initializes all $n$ qubits into an equal superposition:
$$|\psi_0\rangle = |+\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}} \sum_{x \in \{0, 1\}^n} |x\rangle$$
prepared by applying single-qubit Hadamard ($H$) gates:
$$|\psi_0\rangle = \bigotimes_{i=0}^{n-1} H |0\rangle_i$$

### 2.2. Cost Unitary Operator $U_C(\gamma_k)$
The cost Hamiltonian encodes the objective and penalty terms:
$$\hat{H}_C = \sum_{i < j} J_{ij} Z_i Z_j + \sum_{i=0}^{n-1} h_i Z_i + c_0 \cdot I$$
The cost unitary for layer $k \in \{1, \dots, p\}$ with angle $\gamma_k$ is:
$$U_C(\gamma_k) = \exp(-i \gamma_k \hat{H}_C) = \prod_{i < j} \exp(-i \gamma_k J_{ij} Z_i Z_j) \prod_{i=0}^{n-1} \exp(-i \gamma_k h_i Z_i)$$
Because all terms in $\hat{H}_C$ are diagonal in the computational basis, they mutually commute ($[Z_i Z_j, Z_k] = 0$), meaning the operator product is exact without Trotter discretization error.

#### Gate Decomposition:
- **Two-qubit interaction $\exp(-i \theta Z_i Z_j)$:** Synthesized as $\text{CNOT}(i, j) \to RZ(2\theta) \to \text{CNOT}(i, j)$.
- **Single-qubit field $\exp(-i \theta Z_i)$:** Synthesized as $RZ(2\theta)$ on qubit $i$.

### 2.3. Transverse-Field Mixer Unitary $U_M(\beta_k)$
The mixer Hamiltonian explores the Hilbert space by inducing transitions between computational basis states:
$$\hat{H}_M = \sum_{i=0}^{n-1} X_i$$
The mixer unitary with angle $\beta_k$ is:
$$U_M(\beta_k) = \exp(-i \beta_k \hat{H}_M) = \prod_{i=0}^{n-1} \exp(-i \beta_k X_i) = \prod_{i=0}^{n-1} RX(2\beta_k)_i$$

---

## 3. Variational Quantum Trial State

For a chosen circuit depth $p \in \mathbb{N}$ (number of alternating layers):
$$|\psi(\vec{\gamma}, \vec{\beta})\rangle = \left( \prod_{k=1}^p U_M(\beta_k) U_C(\gamma_k) \right) |+\rangle^{\otimes n}$$
The circuit parameters are partitioned into two vectors of length $p$:
- Cost rotation angles: $\vec{\gamma} = (\gamma_1, \dots, \gamma_p) \in [0, 2\pi)^p$
- Mixer rotation angles: $\vec{\beta} = (\beta_1, \dots, \beta_p) \in [0, \pi)^p$

---

## 4. Parameter Optimization Routine

The expectation value is computed using Qiskit's `StatevectorEstimator`:
$$E(\vec{\gamma}, \vec{\beta}) = \langle \psi(\vec{\gamma}, \vec{\beta}) | \hat{H}_C | \psi(\vec{\gamma}, \vec{\beta}) \rangle$$

### Optimizer: COBYLA (Constrained Optimization BY Linear Approximation)
- Gradient-free simplex-based local search method.
- Highly resilient to the non-convex, periodic energy landscape characteristic of QAOA cost functions.
- Default initialization: Uniform random sampling $\gamma_k, \beta_k \sim \mathcal{U}(0, \pi)$ with fixed random seed for reproducible convergence.

---

## 5. Measurement Sampling & Bitstring Decoding

Following parameter optimization:
1. Append computational basis measurements to all $n$ qubits.
2. Sample bitstrings using `StatevectorSampler` across $N_{\text{shots}} = 4096$ shots.
3. Account for Qiskit's little-endian bitstring ordering:
   $$\text{Bitstring from Sampler: } s = b_{n-1} b_{n-2} \dots b_1 b_0$$
   $$\text{Asset Assignment Vector: } x = [b_0, b_1, \dots, b_{n-1}]$$
4. Filter samples into feasible $\mathcal{F} = \{x \mid \sum x_i == B\}$ and infeasible states.
5. Identify the best feasible bitstring $x_{\text{QAOA}} = \arg\max_{x \in \mathcal{F}} \mathcal{U}(x)$.

---

## 6. Evaluation Metrics

1. **Approximation Ratio ($\alpha$):**
   $$\alpha = \frac{\mathcal{U}(x_{\text{QAOA}})}{\mathcal{U}(x_{\text{optimal}})}$$
   where $x_{\text{optimal}}$ is computed via classical brute-force enumeration.
2. **Feasibility Yield ($Y_{\text{feas}}$):**
   $$Y_{\text{feas}} = \frac{\sum_{x \in \mathcal{F}} \text{shots}(x)}{N_{\text{shots}}} \times 100\%$$
   Quantifies the probability of measuring a solution that strictly satisfies the budget constraint.
