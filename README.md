# Code and data for "Grade-Dependent Socioeconomic Gradients in Achievement Change Following the COVID-19 Disruption: Year-by-Year Evidence from Pennsylvania School Districts"

Jonathan Yang and Zhigen Zhao. Everything in the manuscript's tables, figures, and supplementary tables can be reproduced from the files in this folder with Python 3.9 or later (`pip install -r requirements.txt`).

## Source data

The Pennsylvania Department of Education (PDE) publishes PSSA results as annual Excel files (district, school, and state level). The 30 source files used here (district, school, and state files for 2015–2019 and 2021–2025) were downloaded from PDE's Assessment Reporting page (https://www.pa.gov/agencies/education/data-and-reporting/assessment-reporting) on September 21, 2026; their names are listed in `DATA_README.md`. They are not redistributed here; `build_dataset.py` reads them from a `Raw_PDE/` folder and writes the two harmonized CSV files below, which are included so that every later step runs without the source files.

- `pssa_district_2015_2025.csv` — one row per year × district × subject × student group × grade (All Students and Economically Disadvantaged; grades 3–8 and district total; number scored and the four performance-level percentages as published). See `DATA_README.md`.
- `pssa_state_2015_2025.csv` — statewide results, same columns, used to anchor the recovered means.

Validation against the Stanford Education Data Archive (`validate_seda.py`) requires SEDA 2025.2 (`seda_admindist_long_gcs_2025.2.csv`, Pennsylvania rows), available from https://edopportunity.org under SEDA's data use agreement; it is not included.

## Pipeline (run in this order)

| Step | Script | Output | Used for |
|---|---|---|---|
| 1 | `build_dataset.py district` / `state` | the two CSV files above | (needs `Raw_PDE/`; outputs included) |
| 2 | `recover_means.py` | `pssa_district_latent_means.csv` | recovered mean achievement for every district × grade × year × group (Section 2.2; anchor year 2017) |
| 3 | `validate_seda.py` | `seda_validation_by_year.csv` | Section 2.3; Supplementary Table S2 |
| 4 | `analysis_v5_manuscript.py` | `analysis_v5_results.md` | Tables 1–3 (first six rows of Table 3), Supplementary Tables S3, S4, S5, and the participation checks |
| 5 | `checks_v6_size_rounding.py` | `checks_v6_results.md` | Table 3 (district-size restrictions and size groups); Supplementary Note S1 (leave-one-out, two further district-size restrictions, rounding) |
| 6 | `checks_v7_quartiles_sample.py` | `checks_v7_results.md` | last column of Table 4 (grade-band difference by poverty quartile) |
| 7 | `checks_v8_revision.py` | `checks_v8_results.md` | Table 4 (change by poverty quartile and grade band); Section 3.3 (association of district economic disadvantage with achievement itself); Section 4.4 (primary contrast in years of typical learning, Bloom et al. 2008 annual gains) |
| 8 | `figures_v5.py` | `Figure_1`, `Figure_2`, `Figure_3` (png, pdf, tif, jpg), `Figure_S1.png` | Figures 1–3; Supplementary Figure S1 |
| 9 | `build_supplement.py`, then `revise_supplement.py` | `Supplementary_Material_v4.md`, then `Supplementary_Material_v7.md` | assembles the supplementary tables from the result files; the second script applies the numbering of the revised manuscript |

Steps 4–7 also print a few intermediate quantities that the manuscript does not report (for example the R² of nested versions of the primary model); the result files included here show exactly what each script prints. The scripts expect to be run from this folder.

Supplementary Table S1 (changes to the PSSA over 2015–2025) was compiled by hand from the 2015 and 2025 PSSA technical reports published by PDE.

## Revision of November 2026

Added in the revision: `checks_v8_revision.py` and its results file, `figures_v5.py` (replaces `figures_v4.py`; adds Figure 1, the statewide means of Table 1, and renumbers the two earlier figures as Figures 2 and 3 without changing them), and `revise_supplement.py`. The numbers reported in the first submission are unchanged. Table and figure numbers in the table above are those of the revised manuscript: the former Supplementary Table S6 is now Table 4 of the main text, the district-size rows of the former Supplementary Table S2 are now in Table 3, and Supplementary Tables S3, S4, S5 and S7 are now S2, S3, S4 and S5.
