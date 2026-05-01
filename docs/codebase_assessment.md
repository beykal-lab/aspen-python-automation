# Codebase Assessment and Refactor Notes

## Current State

The repository currently mixes three different kinds of content:

- A legacy Aspen COM example (`main.py` and `Aspen_to_Data-driven optimization.py`).
- A Week-1 chemical design competition control pack (`config/`, `data/`, `docs/competition/`, `scripts/validate_week1_pack.py`).
- Downloaded literature, external repositories, logs, Aspen binary artifacts, and generated run outputs.

This mixture made basic repository operations fragile. Running `pytest` from the repository root collected tests inside `github_projects/` and `zotero-mcp/`, then failed on unrelated optional dependencies such as `pptx`, `chromadb`, and Unix-only `fcntl`.

## Main Risks Found

1. `main.py` executed Aspen COM automation at import/runtime with hard-coded files and an undefined variable `S1`.
2. Validation logic lived only inside a script, so tests had to import it through `importlib.util` instead of a stable module path.
3. No repository-level `.gitignore` existed, so generated `.bkp`, `.inp`, logs, downloaded PDFs, and external clones appeared as candidate source files.
4. No pytest configuration existed, so unrelated external test suites were collected.
5. Git history boundaries were unclear: source files, competition templates, generated data, and downloaded research assets were all side by side.

## Refactor Performed

- Added `competition_pack.validation` as the importable validation module.
- Kept `scripts/validate_week1_pack.py` as a thin backward-compatible CLI wrapper.
- Replaced `main.py` with a safe argparse entry point:
  - `validate-week1`
  - `legacy-aspen-sample`
- Added pytest configuration in `pyproject.toml` to restrict test collection to `tests/`.
- Added `.gitignore` for Python caches, Aspen artifacts, logs, generated case outputs, downloaded literature, and external clones.
- Updated tests to import the validation module directly and to prove that `main.py --help` does not start Aspen.

## Recommended Git Policy

- Track source code, tests, YAML/CSV templates, docs, and CI configuration.
- Do not track `.bkp`, `.inp`, `.dmp`, generated result CSVs, downloaded PDFs, logs, or external cloned repositories.
- Keep external research automation scripts in a separate branch or folder only when they are intentionally part of the product.
- Use feature branches for changes:
  - `codex/codebase-audit-refactor` for this refactor.
  - `codex/week1-pack` for competition data pack changes.
  - `codex/aspen-runtime` for Aspen automation changes.

## Next Refactor Slice

The next useful slice is to separate the legacy Aspen scripts from the competition pack:

1. Move legacy Aspen examples into `examples/legacy/`.
2. Add a modern, config-driven Aspen runner only after the Week-1 pack is cleanly versioned.
3. Add CI that runs `python -m pytest` and `python main.py validate-week1 --root .`.
4. Add a release checklist before tagging competition milestones.
