"""build_supplement.py -- assemble Supplementary_Material_v2.md (Tables S1-S7, Figure S1) from
analysis_v5_results.md, seda_validation_by_year.csv (validate_seda.py) and checks_v6_results.md."""
import pandas as pd
R = open("analysis_v5_results.md").read().split("\n")
def table_after(pat, offset=1, n=8):
    i = next(k for k, l in enumerate(R) if l.strip() == pat); return "\n".join(R[i + offset:i + offset + n])
def after(pat, n):
    i = next(k for k, l in enumerate(R) if l.startswith(pat)); return "\n".join(R[i + 1:i + 1 + n])
G = next(k for k, l in enumerate(R) if l.startswith("### Grade-specific poverty slopes"))
def table_from(start, pat, n=8):
    i = next(k for k, l in enumerate(R) if k > start and l.strip() == pat); return "\n".join(R[i + 1:i + 1 + n])
S1_ela = table_from(G, "English Language Arts"); S1_math = table_from(G, "Math")
S2_ela = after("English Language Arts — same slopes arranged by cohort", 11); S2_math = after("Math — same slopes arranged by cohort", 11)
S3_ela = after("English Language Arts: median tested-count ratio", 10); S3_math = after("Math: median tested-count ratio", 10)
def clean(t):
    for a, b in [("('Q1 low', 'early')", "Q1 (lowest poverty), grades 3–5"), ("('Q1 low', 'late')", "Q1, grades 6–8"), ("('Q2', 'early')", "Q2, grades 3–5"), ("('Q2', 'late')", "Q2, grades 6–8"),
                 ("('Q3', 'early')", "Q3, grades 3–5"), ("('Q3', 'late')", "Q3, grades 6–8"), ("('Q4 high', 'early')", "Q4 (highest poverty), grades 3–5"), ("('Q4 high', 'late')", "Q4, grades 6–8"),
                 ("r2019", "2019"), ("r2022", "2022"), ("r2023", "2023"), ("r2024", "2024"), ("|                      |", "| Poverty quartile, band |")]:
        t = t.replace(a, b)
    return t
S4 = pd.read_csv("seda_validation_by_year.csv")
for c in ["r, change since 2019 (recovered mean)", "r, change since 2019 (percent proficient)"]:
    S4[c] = S4[c].apply(lambda v: "—" if pd.isna(v) else f"{v:.3f}")
S4["share of PDE cells (%)"] = S4["share of PDE cells (%)"].astype(int)
S4.columns = ["Year", "Cells matched", "% of PDE cells", "r, level (median)", "r, level (min–max)", "r, % proficient", "r, ED level", "r, change (rec. mean)", "r, change (% prof.)"]
S4md = S4.to_markdown(index=False)

doc = f"""# Supplementary Material

**Grade-Dependent Socioeconomic Gradients in Achievement Change Following the COVID-19 Disruption: Year-by-Year Evidence from Pennsylvania School Districts**

Jonathan Yang and Zhigen Zhao

All estimates use the recovered mean (pooled standard deviation) described in Section 2.2 of the main text, the analytic sample of Section 2.5, and districts weighted equally. Units are standard deviations of the 2017 statewide student distribution for the relevant subject and grade.

## Supplementary Table S1. Grade-specific association between district economic disadvantage and the change in recovered mean achievement since 2017

Entries are coefficients from a separate regression of the change since 2017 on the centered economic-disadvantage share for each grade and year, in standard deviations per 10 percentage points of economically disadvantaged students, with standard errors clustered by district in parentheses. The 2019 and 2022 rows are plotted in Figure 2.

ELA

{S1_ela}

Mathematics

{S1_math}

## Supplementary Table S2. The same grade-specific estimates arranged by cohort

Rows are cohorts identified by the grade the cohort was in during spring 2020 (grade tested minus the number of years after 2020; 0 is kindergarten and negative values are cohorts that had not yet entered kindergarten in 2020). Columns are test years. Each entry repeats the estimate from Table S1 with the tested grade in parentheses.

ELA

{S2_ela}

Mathematics

{S2_math}

## Supplementary Table S3. Participation: median ratio of the number of students scored to the 2017 number, by district poverty quartile, grade band, and year

The ratio is computed for each district-grade and the median is taken within poverty quartile (pre-2020 economically disadvantaged share) and grade band.

ELA

{clean(S3_ela)}

Mathematics

{clean(S3_math)}

In 2022 the late-minus-early difference (δ_2022) estimated on district-grades whose 2022 count was within 5 percent of the 2017 count is 0.025 (SE 0.007; 698 cells) in ELA and 0.025 (SE 0.007; 708 cells) in mathematics. Within poverty quartiles, the correlation between the count ratio and the change in achievement is −0.07, −0.02, −0.05, and −0.01 (ELA, quartiles 1 to 4) and 0.01, −0.08, −0.16, and −0.07 (mathematics).

## Supplementary Table S4. Validation against SEDA 2025.2 by year

Correlations are computed within subject, grade, and year across the 495 name-matched districts and summarized over the subject-grades available in each year (12 through 2019, 8 from 2022) (median, and minimum to maximum for the recovered mean). Level correlations are between our recovered mean (or the percentage proficient or above, or the recovered mean for the economically disadvantaged group) and the corresponding SEDA estimate; change correlations are for district-grade changes since 2019. SEDA's Pennsylvania estimates after 2019 cover grades 3–6 only. Changes are from 2019 to the year shown.

{S4md}

## Supplementary Table S5. Small-district influence and rounding sensitivity

Primary model (Table 2); δ_2022 is the 2022 late-minus-early difference and the contrast is δ_2022 minus the mean of δ_2018 and δ_2019; standard errors clustered by district, in parentheses, with p-values for the contrast. District size is the median number of students scored per grade-year over 2015–2019.

| Variant | ELA δ_2022 (SE) | ELA contrast (p) | Mathematics δ_2022 (SE) | Mathematics contrast (p) | Districts (ELA / mathematics) |
|---|---|---|---|---|---|
| Primary | 0.016 (0.004) | 0.012 (0.001) | 0.016 (0.004) | 0.012 (0.0006) | 492 / 494 |
| Exclude districts with any grade-year cell below 30 students | 0.014 (0.004) | 0.011 (0.002) | 0.014 (0.004) | 0.011 (0.002) | 469 / 470 |
| Exclude districts with any grade-year cell below 50 students | 0.012 (0.004) | 0.008 (0.02) | 0.012 (0.004) | 0.007 (0.07) | 405 / 405 |
| Exclude districts with median cell below 50 students | 0.014 (0.004) | 0.011 (0.003) | 0.015 (0.004) | 0.011 (0.002) | 465 / 465 |
| Exclude districts with median cell below 100 students | 0.011 (0.004) | 0.008 (0.02) | 0.009 (0.004) | 0.006 (0.09) | 350 / 349 |
| Smallest size tercile (20–108 students) | 0.027 (0.011) | 0.029 (0.004) | 0.026 (0.012) | 0.030 (0.003) | 165 / 165 |
| Middle size tercile (108–222 students) | 0.010 (0.009) | 0.002 (0.77) | 0.007 (0.010) | −0.001 (0.88) | 163 / 165 |
| Largest size tercile (222–9,228 students) | 0.012 (0.004) | 0.008 (0.02) | 0.009 (0.004) | 0.008 (0.04) | 164 / 164 |
| No continuity correction in the scoring step | 0.016 (0.004) | 0.012 (0.001) | 0.016 (0.004) | 0.012 (0.0008) | 492 / 494 |

Tests of equal δ_2022 across the three terciles: p = 0.41 (ELA) and 0.38 (mathematics); of equal contrasts: p = 0.09 and 0.05.

Leave-one-district-out: refitting the primary model with each district omitted in turn, δ_2022 ranges from 0.0146 to 0.0165 in ELA and from 0.0155 to 0.0171 in mathematics; the largest change from omitting a single district is 0.0013 (ELA) and 0.0009 (mathematics); the jackknife standard errors (0.0041 and 0.0042) match the cluster-robust standard errors (0.0041 and 0.0041) to within 0.0001.

Rounding: with every published percentage (district and statewide anchor) perturbed independently by a uniform draw within its rounding interval of ±0.05 percentage points and the scoring and model re-run (30 draws), δ_2022 ranges from 0.0158 to 0.0159 in ELA and from 0.0164 to 0.0165 in mathematics, and the contrast p-value from 0.0009 to 0.0010 and from 0.0006 to 0.0007. At the median cell (142 students scored), ±0.05 percentage points corresponds to ±0.07 students.

## Supplementary Table S6. Changes to the PSSA in ELA and mathematics, 2015–2025

Compiled from the 2015 and 2025 PSSA technical reports (DRC, 2015, Chapters 13 and 15; DRC, 2026, Preface pp. 12–34, Chapter 13 p. 153, Chapter 15 pp. 158–159 and 165, Chapter 19 pp. 215–216, Appendix S p. 607). "Same" means no change from the previous year is reported. Computer-based shares are reported for the years in which the 2025 report states them; the online option existed throughout.

| Year | Standards and test design | Standard setting or validation | Equating and scale maintenance | Scaled-score cut scores | Computer-based testing | Other |
|---|---|---|---|---|---|---|
| 2015 | First PSSA aligned to the Pennsylvania Core Standards in ELA and mathematics; new scales; original test length (mathematics 72 points; ELA 62 points in grade 3 and 84 in grades 4–8, including a writing prompt) | Bookmark standard setting, June 9–12, 2015 | Base year; no linking to earlier assessments | Set (DRC, 2015, Table 13–3) | Online option available; share not stated | — |
| 2016 | Same | — | Chained linking to the 2015 base scale; post-equating | Unchanged | Share not stated | — |
| 2017 | Same | — | Same | Unchanged | Share not stated | Reference year of this study |
| 2018 | Reduced-length tests first administered: mathematics 72 to 52 points by proportional reduction of each reporting category; ELA writing prompt and about nine stand-alone multiple-choice language items removed (grade 3 62 to 45 points; grades 4–8 84 to 63 points) | ELA standards validation, June 2018 (modified Bookmark), confirmed the 2015 cut scores | Same | Unchanged | Share not stated | — |
| 2019 | Same | — | Pre-equating design introduced (previously linked item parameters used for form construction and scoring tables) | Unchanged | 3–7 percent | — |
| 2020 | No administration (cancelled March 2020) | — | — | — | — | — |
| 2021 | Same design; testing window April to September | — | Pre-equating; operational item parameters not updated because of pandemic impacts (disruption, lower participation, elongated windows) | Unchanged | Substantial increase over 2019; share not stated | Excluded from this study; participation 67 percent in the Lipscomb et al. (2022) target population |
| 2022 | Same; ELA tested in April, mathematics in May | — | Pre-equating; operational item parameters re-estimated only for items showing misfit or displacement | Unchanged | Roughly stable 2021–2024; share not stated | — |
| 2023 | Same | — | Same | Unchanged | Share not stated | — |
| 2024 | Same | — | Same | Unchanged | 23–38 percent | — |
| 2025 | Same for ELA and mathematics; science administered as a stand-alone field test (no performance levels) | — | Same | Unchanged; identical to 2015 (DRC, 2026, Table 13–2) | 51–62 percent | Person-fit analyses indicate similar functioning across modes; no formal mode study; full online testing planned for 2026 |

## Supplementary Table S7. The grade-band difference by district poverty quartile

Late-minus-early difference in the mean change in the recovered mean since 2017, by quartile of the district economic-disadvantage share (quartile cut points 31.9, 43.6, and 53.5 percent in ELA and 32.0, 43.7, and 53.5 in mathematics), estimated from a version of the primary model in which the linear economic-disadvantage terms are replaced by quartile indicators; districts weighted equally; standard errors clustered by district. Positive values mean that grades 3–5 fell more than grades 6–8. The 2022 column is the difference in 2022 relative to 2017; the contrast is 2022 minus the mean of the 2018 and 2019 check years.

| Subject | Poverty quartile | Districts | 2022 late minus early | Contrast with check years (SE) |
|---|---|---|---|---|
| ELA | Q1 (lowest) | 123 | 0.108 | 0.109 (0.012) |
| | Q2 | 123 | 0.120 | 0.119 (0.014) |
| | Q3 | 123 | 0.105 | 0.092 (0.016) |
| | Q4 (highest) | 123 | 0.172 | 0.163 (0.014) |
| Mathematics | Q1 (lowest) | 124 | −0.105 | −0.109 (0.013) |
| | Q2 | 123 | −0.057 | −0.071 (0.017) |
| | Q3 | 123 | −0.078 | −0.111 (0.020) |
| | Q4 (highest) | 124 | −0.021 | −0.042 (0.015) |

Test of equal contrasts across quartiles: p = 0.005 (ELA) and p = 0.003 (mathematics).

## Supplementary Figure S1. Figure 1 with 2015 as the reference year

The late-minus-early difference in the association between district economic disadvantage and achievement change since 2015, by year, in the same district-contrast units as Figure 1, with 2016–2019 as check years. [File: FigA2015_eventstudy_2015]

## References cited in this supplement

Data Recognition Corporation (2015). *Technical Report for the 2015 Pennsylvania System of School Assessment.* Maple Grove, MN: DRC, for the Pennsylvania Department of Education.

Data Recognition Corporation (2026). *2025 Pennsylvania System of School Assessment Technical Report: Mathematics, English Language Arts, and Science.* Maple Grove, MN: DRC, for the Pennsylvania Department of Education.

Lipscomb, S., Chaplin, D., Vigil, A., and Matthias, H. (2022). *How the COVID-19 Pandemic Affected Academic Proficiency Rates in Pennsylvania in 2021: Findings from a Predictive Model.* Princeton, NJ: Mathematica, for the Pennsylvania Department of Education.
"""
import sys, re
# ---- reorder the supplementary tables by order of first citation in the manuscript (JY, 5 Oct):
# old S6 (PSSA changes) -> S1; old S5 (size/rounding) -> S2; old S4 (SEDA) -> S3; old S1 -> S4; old S2 -> S5; old S7 (quartiles) -> S6; old S3 (participation) -> S7
ORDER = ["S6", "S5", "S4", "S1", "S2", "S7", "S3"]
head, rest = doc.split("## Supplementary Table S1.", 1); rest = "## Supplementary Table S1." + rest
fig_i = rest.index("## Supplementary Figure S1."); tables, tail = rest[:fig_i], rest[fig_i:]
blocks = {}
for part in re.split(r"(?=## Supplementary Table S\d\.)", tables):
    if part.strip(): blocks[re.match(r"## Supplementary Table (S\d)\.", part).group(1)] = part
m = {old: f"S{i+1}" for i, old in enumerate(ORDER)}
def renum(t): return re.sub(r"\b(Table|Tables) (S[1-7])\b", lambda x: f"{x.group(1)} @@{m[x.group(2)]}", t).replace("@@", "")
doc = head + "".join(renum(blocks[k]) for k in ORDER) + renum(tail)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Supplementary_Material_v4.md"
open(OUT, "w").write(doc); print(len(doc.split()), "words written to", OUT)
