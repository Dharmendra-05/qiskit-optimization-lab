---
name: Qiskit Optimization
description: Use when formulating the green energy allocation problem, building the Ising cost Hamiltonian, implementing QAOA, choosing an algorithm, checking Qiskit API compatibility, or evaluating a classical baseline. Use before writing quantum code and whenever a result is described as optimal or advantageous.
---

# Qiskit Optimization

Model the problem rigorously, then solve it. The quantum part is the last step, not the first.

Project context: **Quantum Resource Optimizer** — constrained green energy asset and portfolio allocation, Qiskit Fall Fest 2026 Track 2. Modules: `problem.py`, `hamiltonian.py`, `qaoa_solver.py`, `classical_solvers.py`.

---

## 1. When to activate

Activate this skill when:

- Choosing or justifying the problem formulation and the algorithm.
- Writing or reviewing anything in `hamiltonian.py` or `qaoa_solver.py`.
- Deciding whether QAOA is appropriate versus VQE, Grover, or another ansatz.
- Wiring up Qiskit primitives, transpilation, or a backend.
- Reporting an approximation ratio, feasibility yield, or "quantum advantage".
- Adding or upgrading a Qiskit dependency.

---

## 2. Read the official requirements first

Before choosing an algorithm, re-read the actual grading criteria — do not rely on memory:

- `qff26-reference/HACKATHON_GUIDE.md` — Track 2 requirements, deadlines, grading focus.
- `qff26-reference/README.md` — mandatory section headings the automated grader parses.
- `qff26-reference/references/track-2-optimization/README.md` — the expected pipeline.

Non-negotiable constraints for this submission:

- **Qiskit must power the quantum core.** Classical tools may do UI, baselines, and analysis only.
- Map the scenario to a **mathematical formulation** with a cost Hamiltonian or explicit binary objective and constraints.
- **Compare against a classical baseline** — the comparison is a graded deliverable, not optional.
- Be **honest about limitations**, including NISQ noise and scaling.

If the requirements ever mandate real hardware, that overrides the local-simulation preference in §7.

---

## 3. State the problem mathematically

Write the formulation before writing code, in `docs/mathematical-formulation.md`:

1. **Decision variables** — one per binary choice, with meaning stated in domain language.
   *e.g. $x_i = 1$ if renewable asset $i$ is selected for funding.*
2. **Objective** — maximise return $r_i$ and carbon offset $c_i$ subject to budget $B$:
   $$\max \; \sum_i (r_i x_i + \beta\, c_i x_i)$$
3. **Constraints** — hard (budget, cardinality, exclusivity) vs. soft (preference, diversity).
4. **Penalty formulation** — how each hard constraint enters the cost:
   $$C(x) = -\text{Objective}(x) + \lambda \sum_j P_j(x)^2$$

State which constraints are hard and must be *satisfied*, not merely penalised. A constraint that is only softly penalised can be violated by the returned solution — the feasibility yield metric exists precisely to measure that.

---

## 4. Choose the formulation and algorithm

Pick from what the problem actually is:

| Problem shape | Natural fit |
|---|---|
| Weighted selection under budget | QUBO / knapsack → **QAOA** |
| Partition / two-cluster assignment | Max-Cut / graph bipartition → QAOA |
| Scheduling as graph colouring | Multi-qubit or penalty-encoded → QAOA, possibly VQE for colour values |
| Exact-cover / set packing | QUBO with high penalties → QAOA |
| Small search space, single optimum bitstring | Grover search is defensible |

QAOA is the default for this track because the track guide explicitly frames the work as QAOA or variational circuits. If a different approach is genuinely better, justify it against the alternative in writing.

**Choose the depth `p` deliberately.** Start at `p = 1`, compare against `p = 2, 3`. Deeper ansätze are not automatically better — the cost is exponential circuit depth and shot budget.

---

## 5. Map to an Ising Hamiltonian

Binary to Pauli-Z via $x_i = \frac{I - Z_i}{2}$:

$$H_C = \sum_{i<j} J_{ij} Z_i Z_j + \sum_i h_i Z_i + \text{offset} \cdot I$$

```python
from qiskit.quantum_info import SparsePauliOp

def build_cost_operator(problem):
    terms, coeffs = [], []
    for (i, j), w in problem.penalty_pairs.items():
        z = ["I"] * problem.num_qubits
        z[problem.index[i]] = "Z"
        z[problem.index[j]] = "Z"
        terms.append("".join(reversed(z)))   # Qiskit little-endian
        coeffs.append(w)
    return SparsePauliOp(terms, coeffs)
```

Two failure modes that silently produce plausible-looking wrong answers:

- **Endianness.** Qiskit `SparsePauliOp` string order is little-endian. Getting it backwards flips which asset each qubit controls.
- **Constant offset.** The identity term shifts all eigenvalues equally. It does not change the argmin, but it *does* change every reported expectation value and therefore every plot and ratio.

Verify by evaluating the cost operator on the basis state of a known assignment and comparing against the classical objective. If they disagree, the mapping is wrong — do not tune `lambda` to compensate.

---

## 6. Check Qiskit versions and API compatibility

API names moved between Qiskit 0.4x and 1.x. Always verify against the **installed** version, never from memory or an old tutorial:

```powershell
.venv\Scripts\python -c "import qiskit, importlib.metadata as md; print(qiskit.__version__); print(md.version('qiskit'))"
.venv\Scripts\python -c "import qiskit_aer; print(qiskit_aer.__version__)"
```

For each Qiskit import used, confirm it exists in the installed build:

```powershell
.venv\Scripts\python -c "from qiskit.circuit.library import QAOAAnsatz; print('ok')"
.venv\Scripts\python -c "from qiskit.primitives import StatevectorEstimator, StatevectorSampler; print('ok')"
```

The starter notebook in `qff26-reference/references/track-2-optimization/` uses the modern `QAOAAnsatz` + `StatevectorSampler`/`StatevectorEstimator` + COBYLA pattern — use it as the structural reference, and treat any older `qiskit.opflow` or `Aer.get_backend()` patterns as outdated.

If an import fails, fix the import. Do not pin to an old Qiskit to make old code run.

---

## 7. Simulate locally first

Default to local, deterministic, free execution:

| Need | Use |
|---|---|
| Exact expectation values, no shot noise | `StatevectorEstimator` |
| Bitstring sampling, deterministic | `StatevectorSampler` |
| Shot noise, transpilation realism | `qiskit_aer.AerSimulator` |
| Noise studies | `NoiseModel` + `AerSimulator` |

IBM Quantum hardware is an **optional extension**, not the default path. It costs time, queues, and credits, and for a 24-hour hackathon it is a poor use of budget. Introduce it only when the requirements demand it or a real hardware run materially strengthens the submission — and record CRN and backend name in the run metadata.

---

## 8. Keep credentials out of source and Git

Never write an API key, token, CRN, or channel name into a `.py`, `.ipynb`, `.md`, or test log.

```python
import os
from qiskit_ibm_runtime import QiskitRuntimeService

token = os.environ.get("QISKIT_IBM_TOKEN")
service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
```

- Load credentials from environment variables or an untracked `.env`.
- `.gitignore` already excludes `.env`, `qiskit-ibm-runtime.json`, `*.pem`, `*.key`, and `id_rsa*` — confirm before staging.
- If a secret ever reaches a commit, treat it as compromised: rotate it, then rewrite history. Report it rather than hoping it is unnoticed.

---

## 9. Evaluate solutions independently

Never trust a quantum result without re-scoring it classically.

```python
best = min(samples, key=lambda s: cost_from_bitstring(s))
x = decode(best)
assert feasible(x), f"infeasible assignment returned: {x}"
reported = objective(x, problem)          # classical recomputation
assert reported == cost_from_bitstring(best)
```

Decode with the documented convention, re-evaluate the objective from the original problem definition (not from the quantum cost operator), and check feasibility with an independent constraint checker. Disagreement between the quantum cost and the classical objective is a finding — report it, do not average it away.

---

## 10. Describe results honestly

Keep these three strictly separate in every report, figure, and README claim:

1. **A good candidate solution** — QAOA returned a feasible bitstring with cost $C$.
2. **A proven optimum** — brute force or an exact solver established $C^\*$, and you can state the ratio $C/C^\*$.
3. **Demonstrated quantum advantage** — QAOA beat the classical baseline *and* you can show it.

Reporting only (1) is normal and expected for a 24-hour hackathon. Do not let the wording slide into (2) or (3) without the evidence to support it.

Also required by the grading criteria:

- Report the **approximation ratio** $C_{\text{QAOA}} / C_{\text{optimal}}$ against a *verified* optimum.
- Report the **feasibility yield** — the fraction of sampled bitstrings satisfying hard constraints — and how it moves with $\lambda$.
- State honestly what breaks at larger $n$ (shot budget, circuit width, optimization difficulty) and how NISQ noise would affect it.

A modest, well-measured, honestly-caveated result scores better than an overstated one. The guide evaluates "honest engineering intuition and acknowledgement of limitations" explicitly.