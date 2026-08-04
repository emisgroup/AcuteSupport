# CLAUDE.md

Repository root. This file is a router — the real specs live per product.

## Products

Three independent report pipelines, each self-contained with the same internal layout
(`data/{raw,processed,archive}`, `templates/`, `scripts/`, `outputs/{charts,tables,reports}`):

| Product | Spec | Sub-agent spec |
| --- | --- | --- |
| `Symphony/` | `Symphony/AGENTS.md` | `Symphony/agents/servicenow-trend-classifier/AGENTS.md` |
| `Meds/` | `Meds/AGENTS.md` | — |
| `OCM/` | `OCM/AGENTS.md` | `OCM/agents/servicenow-trend-classifier/AGENTS.md` |

Each `AGENTS.md` is the authoritative spec for its product: required input filenames, the
processing scripts to run in order, placeholder-to-field/table/chart mapping for the DOCX
template, trend taxonomy rules, and QA checks. Read the relevant one before touching a
pipeline. Make edits there, not in the sibling `CLAUDE.md`.

## Working directory matters

Each product dir has a `CLAUDE.md` that imports its `AGENTS.md` via `@AGENTS.md`. That
import is resolved against the **current working directory**, not the importing file, so
it only loads when Claude is started from inside the product directory:

```bash
cd Symphony && claude     # loads Symphony/AGENTS.md
cd OCM && claude          # loads OCM/AGENTS.md
```

Started from this root (or any other directory), the product specs do **not** auto-load and
there is no warning. Read the relevant `AGENTS.md` explicitly instead.

## Shared code

- `run_all.py` — orchestrator. Runs `shared/scripts/{run_full_report,start_new}.py` with the
  working directory set to the chosen product dir, so the shared scripts resolve their
  relative paths against that product.
  ```bash
  python run_all.py --product Symphony        # one product
  python run_all.py --all                     # all three, sequentially
  python run_all.py --all --action start_new  # reset for a new reporting cycle
  ```
- `shared/scripts/`, `shared/templates/` — code and templates common to all three products.
- Per-product `scripts/` also contain product-specific builders (e.g.
  `OCM/scripts/build_full_ocm_docx_report.py`).

Dependencies: Python 3.8+ with `pandas`, `matplotlib`, `python-docx`, `Pillow`.

## Governance

- `data/raw/` exports are immutable — never edit them by hand; they exist for auditability.
- Script-generated backups land in `data/archive/`.
- **Nothing is ignored — by design.** The `.gitignore` was deliberately removed: generated
  deliverables under `outputs/` are version-controlled artefacts, so charts, tables, and
  DOCX/PDF reports are all committed (~295 tracked files). Expect pipeline runs to produce
  large diffs of regenerated outputs; that is expected, not noise to suppress. Do not add a
  `.gitignore` or `git add`-exclude generated files.
  (`README.md` line 38 still says outputs are excluded — stale, needs correcting.)
