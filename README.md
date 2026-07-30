Management_Reports

Purpose: store export, processing scripts and management reports per product.

Layout (per product):
  - raw/       -> original exports (do not edit)
  - processed/ -> cleaned or merged CSVs used for analysis
  - reports/   -> generated DOCX/PDF and JSON summaries
  - scripts/   -> analysis scripts (Python)
  - templates/ -> DOCX templates

Naming conventions:
  - Use product in filename and YYYYMMDD prefix for generated files, e.g. Symphony_report_20250729.docx
  - Preserve original files in raw/; processed files may be overwritten.
