"""
analysis_v5_manuscript.py -- every number the revised manuscript reports, in one run.
Outputs analysis_v5_results.md.
Primary design: D = mu[y] - mu[2017]; years 2018, 2019, 2022-2025; early(3-5)/late(6-8) x poverty by year;
poverty = pre-2020 ED share per +10 pts, centered; cluster SE by district; equal district weights.
"""
import numpy as np, pandas as pd, statsmodels.api as sm, warnings
from scipy.stats import norm
import recover_means as rm
warnings.filterwarnings("ignore")
YEARS = [2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]; YRS = [2018, 2019, 2022, 2023, 2024, 2025]
PRE = [2018, 2019]; GR = ["3", "4", "5", "6", "7", "8"]
o = pd.read_csv("pssa_district_latent_means.csv", dtype={"grade": str})
d = pd.read_csv("pssa_district_2015_2025.csv", dtype={"grade": str})
s = pd.read_csv("pssa_state_2015_2025.csv", dtype={"grade": str})
tot = d[d.grade == "Total"].pivot_table(index=["aun", "subject", "year"], columns="group", values="n_scored", aggfunc="sum").reset_index()
ed_pre = tot[tot.year <= 2019].groupby(["aun", "subject"]).apply(lambda x: 100 * x["Economically Disadvantaged"].sum() / x["All Students"].sum()).rename("ed").reset_index()
OUT = ["# analysis_v5 results (all manuscript numbers)\n"]
def P(x=""): OUT.append(x)

# ------------------------------------------------------------------ helpers
def wide(subject, col, src=None, group="All Students"):
    a = (o if src is None else src); a = a[(a.subject == subject) & (a.group == group) & a.year.isin(YEARS)]
    return a.pivot_table(index=["aun", "grade"], columns="year", values=col)

def stack(w, base, years, edtab, subject, need_years=None):
    need = [base] + years if need_years is None else need_years
    w = w.dropna(subset=need); ok = w.groupby(level="aun").size() == 6; w = w[w.index.get_level_values("aun").isin(ok[ok].index)]
    L = pd.concat([(w[y] - w[base]).rename("D").reset_index().assign(t=y) for y in years], ignore_index=True)
    if edtab is not None:
        L = L.merge(edtab[edtab.subject == subject][["aun", "ed"]], on="aun"); L["ed"] = (L.ed - L.ed.mean()) / 10
    L["late"] = (L.grade.astype(int) >= 6).astype(float); return L, w

def fit_band(L, years, with_ed=True, weights=None):
    X = {}
    for y in years:
        m = (L.t == y).astype(float); X[f"{y}:i"] = m; X[f"{y}:l"] = m * L.late
        if with_ed: X[f"{y}:e"] = m * L.ed; X[f"{y}:le"] = m * L.late * L.ed
    X = pd.DataFrame(X); cols = list(X.columns)
    mod = sm.WLS(L.D.to_numpy(), X.to_numpy(), weights=np.ones(len(L)) if weights is None else weights).fit(cov_type="cluster", cov_kwds={"groups": L.aun.to_numpy()})
    def v(name): z = np.zeros(len(cols)); z[cols.index(name)] = 1; return z
    def est(vec): e = vec @ mod.params; se = np.sqrt(vec @ mod.cov_params() @ vec); return e, se, 2 * norm.sf(abs(e / se))
    key = "le" if with_ed else "l"
    pre = [y for y in years if y < 2020]
    rows = {y: dict(zip(["est", "se", "p"], est(v(f"{y}:{key}")))) for y in years}
    if with_ed:
        for y in years:
            rows[y]["early"] = est(v(f"{y}:e")); rows[y]["late"] = est(v(f"{y}:e") + v(f"{y}:le"))
    else:
        for y in years:
            rows[y]["early"] = est(v(f"{y}:i")); rows[y]["late"] = est(v(f"{y}:i") + v(f"{y}:l"))
    R = np.array([v(f"{y}:{key}") for y in pre]); placebo = mod.wald_test(R, scalar=True).pvalue
    R3 = np.array([v(f"{years[0]}:{key}") - v(f"{y}:{key}") for y in years[1:]]); three = mod.wald_test(R3, scalar=True).pvalue
    con = est(v(f"2022:{key}") - sum(v(f"{y}:{key}") for y in pre) / len(pre))
    return rows, placebo, three, con, mod.rsquared, len(L), L.aun.nunique()

def ci(e, se): return f"{e:+.4f} [{e - 1.96 * se:+.4f}, {e + 1.96 * se:+.4f}]"

# ------------------------------------------------------------------ A. descriptives
P("## A. Descriptives")
for subject in ["English Language Arts", "Math"]:
    w = wide(subject, "mu_pool"); full = w.dropna(subset=YEARS); ok = full.groupby(level="aun").size() == 6
    keep = ok[ok].index; excluded = sorted(set(w.index.get_level_values("aun")) - set(keep))
    e = ed_pre[ed_pre.subject == subject].set_index("aun").ed.reindex(keep)
    P(f"- {subject}: districts in file {w.index.get_level_values('aun').nunique()}; analytic sample {len(keep)}; excluded {len(excluded)} (AUNs {excluded}) for missing cells in some year/grade")
    P(f"  ED share (pre-2020 pooled) among analytic districts: mean {e.mean():.1f}, SD {e.std():.1f}, min {e.min():.1f}, Q1 {e.quantile(.25):.1f}, median {e.median():.1f}, Q3 {e.quantile(.75):.1f}, max {e.max():.1f}")
n = d[(d.group == "All Students") & (d.grade != "Total") & d.subject.isin(["English Language Arts", "Math"]) & (d.year != 2021)]
P(f"- students scored per district-grade-year (All Students, ELA+Math, excl. 2021): median {n.n_scored.median():.0f}, IQR {n.n_scored.quantile(.25):.0f}-{n.n_scored.quantile(.75):.0f}, min {n.n_scored.min()}")
sup = d[(d.grade != "Total") & d.subject.isin(["English Language Arts", "Math"]) & (d.year != 2021)]
P(f"- suppressed cells (percentages blank, n<=10): All Students {int(sup[sup.group=='All Students'].pct_prof_above.isna().sum())}, ED {int(sup[sup.group=='Economically Disadvantaged'].pct_prof_above.isna().sum())} of {int((sup.group=='All Students').sum())} each")
# statewide latent means vs 2019
L_ = ["pct_below_basic", "pct_basic", "pct_proficient", "pct_advanced"]
a = s[(s.group == "All Students") & (s.grade != "Total") & s.subject.isin(["English Language Arts", "Math"])].dropna(subset=L_)
def shares(r): v = r[L_].to_numpy(dtype=float); return np.cumsum(v / v.sum())[:3]
rows = []
for (sub, g), grp in a.groupby(["subject", "grade"]):
    cuts = norm.ppf(shares(grp[grp.year == rm.ANCHOR].iloc[0]))
    for _, r in grp.iterrows():
        q = norm.ppf(np.clip(shares(r), 1e-4, 1 - 1e-4)); b = np.polyfit(cuts, q, 1); rows.append((sub, g, int(r.year), -b[1] / b[0]))
st = pd.DataFrame(rows, columns=["subject", "grade", "year", "mu"])
P(f"\nStatewide recovered mean relative to {rm.ANCHOR} (SD units), All Students:")
for sub in ["English Language Arts", "Math"]:
    P(f"\n{sub}\n" + st[st.subject == sub].pivot(index="year", columns="grade", values="mu").round(2).to_markdown())
# equal-district mean of mu_pool by year (analytic sample) and by ED quartile x band, 2022 vs 2017
P("\nEqual-district mean recovered score by year (analytic sample), and 2022-2017 change by ED quartile and band:")
for subject in ["English Language Arts", "Math"]:
    w = wide(subject, "mu_pool").dropna(subset=YEARS); ok = w.groupby(level="aun").size() == 6; w = w[w.index.get_level_values("aun").isin(ok[ok].index)]
    P(f"\n{subject}: " + ", ".join(f"{y}: {w[y].mean():+.3f}" for y in YEARS))
    x = w.reset_index().merge(ed_pre[ed_pre.subject == subject][["aun", "ed"]], on="aun"); x["q"] = pd.qcut(x.ed, 4, labels=["Q1 low", "Q2", "Q3", "Q4 high"]); x["band"] = np.where(x.grade.astype(int) <= 5, "early", "late")
    x["d22"] = x[2022] - x[2017]; x["d19"] = x[2019] - x[2017]
    P(x.groupby(["q", "band"], observed=True)[["d19", "d22"]].mean().round(3).unstack("band").to_markdown())

# ------------------------------------------------------------------ B. primary model
P("\n## B. Primary model (All Students; D = mu_pool[y] - mu_pool[2017])")
primary = {}
for subject in ["English Language Arts", "Math"]:
    L, w = stack(wide(subject, "mu_pool"), 2017, YRS, ed_pre, subject, need_years=YEARS)
    rows, placebo, three, con, r2, nobs, nd = fit_band(L, YRS); primary[subject] = (rows, placebo, three, con, r2, nobs, nd, L)
    P(f"\n### {subject}: N districts {nd}, district-grade-year obs {nobs}, R² {r2:.3f}")
    P("| year vs 2017 | poverty slope, grades 3-5 [95% CI] | poverty slope, grades 6-8 [95% CI] | late minus early [95% CI] | p |"); P("|---|---|---|---|---|")
    for y in YRS:
        r = rows[y]; P(f"| {y} | {ci(*r['early'][:2])} | {ci(*r['late'][:2])} | {ci(r['est'], r['se'])} | {r['p']:.2g} |")
    P(f"joint placebo test (2018 = 2019 = 0): p = {placebo:.2g}; test that late-minus-early is constant across the six years: p = {three:.2g}; 2022 minus mean(2018, 2019): {ci(con[0], con[1])}, p = {con[2]:.2g}")
    k = (ed_pre[ed_pre.subject == subject].set_index('aun').ed.reindex(L.aun.unique()).quantile(.75) - ed_pre[ed_pre.subject == subject].set_index('aun').ed.reindex(L.aun.unique()).quantile(.25)) / 10
    P(f"IQR scaling (75th minus 25th percentile of ED share)/10 = {k:.2f}; 2022 late-minus-early for that contrast = {rows[2022]['est'] * k:+.3f} SD")

# grade-specific slopes vs 2017 (HC1), all years
P("\n### Grade-specific poverty slopes of the change vs 2017 (SD per +10 pts ED; HC1 SE)")
for subject in ["English Language Arts", "Math"]:
    L, w = stack(wide(subject, "mu_pool"), 2017, YRS, ed_pre, subject, need_years=YEARS)
    P(f"\n{subject}\n| year | " + " | ".join(f"g{g}" for g in GR) + " |"); P("|---" * 7 + "|")
    for y in YRS:
        cells = []
        for g in GR:
            x = L[(L.t == y) & (L.grade == g)]; m = sm.OLS(x.D.to_numpy(), sm.add_constant(x.ed.to_numpy())).fit(cov_type="HC1"); cells.append(f"{m.params[1]:+.3f} ({m.bse[1]:.3f})")
        P(f"| {y} | " + " | ".join(cells) + " |")
    # cohort re-expression
    P(f"\n{subject} — same slopes arranged by cohort (grade in spring 2020 = grade - (year - 2020)); rows = cohort, columns = year")
    tab = {}
    for y in [2022, 2023, 2024, 2025]:
        for g in GR:
            x = L[(L.t == y) & (L.grade == g)]; m = sm.OLS(x.D.to_numpy(), sm.add_constant(x.ed.to_numpy())).fit(cov_type="HC1")
            tab.setdefault(int(g) - (y - 2020), {})[y] = f"{m.params[1]:+.3f} (g{g})"
    P(pd.DataFrame(tab).T.sort_index().fillna("").to_markdown())

# ------------------------------------------------------------------ C. participation
P("\n## C. Participation (tested counts)")
cnt = d[(d.group == "All Students") & (d.grade != "Total") & d.subject.isin(["English Language Arts", "Math"])].pivot_table(index=["aun", "subject", "grade"], columns="year", values="n_scored")
for subject in ["English Language Arts", "Math"]:
    c = cnt.xs(subject, level="subject").copy(); c = c.reset_index().merge(ed_pre[ed_pre.subject == subject][["aun", "ed"]], on="aun")
    c["q"] = pd.qcut(c.ed, 4, labels=["Q1 low", "Q2", "Q3", "Q4 high"]); c["band"] = np.where(c.grade.astype(int) <= 5, "early", "late")
    for y in [2019, 2022, 2023, 2024]: c[f"r{y}"] = c[y] / c[2017]
    P(f"\n{subject}: median tested-count ratio vs 2017 by ED quartile and band\n" + c.groupby(["q", "band"], observed=True)[["r2019", "r2022", "r2023", "r2024"]].median().round(3).to_markdown())
    # sensitivity: 2022 primary estimate on cells with 2022/2017 ratio within 0.95-1.05
    L, w = stack(wide(subject, "mu_pool"), 2017, YRS, ed_pre, subject, need_years=YEARS)
    L = L.merge(c[["aun", "grade", "r2022"]], on=["aun", "grade"])
    sub22 = L[(L.t == 2022)]; keep = sub22[(sub22.r2022 >= 0.95) & (sub22.r2022 <= 1.05)]
    def one(x):
        X = pd.DataFrame({"i": 1.0, "l": x.late, "e": x.ed, "le": x.late * x.ed}); m = sm.OLS(x.D.to_numpy(), X.to_numpy()).fit(cov_type="cluster", cov_kwds={"groups": x.aun.to_numpy()}); return m.params[3], m.bse[3]
    a1, a2 = one(sub22), one(keep)
    rho = sub22.groupby(pd.qcut(sub22.ed, 4, labels=False)).apply(lambda x: np.corrcoef(x.r2022, x.D)[0, 1]).round(3).tolist()
    P(f"2022 late-minus-early: all cells {a1[0]:+.4f} ({a1[1]:.4f}, n={len(sub22)}); cells with 2022 count within 5% of 2017 {a2[0]:+.4f} ({a2[1]:.4f}, n={len(keep)}); corr(count ratio, change) within ED quartiles: {rho}")

# ------------------------------------------------------------------ D. robustness
P("\n## D. Robustness of the 2022 late-minus-early estimate and its contrast with the pre-years")
P("| variant | ELA 2022 (SE) | ELA 2022 - pre (p) | Math 2022 (SE) | Math 2022 - pre (p) |"); P("|---|---|---|---|---|")
nsc = d[(d.group == "All Students") & (d.grade != "Total") & d.year.isin(YEARS)].groupby(["aun", "subject", "grade"]).n_scored.mean().rename("nbar").reset_index()   # student weights: mean number scored over the nine analysis years
ed17 = tot[tot.year == 2017].assign(ed=lambda x: 100 * x["Economically Disadvantaged"] / x["All Students"])[["aun", "subject", "ed"]]
def variant(subject, col="mu_pool", edtab=None, base=2017, years=None, weights=False, drop7=False):
    edtab = ed_pre if edtab is None else edtab; years = YRS if years is None else years
    L, w = stack(wide(subject, col), base, years, edtab, subject, need_years=YEARS)
    if drop7: L = L[L.grade != "7"]
    wts = None
    if weights: L = L.merge(nsc[nsc.subject == subject][["aun", "grade", "nbar"]], on=["aun", "grade"]); wts = L.nbar.to_numpy()
    rows, placebo, three, con, r2, nobs, nd = fit_band(L, years, weights=wts); return rows[2022], con
for lab, kw in [("primary", {}), ("fixed SD (mu_hom)", {"col": "mu_hom"}), ("cell-specific SD (mu_het)", {"col": "mu_het"}), ("ED share measured in 2017", {"edtab": ed17}),
                ("student-weighted", {"weights": True}), ("excluding grade 7", {"drop7": True}), ("baseline 2015 (pre 2016-19)", {"base": 2015, "years": [2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]})]:
    cells = []
    for subject in ["English Language Arts", "Math"]:
        r, con = variant(subject, **kw); cells += [f"{r['est']:+.4f} ({r['se']:.4f})", f"{con[0]:+.4f} ({con[2]:.2g})"]
    P(f"| {lab} | " + " | ".join(cells) + " |")
open("analysis_v5_results.md", "w").write("\n".join(OUT)); print("\n".join(OUT))
