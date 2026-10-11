---
name: Python Testing
description: Use when writing, changing, or verifying any Python code, especially problem formulation, cost Hamiltonians, QAOA solvers, decoders, or classical baselines. Covers hand-checked math, edge cases, exact-solution cross-checks, Qiskit feasibility checks, and the rule that tests are never claimed as passing without being executed.
---

# Python Testing

Prove the mathematics is right before claiming the quantum result is meaningful.

Project context: **Quantum Resource Optimizer** — constrained green energy asset and portfolio allocation solved with QAOA. Source lives in `src/quantum_optimizer/`; tests live in `tests/`.

---

## 1. When to activate

Activate this skill when:

- Writing or modifying any file under `src/` or `tests/`.
- Changing `problem.py`, `hamiltonian.py`, `qaoa_solver.py`, or `classical_solvers.py`.
- Reporting that a bug is fixed.
- About to state that the implementation is correct, tested, or working.
- Reviewing a diff that touches objective functions, penalties, encoding, or decoding.

A clean-looking result from an unverified cost function is worse than no result: it launders a math error into a "quantum advantage" claim.

---

## 2. Hand-checked examples first

Every objective function, penalty term, and decoder gets at least one test whose expected value was **computed by hand on paper**, not by running the code and recording whatever it printed.

Worked pattern:

```python
def test_penalty_term_hand_calculated():
    """Two assets, K=1. Picking 2 violates the budget by exactly 1."""
    # Budget constraint: (x0 + x1 - K)^2 with K = 1
    # x = (1, 1)  ->  (1 + 1 - 1)^2 = 1
    assert budget_penalty([1, 1], K=1) == pytest.approx(1.0)
    # x = (1, 0)  ->  (1 + 0 - 1)^2 = 0
    assert budget_penalty([1, 0], K=1) == pytest.approx(0.0)
```

If a test's expected value was produced by the implementation itself, it is a regression test, not a correctness test. Label it honestly and add a separate hand-derived case.

---

## 3. Input validation and edge cases

Test the boundaries, not just the nominal case.

| Category | Cases |
|---|---|
| Sizes | `n = 0`, `n = 1`, `n = 2`, largest supported, one over the documented cap |
| Budget | `K = 0` (must select nothing), `K = n` (select everything), `K < 0`, `K > n` |
| Malformed | Wrong-length bitstring, non-binary values (`2`, `-1`, `0.5`, `True` confusion), `None`, empty list |
| Numeric | Zero coefficients, negative returns, tied values (tie-breaking), very large magnitudes |
| Types | Bit ordering convention: is index 0 the LSB? Assert it explicitly in a test |

Every public function should reject invalid input with a clear error rather than silently producing a wrong answer. Assert the *behaviour you intend*, including the exception type.

---

## 4. Objective, constraints, encoding, decoding

These four are tested as one round-trip:

1. **Objective function** — matches the hand calculation for known assignments.
2. **Constraints** — feasible and infeasible assignments classified correctly; check the feasibility rule independently of the penalty weight.
3. **Encoding** — classical decision vector → qubit layout. Assert the mapping explicitly (e.g. `bit i of the bitstring corresponds to asset i`, plus endianness).
4. **Decoding** — sampled bitstring → back to a decision vector. Assert the inverse property.

```python
def test_encode_decode_round_trip():
    for x in ([1, 0, 1, 0], [0, 1, 1, 1], [1, 1, 1, 1]):
        bits = encode(x)
        assert decode(bits) == x
```

**Endianness is the classic silent bug in QAOA projects.** A decode that reverses bit order still returns *a* bitstring and still looks plausible — it just means the wrong assets get selected. Pin it with an explicit test that distinguishes `[1,0]` from `[0,1]`.

---

## 5. Exact solutions as an oracle

For small instances, compute the true optimum by brute force and use it as ground truth:

```python
def brute_force_optimum(problem):
    best = None
    for bits in itertools.product([0, 1], repeat=problem.num_assets):
        x = list(bits)
        c = objective(x, problem) if feasible(x, problem) else float("inf")
        if best is None or c < best:
            best = c
    return best
```

Then assert:

- The greedy/classical baseline never beats the exact optimum on small instances (it may tie).
- The reported approximation ratio uses the **verified** optimum, not an assumed one.
- QAOA solutions are always re-scored with the *same* objective used for brute force.

`2^n` is the ceiling — keep oracle tests to `n <= 10` so the suite stays fast. Use `pytest.mark.slow` for the larger sweeps.

---

## 6. Qiskit integration and feasibility

Test the quantum path end to end, not just the classical maths:

- The `SparsePauliOp` has the expected number of terms and the expected Pauli structure.
- The cost operator's lowest eigenvalue corresponds to a **feasible** assignment — check the decoded bitstring against the independent constraint checker.
- Bitstring → cost matches the classical objective for the same assignment (endianness check again).
- The ansatz builds with the intended depth `p` and the expected parameter count (`2p`).
- QuBit count matches `problem.num_assets`.

**Feasibility is evaluated by an independent classical checker, never by the penalty value.** A solution can have a low cost and still violate a hard constraint if `lambda` is too small. Test feasibility directly.

---

## 7. Run the tests — always

```powershell
.venv\Scripts\python -m pytest -v tests/
```

Targeted runs while iterating:

```powershell
.venv\Scripts\python -m pytest tests/test_problem.py::test_name -v
.venv\Scripts\python -m pytest tests/ --lf          # last failed
.venv\Scripts\python -m pytest tests/ -q --tb=short
```

### The reporting rule

**Never state that tests passed without having executed them in this session.**

State the exact command and the real outcome:

> `.venv\Scripts\python -m pytest -v tests/` → **14 passed, 1 failed in 3.21s**.
> Failure: `test_budget_penalty_hand_calculated` — expected 1.0, got 0.0.

Never write "tests pass", "all tests pass", or "this should work" as though verified. If tests were not run, say **"not yet executed"**. If a failure appears, report it and let the user decide whether to fix it or commit anyway — do not quietly delete the test, weaken the assertion, or add a skip to make the suite green.

A skipped test is a reported gap, not a passing test.