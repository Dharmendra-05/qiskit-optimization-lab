---
name: Technical Documentation
description: Use when writing or updating README.md, docs/, research-log/ (including LaTeX), PROJECT_STATUS.md, or any project record. Covers keeping documentation consistent with the implementation, recording design decisions, citing only consulted sources, and separating shipped work from planned work.
---

# Technical Documentation

Documentation must match the code. A README that overstates what exists is worse than no README.

Project context: **Quantum Resource Optimizer** — constrained green energy asset and portfolio allocation with QAOA (Qiskit Fall Fest 2026, Track 2). Documents live in `README.md`, `docs/`, `research-log/`, and `PROJECT_STATUS.md`.

---

## 1. When to activate

Activate this skill when:

- Writing or editing `README.md`, any file in `docs/`, or `research-log/`.
- Updating `PROJECT_STATUS.md`.
- Adding a section, figure, table, equation, or command to the submission.
- Recording a design decision, experiment finding, or limitation.
- Any change that makes an existing document inaccurate.

---

## 2. Keep the document set consistent

These documents describe one system. When behaviour changes, find every document that mentions it:

| Document | Owns |
|---|---|
| `README.md` | Submission summary, mandatory sections 1–7, results, run instructions |
| `docs/fundamentals.md` | Quantum concepts explained for a beginner audience |
| `docs/mathematical-formulation.md` | Decision variables, objective, constraints, Ising mapping |
| `docs/architecture.md` | Module layout, data flow, component responsibilities |
| `docs/requirements-analysis.md` | Requirement traceability against the official template |
| `research-log/` | Dated research journal: questions tried, findings, dead ends |
| `PROJECT_STATUS.md` | Phase progress, verified tests, blockers, next command |

Before editing, grep for the thing you changed:

```powershell
Select-String -Path README.md,docs\*.md -Pattern "approximation ratio"
```

If the implementation changed, every matching document is now stale until updated. Leave no contradiction behind.

---

## 3. Record design decisions

When a choice is made that a reader would otherwise question, capture:

1. **What** changed.
2. **Why** — the constraint, requirement, or evidence that drove it.
3. **Which files** were affected.
4. **How it was verified** — the command run and its actual outcome.

```markdown
### 2026-10-11 — Switched initial parameters to fixed-seed uniform [0, 2π)

**Change:** `qaoa_solver.py` now seeds `initial_params` with `np.random.default_rng(42)`.

**Why:** Unseeded initialisation made depth comparisons non-reproducible; §5 of the
grading criteria weights honest, repeatable benchmarking.

**Files:** `src/quantum_optimizer/qaoa_solver.py`, `tests/test_qaoa_solver.py`

**Verification:** `.venv\Scripts\python -m pytest tests/test_qaoa_solver.py -v`
→ 6 passed in 2.14s. Two repeated runs produced identical parameter vectors.
```

Put dated entries in `research-log/`. Undated claims are unverifiable later.

---

## 4. Cite only what you actually read

A citation implies the source informed the work. Never cite a source you have not opened.

- Real, verified sources go in `references/sources.bib`; reuse existing BibTeX keys rather than duplicating entries.
- If the project used Qiskit tutorial code or the Fall Fest starter notebook, cite it — the hackathon rules require attribution for adapted material.
- **Never invent** a DOI, author list, page number, or arXiv identifier. If the metadata is not confirmed, write the entry without the uncertain field, or omit it.
- A citation formatted but never consulted is fabrication. Prefer fewer, accurate references.

Acknowledge tooling honestly: which model did what, which tools were used, and which work was human-written.

---

## 5. Record model and tool usage accurately

`METADATA.md` and `README.md` both describe provenance. Keep them truthful and consistent.

State plainly:

- Which agent or model produced the implementation, the documentation, and the review.
- Which libraries and versions were used (`requirements.txt`, run metadata).
- That AI assistance was used for brainstorming, debugging, and syntax — and that the team understands and can explain the submitted code. The rules require this explicitly.
- Any external code that was adapted, and where it came from.

Do not imply work was done manually if an agent did it, and do not describe AI-generated boilerplate as if it were hand-engineered. Neither direction is acceptable.

---

## 6. Write for the intended reader

The audience includes judges who may not know quantum computing, and an automated grader parsing structure.

- **Explain commands.** Never present a bare shell line. Give what it does, the expected output, and what a failure looks like:

  ```bash
  # Install dependencies into the active environment
  pip install -r requirements.txt

  # Run the full test suite (expect: "N passed")
  pytest -v tests/
  ```

- **Explain equations.** Introduce symbols before using them. State $x_i$ means before writing $\sum_i x_i$. Give a tiny worked example of a penalty term.
- **Define jargon on first use** — QAOA, cost Hamiltonian, eigenvalue, shot, transpiler.
- **Keep the mandatory README headings exactly as the template provides them.** The automated evaluation parses those headings. Renaming or reordering them breaks grading. Edit the body freely; never the section structure.

---

## 7. Separate what ships from what is planned

Use unambiguous, consistent language:

| State | Wording |
|---|---|
| Implemented and verified | "Implemented. Verified by `<command>` → `<result>`." |
| Implemented, unverified | "Implemented; not yet verified by a recorded run." |
| Partial | "Partial — handles `A` and `B`; `<C>` is not implemented." |
| Planned | "Planned, not implemented." |
| Won't do | "Out of scope for this submission." |

Never describe planned work in the present tense. Never list an unimplemented module in the repository-structure tree as though it exists — a structure diagram is a factual claim about the filesystem.

In the README, keep results and limitations both visible. The grading criteria reward honest critical reflection on NISQ noise, scaling limits, and what the approach cannot yet do.

---

## 8. Keep PROJECT_STATUS.md current

`PROJECT_STATUS.md` is the verified-progress record. Update it after any phase completes, any blocker appears, or any test run happens.

Required sections:

- **Current phase** and last-updated date.
- **Completed work** — checked only when genuinely done.
- **Remaining work** — unchecked, specific, actionable.
- **Last verified tests** — the actual command and its real result, or "None yet".
- **Known blockers** — or "None". Do not leave a stale empty section.
- **Exact next command** — copy-pasteable, correct for this machine.

Rules:

- Only check an item when the work is done *and verified*. Unverified work stays unchecked.
- Copy test outcomes verbatim from the run — never retype an expected result.
- Remove blockers once resolved; do not leave a resolved blocker listed.
- If the next command depends on setup that has not been verified, say so instead of implying it will work.