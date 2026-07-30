Management Reports Repository

Purpose
Store ServiceNow exports, analysis scripts and generated management reports for multiple products.

Repository layout (per product)
- data/raw/        - original CSV exports (do not edit)
- data/processed/  - cleaned/merged CSVs used by scripts
- data/raw/report_outputs/ - generated charts, CSVs, DOCX
- scripts/         - analysis and pipeline scripts (run from repo root)
- templates/       - DOCX templates and Trends.txt

Quick start
1) Install Python 3.8+ and packages: pandas, matplotlib, python-docx, Pillow
   python -m pip install pandas matplotlib python-docx Pillow
2) Place source CSVs into data\raw\<product>\ using canonical filenames.
3) From repository root run product-specific scripts in scripts\ or run_full_report.py where available.

Notes
- Keep original exports in data/raw/ for audit. Use data/processed/ for intermediates.
- Generated outputs are written to data/raw/report_outputs/; these are excluded in .gitignore.

Contact: Lee Booth (lee.booth@emishealth.com)
