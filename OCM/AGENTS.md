# AGENTS.md

## Purpose

Provide a repeatable, auditable agent specification that produces a fully populated, executive-quality DOCX management report from ServiceNow case exports.

This file documents:
- required inputs and exact filenames
- data processing steps and scripts to run
- placeholder-to-field/table/chart mapping for the DOCX template
- trend classification and how to update Trends.txt
- QA and delivery checks

Primary inputs (expected paths relative to repository root):
- data\raw\Symphony_Cases_Last_12-Months.csv  (case export)
- data\raw\Symphony_SLA_Last_12-Months.csv    (SLA durations)
- templates\Cases_Management_Report_Template.docx
- templates\Trends.txt

Primary generated artefacts (locations relative to repository root):
- data/processed/Merged_Cases_With_SLA_Formatted.csv
- outputs/tables/kpi_overview.csv
- outputs/charts/*.png (charts)
- outputs/tables/*.csv (tables)
- outputs/reports/Cases_Management_Report_Completed_tables_filled_final.docx

Note: Historical backups are archived under data/archive/. Canonical outputs are stored under outputs/.

---

# How to run (developer-friendly)

1. Ensure Python 3.8+ and packages: pandas, matplotlib, python-docx, Pillow
   - Install: python -m pip install pandas matplotlib python-docx Pillow
2. Place source CSVs in data\raw\ as named above (or update the variables in scripts).
3. Run merge script (PowerShell or Python) to create data\raw\Merged_Cases_With_SLA.csv and the formatted version.
   - Example PowerShell: Merge on cases.number == sla.task, preserve all cases from case export, add SLA_Business_Time_seconds and SLA_Duration_seconds columns.
4. Run the pipeline from the repository root using the scripts in scripts\ — recommended sequence:
   - python scripts\generate_report_charts.py
   - python scripts\classify_other_trends.py (inspect 'Other')
   - python scripts\apply_new_trends_and_regenerate.py (if new trends approved)
   - python scripts\export_charts_to_docx.py
   - python scripts\fill_tables_advanced.py
   - python scripts\fill_metrics_and_finalize_report.py

A single wrapper command can be added (e.g., python scripts\run_full_report.py) to execute steps 3→6 in order.

---

# Start New Command

When the user gives the command `"Start New"`, the agent must execute the output archiving routine:
- Move all generated files from `outputs/charts/`, `outputs/reports/`, and `outputs/tables/` into their respective target subdirectories under `outputs/Archived/`:
  - `outputs/charts/*` -> `outputs/Archived/charts/`
  - `outputs/reports/*` -> `outputs/Archived/reports/`
  - `outputs/tables/*` -> `outputs/Archived/tables/`
- Move all processed data files from `data/processed/` into `data/archive/`:
  - `data/processed/*` -> `data/archive/`
- **Collision / Conflict Handling**: If a file with the same name already exists in the target archive folder, rename the incoming file by appending a timestamp (`_<YYYYMMDD_HHMMSS>`) before moving it to prevent overwriting existing archived artefacts.
- **Execution**: Run `python scripts/start_new.py`.

---

# Raw File Ingestion & Ignore Rules

- **Ignored Folders**: Ignore any raw files located inside `IgnoredFiles`, `IgnoreFile`, or any subdirectories under `data/raw/` when processing reports.
- Only ingest active top-level `.csv` files located directly in `data/raw/`.

---




# CSV field mapping and normalization rules

The agent must map CSV columns to canonical names before calculation. Use these canonical names in scripts:
- number (case number) — source: Number, Number/number, case_number
- sys_created_on (created date) — parse with day-first format
- resolved_at (resolved date)
- state
- priority
- product
- account
- short_description
- description
- SLA_Business_Time_seconds (from SLA business_duration)
- SLA_Duration_seconds (from SLA duration)

Normalization:
- Trim whitespace, uppercase case keys if necessary.
- Remove stray quotes and unescape newline characters inside CSV fields.
- Preserve leading 'CS' prefixes when present.

If automatic mapping fails or multiple candidate columns exist, prompt user to confirm mapping.

---

# Trend classification and updates

Primary source: templates\Trends.txt. Classification process:
1. Read Trends.txt lines as canonical trend names.
2. Tokenise each trend on "/" and "," into keyword tokens.
3. Classify each case by checking if any token appears (case-insensitive) in Short Description + Description.
4. If multiple trends match, choose the highest-priority trend (order in Trends.txt) or ask the user if ambiguous.
5. For remaining 'Other' cases, run expanded keyword pass, then suggest candidate new trend names based on frequent bigrams.

When a candidate new trend is authorised, append it to templates\Trends.txt (one-per-line) and re-run classification.

Never silently create or rename trends without explicit authorisation.

---

# Placeholder mapping rules (DOCX)

The template must use brace placeholders. Use these conventions and the script will replace them:
- KPI placeholders — {Total Cases}, {Open/UnResolved}, {TTR}, {Top Trend}, {Executive summary}
- Chart placeholders — {Chart:monthly_case_trend}, {Chart:priority_profile}, {Chart:product_distribution}, {Chart:trend_distribution}, {Chart:trend_movement}, {Chart:median_vs_p90}, {Chart:sla_performance}
- Table placeholders — {Table:monthly_case_trend}, {Table:priority_profile}, {Table:product_distribution}, {Table:trend_distribution}, {Table:trend_movement}
- Source data — {Source Data}

Table population rules (use header row to decide):
- Metric tables: first column = metric name; second column = value; third column = notes. Compute values as per KPI rules below and populate notes with short explanations.
- Trend table: first row (header) may contain trend names — if so, interpret subsequent columns (Matching cases, Recent signal from June onwards, Management implication) and fill using trend_distribution.csv and trend_movement.csv. If the template instead lists trends in first column, fill remaining columns per header labels.
- Product/Account/State tables: populate top N (default 10) with counts and open counts where requested.

Never leave table placeholders or header rows empty. If table column names do not match expectations, pause and ask.

---

# KPI calculation rules (precise)

Time to Resolution (TTR): resolved_at - sys_created_on (seconds). Calculate and store in TTR_seconds.
Required KPIs (computed from merged CSV):
- total_cases: count(df)
- closed_cases: count where state contains 'Closed'
- open_cases: total - closed_cases
- resolved_cases: count where resolved_at present
- p1_count..p4_count: parse priority to leading digit, count
- median_ttr_seconds, p90_ttr_seconds, shortest_ttr_seconds, longest_ttr_seconds
- avg_sla_business_seconds, avg_sla_duration_seconds

Formatting durations: present human readable using "[DD] days, [HH] hrs, [MI] mins", suppress zero components.
Store original seconds under columns *_seconds for verification.

P4 deep-dive: filter priority == 4, compute volume, median and P90, list shortest and longest with case number and summary.

---

# Recommended management action derivation

Populate recommended actions automatically by scanning high-volume trends and known automation opportunities:
- For top trends (volume > 10%): recommend KB + automation (P1)
- For medium trends (3–10%): recommend triage rules, KB (P2)
- For low-volume recurring items: monitor and add KB if repeatable (P3)

Scripts populate Recommendation table with columns: Priority, Recommendation, Rationale.

---

# Quality assurance and checks

Before finalising report, verify:
- All placeholders replaced (scan for '{' in DOCX).
- All tables populated (no header-only tables remaining).
- Trend distribution counts sum to total_cases (or explain differences).
- Durations formatted and *_seconds columns preserved.
- No patient-identifiable text included in the Executive Summary or tables.

Scripts write backups before overwriting files (see data\raw\ for backups). Keep backups for audit trail.

---

# Automation notes

- Scripts included:
  - generate_report_charts.py (computes KPIs, charts, tables)
  - classify_other_trends.py (inspect 'Other' items and propose candidates)
  - apply_new_trends_and_regenerate.py (apply authorised new trends and rerun)
  - export_charts_to_docx.py (insert charts and basic KPI placeholders)
  - fill_tables_advanced.py (populate tables using CSV tables)
  - fill_metrics_and_finalize_report.py (final KPIs, exec summary, source data, appendix)

- To rerun for new data: replace CSVs in data\raw\, run run_full_report.py which executes scripts in order and produces final DOCX in data\raw\report_outputs.

---

# Versioning and change control

- When Trends.txt or the template is changed, increment the local change log (templates/CHANGELOG.md) with rationale.
- All automated runs must keep a timestamped backup of the merged CSV and the previous DOCX.

---

# Troubleshooting

- If many cases remain 'Other', run classify_other_trends.py to get suggested tokens and ask user to confirm new trends.
- If date parsing fails, confirm date format and adjust dayfirst flag in scripts.
- If images do not appear in DOCX, ensure the PNGs exist in data\raw\report_outputs and that the template uses the chart placeholders described above.

---

# Final Deliverable

When followed, the agent will produce:
- A fully completed DOCX report (data\raw\report_outputs\Cases_Management_Report_Completed_tables_filled_final.docx)
- Supporting CSVs and chart images for audit and reuse

No placeholders. No draft sections. No assumptions unauthorised by the user.


# P4 Analysis Rules

Always include:

## P4 Volume

Count

Percentage of total.

---

## P4 Trending

Trend clusters.

---

## P4 Median TTR

---

## P4 P90 TTR

---

## Longest P4

Include:

Case Number

Summary

Duration

---

## Shortest P4

Include:

Case Number

Summary

Duration

---

# Trend Reporting

Always generate:

## Trend Volume

Cases by trend.

---

## Trend Evolution

Trend movement by month.

---

## Trend TTR

Per trend:

- Median TTR
- P90 TTR

---

## Trend Risk

Management interpretation.

---

# Management Observations

After every significant section include:

## Management Observation

Interpret:

- demand patterns
- service impacts
- operational implications
- process bottlenecks
- workload concentration

Do not simply repeat chart findings.

Explain why they matter.

---

# Service Improvement Analysis

Always look for:

## Knowledge Base Opportunities

Examples:

- repeat audits
- access requests
- printing issues
- recurrent support questions

---

## Automation Opportunities

Examples:

- password resets
- access requests
- audit requests
- standard data requests

---

## Triage Opportunities

Examples:

- high volume low complexity work
- repeat demand
- inefficient routing

---

# Recommended Actions

Categorise:

## Priority 1

Highest impact.

## Priority 2

Medium impact.

## Priority 3

Long-term optimisation.

Always provide rationale.

---

# Executive Summary Rules

Written for senior management.

Must answer:

1. What happened?
2. Why does it matter?
3. What should leadership do?

Avoid technical language.

---

# Report Sections

Minimum required order:

1. Executive Summary
2. KPI Overview
3. Case Volume Analysis
4. Priority Analysis
5. Product Analysis
6. Trend Analysis
7. TTR Analysis
8. SLA Analysis
9. P4 Deep Dive
10. Management Recommendations
11. Methodology
12. Caveats

Unless the template requires a different order.

---

# Chart Requirements

Generate where supported:

## Monthly Case Trend

Line chart.

## Priority Profile

Bar chart.

## Product Distribution

Bar chart.

## Trend Distribution

Bar chart.

## Trend Movement

Monthly trend movement.

## Median vs P90

Comparison chart.

## SLA Performance

Where available.

---

# Quality Assurance Rules

Before delivery:

Verify:

- No placeholders remain.
- All tables populated.
- All chart placeholders replaced.
- Trend classifications validated.
- Durations formatted correctly.
- UK spelling used.
- Executive summary present.
- Caveats populated.

---

# Uncertainty Rules

When unsure:

STOP.

Never guess.

Never fabricate.

Ask the user:

- Confirm trend name
- Confirm field mapping
- Confirm interpretation

Only continue after clarification.

---

# Privacy Rules

Never report:

- Patient identifiable data
- Raw descriptions containing patient information
- Raw work notes
- Analyst rankings
- Individual performance comparisons

Aggregate all sensitive content.

---

# Analyst Protection Rule

Do not:

- Score analysts
- Rank analysts
- Compare analysts

Focus on:

- Demand
- Process
- Service quality
- Operational trends

---

# Language

English (United Kingdom)

Use:

- prioritised
- analysed
- optimisation
- organisation
- behaviour

Avoid US spellings.

---

# Final Deliverable

Primary output:

- Fully completed downloadable DOCX report

Secondary output:

- Short management summary in chat

No placeholders.

No draft sections.

No incomplete charts.

No assumptions without confirmation.

## ServiceNow Trend Classification Trigger

If the user request contains any of the following phrases or intent:

- ServiceNow trends
- trend categories
- classify cases
- categorise cases
- exported CSV
- Short Description
- Description
- Close Notes
- case trends
- ticket trends
- incident trends
- audit request
- performance trend

Then use the specialist instructions from:

`agents/servicenow-trend-classifier/AGENTS.md`

The specialist instructions override general classification behaviour for this task.

The agent must:
- Use the predefined taxonomy.
- Classify every case individually.
- Assign one Trend Category and one Sub-Category.
- Provide confidence scoring.
- Provide summary counts.
- Avoid unnecessary personal data exposure.
- Mark unclear cases for manual review.