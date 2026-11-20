# checks_v6 results: small-district influence, rounding sensitivity, R² decomposition

## A. Small-district influence (primary model, equal district weights)

### English Language Arts
Primary: δ_2022 +0.0159 (SE 0.0041) | contrast +0.0116 (SE 0.0035, p = 0.00097) | N districts 492
District size (median students scored per grade-year, 2015–19) among analytic districts: min 22, P10 57, Q1 89, median 147, Q3 272, max 9199

**A1. Size restrictions**
| Restriction | result |
|---|---|
| exclude districts with any grade-year cell < 30 students (469 districts) | δ_2022 +0.0141 (SE 0.0041) | contrast +0.0110 (SE 0.0035, p = 0.0018) | N districts 469 |
| exclude districts with any grade-year cell < 50 students (405 districts) | δ_2022 +0.0117 (SE 0.0039) | contrast +0.0077 (SE 0.0034, p = 0.022) | N districts 405 |
| exclude districts with median cell < 50 students (465 districts) | δ_2022 +0.0140 (SE 0.0041) | contrast +0.0107 (SE 0.0036, p = 0.0026) | N districts 465 |
| exclude districts with median cell < 100 students (350 districts) | δ_2022 +0.0108 (SE 0.0040) | contrast +0.0076 (SE 0.0033, p = 0.022) | N districts 350 |

**A2. By district-size tercile**
| Tercile (median students per grade-year) | result |
|---|---|
| small (22–108) | δ_2022 +0.0272 (SE 0.0114) | contrast +0.0289 (SE 0.0100, p = 0.0037) | N districts 165 |
| medium (108–222) | δ_2022 +0.0097 (SE 0.0091) | contrast +0.0021 (SE 0.0073, p = 0.77) | N districts 163 |
| large (222–9199) | δ_2022 +0.0117 (SE 0.0042) | contrast +0.0084 (SE 0.0034, p = 0.015) | N districts 164 |

**A3. Leave-one-district-out**
Full-sample δ_2022 +0.0159, contrast +0.0116. Leaving out one district at a time (492 refits, 2.8s):
- δ_2022 ranges +0.0146 to +0.0165 (largest single-district change 0.0013); jackknife SE 0.0041 vs cluster SE 0.0041
- contrast ranges +0.0103 to +0.0122 (largest single-district change 0.0013); jackknife SE 0.0035 vs cluster SE 0.0035
- smallest contrast after any single omission = +0.0103, i.e. 2.9 cluster SEs from zero
- most influential districts for the contrast (omitting the district changes it by): ALIQUIPPA SD (−0.0013; size 74; ED 99%); CLAIRTON CITY SD (−0.0006; size 56; ED 85%); MONESSEN CITY SD (+0.0006; size 56; ED 74%); TITUSVILLE AREA SD (+0.0005; size 140; ED 62%); WALLINGFORD-SWARTHMORE SD (−0.0005; size 270; ED 13%)

### Math
Primary: δ_2022 +0.0164 (SE 0.0041) | contrast +0.0124 (SE 0.0036, p = 0.00064) | N districts 494
District size (median students scored per grade-year, 2015–19) among analytic districts: min 20, P10 57, Q1 88, median 147, Q3 271, max 9228

**A1. Size restrictions**
| Restriction | result |
|---|---|
| exclude districts with any grade-year cell < 30 students (470 districts) | δ_2022 +0.0139 (SE 0.0041) | contrast +0.0106 (SE 0.0035, p = 0.0024) | N districts 470 |
| exclude districts with any grade-year cell < 50 students (405 districts) | δ_2022 +0.0116 (SE 0.0042) | contrast +0.0065 (SE 0.0035, p = 0.065) | N districts 405 |
| exclude districts with median cell < 50 students (465 districts) | δ_2022 +0.0146 (SE 0.0041) | contrast +0.0109 (SE 0.0035, p = 0.0019) | N districts 465 |
| exclude districts with median cell < 100 students (349 districts) | δ_2022 +0.0093 (SE 0.0042) | contrast +0.0060 (SE 0.0036, p = 0.094) | N districts 349 |

**A2. By district-size tercile**
| Tercile (median students per grade-year) | result |
|---|---|
| small (20–107) | δ_2022 +0.0258 (SE 0.0119) | contrast +0.0301 (SE 0.0101, p = 0.003) | N districts 165 |
| medium (108–221) | δ_2022 +0.0073 (SE 0.0103) | contrast -0.0012 (SE 0.0079, p = 0.88) | N districts 165 |
| large (222–9228) | δ_2022 +0.0088 (SE 0.0041) | contrast +0.0076 (SE 0.0038, p = 0.043) | N districts 164 |

**A3. Leave-one-district-out**
Full-sample δ_2022 +0.0164, contrast +0.0124. Leaving out one district at a time (494 refits, 2.6s):
- δ_2022 ranges +0.0155 to +0.0171 (largest single-district change 0.0009); jackknife SE 0.0042 vs cluster SE 0.0041
- contrast ranges +0.0115 to +0.0132 (largest single-district change 0.0009); jackknife SE 0.0036 vs cluster SE 0.0036
- smallest contrast after any single omission = +0.0115, i.e. 3.2 cluster SEs from zero
- most influential districts for the contrast (omitting the district changes it by): FARRELL AREA SD (−0.0009; size 50; ED 100%); CORNELL SD (+0.0009; size 44; ED 89%); FERNDALE AREA SD (−0.0008; size 46; ED 71%); UPPER DUBLIN SD (+0.0006; size 292; ED 11%); WALLINGFORD-SWARTHMORE SD (−0.0006; size 270; ED 13%)

## B. Sensitivity to one-decimal rounding of the published percentages
- reproduction check, English Language Arts: max |mu_pool(rebuilt) − mu_pool(file)| = 5.00e-05
- reproduction check, Math: max |mu_pool(rebuilt) − mu_pool(file)| = 5.00e-05

**B2. No continuity correction** (reported proportions used directly; only empty bins moved to 0.5/n)
- English Language Arts: δ_2022 +0.0159 (SE 0.0041) | contrast +0.0115 (SE 0.0035, p = 0.0011) | N districts 492
- Math: δ_2022 +0.0163 (SE 0.0041) | contrast +0.0122 (SE 0.0036, p = 0.00076) | N districts 494

**B1. Monte Carlo: every published percentage (district and statewide anchor) perturbed by U(−0.05, +0.05) percentage points, 30 draws**
- English Language Arts: δ_2022 mean +0.0159, range +0.0158 to +0.0159, SD across draws 0.00003; contrast mean +0.0116, range +0.0116 to +0.0116; contrast p range 0.00093 to 0.001
- Math: δ_2022 mean +0.0164, range +0.0164 to +0.0165, SD across draws 0.00003; contrast mean +0.0124, range +0.0123 to +0.0125; contrast p range 0.0006 to 0.00067
- for scale: ±0.05 percentage points is ±0.07 students at the median cell (n = 142) and ±0.03 at the 10th percentile (n = 53); the continuity correction moves each cumulative count by 0.5 student

## C. R² of the primary model and of nested versions
| Subject | year effects only | year × band | year × band × poverty (primary) |
|---|---|---|---|
| English Language Arts | 0.260 | 0.288 | 0.291 |
  SD of district-grade changes since 2017 by year (English Language Arts): {2018: 0.163, 2019: 0.174, 2022: 0.23, 2023: 0.224, 2024: 0.228, 2025: 0.244}
| Math | 0.073 | 0.082 | 0.090 |
  SD of district-grade changes since 2017 by year (Math): {2018: 0.175, 2019: 0.193, 2022: 0.247, 2023: 0.244, 2024: 0.257, 2025: 0.26}