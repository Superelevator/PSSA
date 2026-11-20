# Data files built by build_dataset.py from PDE's PSSA files (Raw_PDE/)

Source: Pennsylvania Department of Education, annual PSSA district-level and state-level
results files, 2015-2019 and 2021-2025 (no PSSA in 2020). Nothing is altered or imputed;
the script only harmonizes column names, grade labels and two subgroup spellings, and
selects rows. Re-run `python3 build_dataset.py district` / `state` to rebuild.

## pssa_district_2015_2025.csv  (166,540 rows; 499 traditional districts, no charters)
One row per year x district x subject x group x grade.
- year (2015-2019, 2021-2025), aun, county, district
- subject: English Language Arts, Math, Science (Science: grades 4 and 8 only; no Science in 2025, a field-test year)
- group: All Students, Economically Disadvantaged (other PDE subgroups are in the source files only)
- grade: 3-8 or Total (district total across grades)
- n_scored: students scored (present even when percentages are suppressed)
- pct_advanced, pct_proficient, pct_basic, pct_below_basic: PDE performance-level shares (%),
  each rounded to 0.1, so the four sum to 100 +/- 0.2
- pct_prof_above = pct_advanced + pct_proficient (as reported)
Suppression: cells with n <= 10 have blank percentages.

## pssa_state_2015_2025.csv  (862 rows)
Statewide results, same columns minus aun/county/district. All Students is present for every
year; other groups appear from 2022 on.
Use: reference distributions for anchoring the recovered means (anchor year 2017).

## Analysis years
2015-2019 and 2022-2025. 2021 is kept in the files but excluded from the analysis
(see Section 2.1 of the manuscript).

## Source files (Pennsylvania Department of Education; not redistributed here)

The 30 files below were downloaded from PDE's Assessment Reporting page
(https://www.pa.gov/agencies/education/data-and-reporting/assessment-reporting) on September 21, 2026.
`build_dataset.py` reads the district-level and state-level files from a folder named `Raw_PDE` one level above the scripts.

| Year | District level | School level | State level |
|---|---|---|---|
| 2015 | 2015 pssa district data.xlsx | 2015 pssa school level data.xlsx | 2015 pssa state level data.xlsx |
| 2016 | 2016 pssa district data.xlsx | 2016 pssa school level data.xlsx | 2016 pssa state level data.xlsx |
| 2017 | 2017 pssa district data.xlsx | 2017 pssa school level data.xlsx | 2017 pssa state level data.xlsx |
| 2018 | 2018 pssa district data.xlsx | 2018 pssa school level data.xlsx | 2018 pssa state level data.xlsx |
| 2019 | 2019 pssa district data.xlsx | 2019 pssa school level data.xlsx | 2019 pssa state level data.xlsx |
| 2021 | 2021 pssa district data.xlsx | 2021 pssa school level data.xlsx | 2021 pssa state level data.xlsx |
| 2022 | 2022 pssa district data.xlsx | 2022 pssa school level data.xlsx | 2022 pssa state level data.xlsx |
| 2023 | 2023 pssa district level data.xlsx | 2023 pssa school level data.xlsx | 2023 pssa state level data.xlsx |
| 2024 | 2024-pssa-district-data.xlsx | 2024-pssa-school-data.xlsx | 2024-pssa-state-data.xlsx |
| 2025 | 2025-pssa-district-level-data.xlsx | 2025-pssa-school-level-data.xlsx | 2025-pssa-state-level-data.xlsx |
