---
name: Experiment Reproducibility
description: Use when running, repeating, or comparing any benchmark, sweep, simulation, or QAOA experiment in this repository. Covers experiment IDs, output naming, seeding, run metadata, and honest comparison of results. Use before and after running anything that writes to outputs/ or research-log/.
---

# Experiment Reproducibility

Make every experiment re-runnable by someone else, and make every reported number traceable to a file on disk.

Project context: **Quantum Resource Optimizer** — constrained green energy asset and portfolio allocation solved with QAOA (Qiskit Fall Fest 2026, Track 2).

---

## 1. When to activate

Activate this skill when:

- Running any QAOA solve, parameter sweep, depth sweep, penalty sweep, or baseline comparison.
- Producing anything under `outputs/runs/`, `outputs/plots/`, or `outputs/circuits/`.
- Reporting a number in `README.md`, `docs/`, or `research-log/` that came from an execution.
- Re-running a previous experiment to confirm or refute a claim.
- Answering "what happens if we change X?" with a measurement.

Do **not** activate it for unit tests with no recorded metrics — that is `python-testing`.

---

## 2. Experiment IDs

Use a stable, sortable ID assigned once and never reused:

```
EXP-<NNN>-<slug>
```

| Field | Rule | Example |
|---|---|---|
| `NNN` | Zero-padded, sequential, 3 digits | `001` |
| `slug` | lowercase kebab-case, describes the *question* not the run | `qaoa-depth-sweep` |

Examples:

```
EXP-001-baseline-greedy-vs-exact
EXP-002-qaoa-depth-sweep-p1-p4
EXP-003-penalty-strength-lambda
EXP-004-instance-scaling-n4-n8
```

**The ID identifies the question.** Seeds, shot counts, and depth values go in the run metadata, never in the ID. `EXP-002-seed42` and `EXP-002-seed43` are the *same* experiment.

---

## 3. Output naming

```
outputs/
├── runs/       <EXP-ID> / run.json      machine-readable metadata + metrics
│               <EXP-ID> / summary.csv    one row per configuration
├── plots/      <EXP-ID>-<metric>.png    one figure per claim
└── circuits/   <EXP-ID>-<config>.png    circuit diagrams, QAOA depth labelled
```

Rules:

- Never overwrite a previous run. Each run gets its own file or its own subdirectory.
- Include the seed in the filename when a comparison spans seeds.
- Use the experiment ID in **every** artifact so figures and tables can be traced back.

Good: `outputs/runs/EXP-002-qaoa-depth-sweep-p1-p4/run.json`,
`outputs/plots/EXP-002-approximation-ratio-vs-depth.png`

Bad: `results.png`, `final_results_v2.json`, `output1.csv`

---

## 4. Seeding and reproducibility limits

Always record the seed. Always state what the seed does and does not guarantee.

```python
SEED = 42
np.random.seed(SEED)
algorithm_quantum.random_seed = SEED   # Qiskit transpiler/runtime seed
```

**Seeded and deterministic** (given identical library versions):

- Problem instance generation
- Classical solver with deterministic tie-breaking
- QAOA initial parameter vectors

**Not fully reproducible even with a fixed seed:**

- Shot-based sampling — results vary run to run; statevectors (`StatevectorSampler`) are deterministic, `Aer` shots are not.
- Variational optimization — COBYLA/SPSA land on slightly different points across backends and library versions.
- Transpiler output — layout and routing depend on the installed transpiler version and optimization level.
- Anything on real hardware — drift, queue state, and calibration data change daily.

**Never claim "bit-identical reproducibility."** Claim instead: *"reproducible to within statistical sampling error; seed recorded; run metadata captures library versions."*

Record these limits in `research-log/` rather than hiding them. They are part of the honest-limitation criterion the hackathon grades on.

---

## 5. Required run metadata

Every run writes machine-readable metadata. JSON is the source of truth; CSV is a derived convenience view.

```json
{
  "experiment_id": "EXP-002-qaoa-depth-sweep-p1-p4",
  "timestamp_utc": "2026-10-11T09:14:22Z",
  "seed": 42,
  "algorithm": {
    "name": "qaoa",
    "depth_p": 2,
    "shots": 2048,
    "optimizer": "COBYLA",
    "initial_params": [0.1234, -0.5678]
  },
  "problem": {
    "instance_id": "inst-n6-k2-seed42",
    "num_assets": 6,
    "budget_k": 2,
    "num_qubits": 6
  },
  "environment": {
    "python": "3.12.4",
    "qiskit": "1.2.4",
    "qiskit_aer": "0.15.1",
    "numpy": "2.1.3",
    "platform": "win32"
  },
  "execution": {
    "backend": "StatevectorEstimator",
    "noise_model": null,
    "transpiler_optimization_level": 1
  },
  "timing": {
    "runtime_seconds": 18.42,
    "total_shots_simulated": 2048
  },
  "metrics": {
    "best_cost": 4.0,
    "best_bitstring": "010011",
    "approximation_ratio": 0.5714,
    "feasibility_yield": 0.9375,
    "optimizer_iterations": 143,
    "converged": true
  },
  "artifacts": {
    "plot": "outputs/plots/EXP-002-approximation-ratio-vs-depth.png",
    "circuit": "outputs/circuits/EXP-002-p2.png"
  },
  "errors": []
}
```

**Capture version numbers programmatically**, never by hand:

```python
import importlib.metadata as md
versions = {p: md.version(p) for p in ("qiskit", "qiskit-aer", "numpy")}
```

Mandatory in every run: `experiment_id`, `seed`, algorithm parameters, input sizes, dependency versions, backend/simulator, runtime, metrics, output paths, errors.

---

## 6. Record errors, do not hide them

Failed and partial runs are data. Write them out with `"errors": [...]` and `"converged": false` rather than deleting them or quietly retrying until something looks good.

Record: the exception type, the message, the traceback summary, and the configuration that triggered it. A documented failure that later gets fixed is a positive research-log entry, not a blemish.

Never fabricate, interpolate, or "estimate" a metric that did not run. If a number is absent, write `null` and say so.

---

## 7. Comparing runs

Compare only against runs that share a comparable problem instance.

```python
# Correct: same instance, different depth
before = load("EXP-002/seed42-p1.json")
after  = load("EXP-002/seed42-p2.json")
delta = after["metrics"]["approximation_ratio"] - before["metrics"]["approximation_ratio"]
```

Before reporting a difference, confirm:

1. **Same problem instance** (identical `instance_id`, not just identical size).
2. **Same feasibility definition** — a change in the constraint checker invalidates the comparison.
3. **Same metric definition** — approximation ratio is only meaningful against a verified optimum.
4. **Seeds recorded on both sides**, and ideally more than one seed per configuration.

**Never invent comparison data, interpolate between points, or present an unexecuted configuration as if it had run.** If only three depths were tested, the figure shows three depths. If the baseline was not run, the comparison table stays empty — do not fill it with a remembered number or a textbook expectation.

---

## 8. Update the experiment log

After a run:

1. Append to `research-log/logs/` — a dated entry with the experiment ID, the question, the command, and what actually happened.
2. Update `PROJECT_STATUS.md` under "Last Verified Tests" or the relevant phase, using only verified results.
3. Update `docs/` or `README.md` **only** with numbers traceable to a file in `outputs/runs/`.
4. If the run contradicts a documented claim, correct the claim rather than softening it.

Write findings as *verified*, *inconclusive*, or *refuted*. If a result is inconclusive, say so — that is a legitimate and creditable outcome.