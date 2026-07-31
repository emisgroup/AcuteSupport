# AcuteSupport — Management Reports Repository

## Purpose
Store ServiceNow exports, analysis pipelines, and generated executive management reports across AcuteSupport product lines (`Symphony`, `Meds`, `OCM`).

## Standard Repository Layout (per product)
- `data/raw/` — Immutable source CSV exports (do not modify manually)
- `data/processed/` — Cleaned, merged, and classified CSVs (`Merged_Cases_With_SLA_Formatted.csv`)
- `data/archive/` — Historical run backups and timestamped CSVs
- `templates/` — DOCX report templates and `Trends.txt` keyword taxonomies
- `scripts/` — Active data engineering, trend classification, and DOCX generation scripts
- `outputs/` — Clean execution deliverables
  - `outputs/charts/` — Generated PNG visualisations
  - `outputs/tables/` — Metric CSV tables and classification summaries
  - `outputs/reports/` — Final management DOCX reports

## Quick Start
1. Install Python 3.8+ and dependencies:
   ```bash
   python3 -m pip install pandas matplotlib python-docx Pillow
   ```
2. Place source CSV exports in `<product>/data/raw/` using canonical filenames (e.g., `Symphony_Casea_Last_12-Months.csv`, `Symphony_SLA_Last_12-Months.csv`).
3. Run the product-specific report pipeline:
   ```bash
   # Symphony
   cd Symphony && python3 scripts/run_full_report.py

   # Meds
   cd Meds && python3 scripts/build_full_meds_docx_report.py

   # OCM
   cd OCM && python3 scripts/build_full_ocm_docx_report.py
   ```

## Key Governance & Rules
- Source exports in `data/raw/` are preserved for auditability.
- Automated script backups are stored under `data/archive/`.
- Generated deliverables in `outputs/` are excluded from version control via `.gitignore`.
- Refer to each project's `AGENTS.md` for specific taxonomy rules and QA checklists.

**Contact**: Lee Booth (lee.booth@emishealth.com)
