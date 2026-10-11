---
name: ai-commit
description: Creates focused Git commits by inspecting the working tree, recent commit history, diffs, repository conventions, and tests. Use when changes are ready to commit, when the user asks for an automatic or AI-generated commit, or when a coherent set of changes should be committed without mixing unrelated work.
---

# AI Commit Skill

Create one deliberate, repository-consistent Git commit from the current worktree.

## Core rule

A commit is a historical explanation of a coherent change, not a snapshot of everything currently modified.

Never blindly run `git add .` or `git commit -am`.

## Procedure

### 1. Inspect repository state

Run, as appropriate:

- `git status --short`
- `git branch --show-current`
- `git log -8 --oneline`
- `git diff --stat`
- `git diff`
- `git diff --cached`

Also inspect recent commit messages enough to learn the repository's existing convention.

### 2. Identify the commit boundary

Classify changed files into:

- **Relevant changes**: directly part of the current task.
- **Unrelated changes**: edits that appear to belong to another task.
- **Generated/local files**: caches, credentials, build output, temporary files, local databases, notebooks checkpoints, etc.

Do not commit unrelated changes.

If the worktree contains both relevant and unrelated changes, stage only the relevant paths.

If it is impossible to determine the boundary safely, stop and ask the user which files belong in the commit.

### 3. Inspect sensitive files

Before staging, look for likely secrets:

- `.env`
- API keys
- access tokens
- private keys
- credentials
- service-account files
- local database files containing private data

Never stage secrets. If a secret appears to be tracked already, warn the user instead of silently committing it.

### 4. Understand the change

Use the diff and recent history to determine:

- What changed?
- Why did it change?
- Which subsystem is affected?
- Is this a feature, fix, refactor, docs change, data change, test change, chore, or other project-specific category?

Prefer the repository's existing commit vocabulary over inventing a new convention.

### 5. Validate

Run the smallest useful validation that matches the changed files.

Examples:

- Python: project tests, import checks, lint/type checks if configured.
- Data pipeline: relevant script/test or schema validation.
- Frontend: project test/build command if configured.
- Documentation-only change: no expensive test run unless the repo requires it.

Do not invent commands. Check `README.md`, `pyproject.toml`, `package.json`, Makefile, or existing contributor instructions when necessary.

If validation fails:
- Do not commit automatically.
- Report the failure and ask whether to fix it or commit despite it.

### 6. Stage narrowly

Stage only the files belonging to this commit.

Prefer:

`git add <specific paths>`

Use `git add -p` when only part of a file belongs in the commit.

Then inspect:

`git diff --cached --stat`
`git diff --cached`

### 7. Write the commit message

Use the repository's existing style.

If the repo follows Conventional Commits, use:

`type(scope): concise imperative description`

Common types:
- `feat` — new functionality
- `fix` — bug fix
- `refactor` — behavior-preserving restructuring
- `docs` — documentation
- `test` — tests
- `chore` — maintenance
- `data` — dataset/pipeline changes, if the repository uses this category

The subject should describe the actual change, not the work session.

Good:
`feat(rag): add cleaned campus document pipeline`

Bad:
`updated files`
`final changes`
`AI generated commit`

For a small, obvious change, a one-line commit is enough.

### 8. Commit

After staging and validating, create exactly one focused commit.

Do not:
- amend an existing commit unless explicitly requested
- force-reset files
- discard user changes
- push to a remote
- create multiple commits unless explicitly requested

Use the normal commit command with the generated message.

### 9. Verify

Run:

- `git status --short`
- `git log -1 --oneline`

Report:
- commit hash
- commit message
- files committed
- validation performed
- any remaining uncommitted changes

## Important repository-specific behavior

For data/ML projects:

- Treat raw scraped data as a distinct data lifecycle stage.
- Do not accidentally commit huge raw datasets, model weights, caches, virtual environments, or generated vector indexes.
- Check `.gitignore` before staging.
- If a changed data artifact is intentionally versioned, say so in the commit summary.
- Never mix source-code changes with unrelated experimental outputs merely because they changed together.

For Sputnik, preserve the distinction between:
`data/raw` → `data/interim` → `data/processed` → `models/artifacts`

and keep project documentation in `README.md` and `docs/`.

## Output

After committing, give a concise report:

Commit: `<hash> <message>`
Changed: `<short file/path summary>`
Validation: `<commands/checks>`
Remaining: `<anything intentionally left uncommitted>`

If no safe commit can be made, do not manufacture one. Explain the blocking reason.
