"""validate_seda.py -- compare our recovered latent means with SEDA 2025.2 (Pennsylvania rows,
grade-cohort scale 'gcs') for the same district x subject x grade x year cells.
Districts are matched by normalized name (PDE files carry AUN, SEDA carries NCES LEA ids).
Also writes seda_validation_by_year.csv (Supplementary Table S4)."""
import re, numpy as np, pandas as pd
o = pd.read_csv("pssa_district_latent_means.csv", dtype={"grade": str})
o["pct_prof_above"] = o.pct_proficient + o.pct_advanced
o = o[(o.group == "All Students") & o.subject.isin(["English Language Arts", "Math"]) & (o.grade != "Total")].copy()
o["subject"] = o.subject.map({"English Language Arts": "rla", "Math": "mth"}); o["grade"] = o.grade.astype(int)
s = pd.read_csv("../SEDA/seda_PA_admindist_long_gcs_2025.2.csv",
                usecols=["sedaadmin", "sedaadminname", "subject", "grade", "year", "tot_asmt_all", "gcs_mn_all", "gcs_mn_se_all", "gcs_mn_ecd"])
def norm(x):
    x = re.sub(r"[^A-Z0-9 ]", " ", str(x).upper()); x = re.sub(r"\bSCHOOL DISTRICT\b", "SD", x)
    return re.sub(r"\s+", " ", x).strip()
pde = o[["aun", "district"]].drop_duplicates(); pde["key"] = pde.district.map(norm)
sed = s[["sedaadmin", "sedaadminname"]].drop_duplicates(); sed["key"] = sed.sedaadminname.map(norm)
sed = sed[~sed.key.str.endswith(" CS")]                                  # charters are not in the PDE district file
xw = pde.merge(sed, on="key", how="inner")
dup = xw.key.duplicated(keep=False); xw = xw[~dup]
print(f"name match: {xw.aun.nunique()} of {pde.aun.nunique()} PDE districts matched to SEDA (dropped {dup.sum()//2} ambiguous names)")
m = o.merge(xw[["aun", "sedaadmin"]], on="aun").merge(s, on=["sedaadmin", "subject", "grade", "year"], how="inner")
m = m.dropna(subset=["gcs_mn_all", "mu_pool"])
print("matched cells:", len(m), "| by year:", m.groupby("year").size().to_dict())
def corr_by(df, a, b, keys): return df.groupby(keys).apply(lambda x: x[[a, b]].corr().iloc[0, 1] if len(x) > 30 else np.nan)
print("\nLEVELS: within subject-grade-year correlation with SEDA gcs_mn_all (median over subject-grades, by year)")
rows = {}
for col in ["mu_pool", "mu_het", "mu_hom", "pct_prof_above"]:
    r = corr_by(m, col, "gcs_mn_all", ["subject", "grade", "year"]).rename("r").reset_index()
    rows[col] = r.groupby("year").r.median().round(3)
lev = pd.DataFrame(rows); print(lev.to_string())
# min/max across subject-grades too (for the supplement)
r = corr_by(m, "mu_pool", "gcs_mn_all", ["subject", "grade", "year"]).rename("r").reset_index()
rng = r.groupby("year").r.agg(["min", "max"]).round(3)
print("\nscale: SEDA gcs units per 1 SD of ours (slope of gcs on mu_pool within subject-grade-year), median by year:")
sl = m.groupby(["subject", "grade", "year"]).apply(lambda x: np.polyfit(x.mu_pool, x.gcs_mn_all, 1)[0] if len(x) > 30 else np.nan)
print(sl.groupby(level="year").median().round(2).to_dict())
print("\nCHANGES 2019 -> post year: correlation of district-grade changes (ours vs SEDA), median over subject-grades")
w = m.pivot_table(index=["aun", "subject", "grade"], columns="year", values=["mu_pool", "mu_hom", "pct_prof_above", "gcs_mn_all"])
out = {}
for y in [2022, 2023, 2024, 2025]:
    d = pd.DataFrame({c: w[(c, y)] - w[(c, 2019)] for c in ["mu_pool", "mu_hom", "pct_prof_above", "gcs_mn_all"]}).dropna().reset_index()
    out[y] = {c: corr_by(d, c, "gcs_mn_all", ["subject", "grade"]).median().round(3) for c in ["mu_pool", "mu_hom", "pct_prof_above"]}
    out[y]["n_cells"] = len(d)
chg = pd.DataFrame(out); print(chg.to_string())
print("\nED subgroup levels: our ED-group mu_pool vs SEDA gcs_mn_ecd, median r by year")
oe = pd.read_csv("pssa_district_latent_means.csv", dtype={"grade": str})
oe = oe[(oe.group == "Economically Disadvantaged") & oe.subject.isin(["English Language Arts", "Math"]) & (oe.grade != "Total")].copy()
oe["subject"] = oe.subject.map({"English Language Arts": "rla", "Math": "mth"}); oe["grade"] = oe.grade.astype(int)
me = oe.merge(xw[["aun", "sedaadmin"]], on="aun").merge(s, on=["sedaadmin", "subject", "grade", "year"]).dropna(subset=["gcs_mn_ecd", "mu_pool"])
ed = corr_by(me, "mu_pool", "gcs_mn_ecd", ["subject", "grade", "year"]).groupby(level="year").median().round(3)
print(ed.to_dict())
# S4 table
cov = m.groupby("year").size(); tot = o[o.year.isin(cov.index)].groupby("year").size()
S4 = pd.DataFrame({"cells matched": cov, "share of PDE cells (%)": (100 * cov / tot).round(0),
                   "r, recovered mean (median)": lev["mu_pool"], "r, recovered mean (min–max)": rng["min"].astype(str) + "–" + rng["max"].astype(str),
                   "r, percent proficient or above": lev["pct_prof_above"], "r, ED-group recovered mean": ed,
                   "r, change since 2019 (recovered mean)": chg.loc["mu_pool"].reindex(cov.index), "r, change since 2019 (percent proficient)": chg.loc["pct_prof_above"].reindex(cov.index)})
S4.to_csv("seda_validation_by_year.csv"); print("\n" + S4.to_markdown())
