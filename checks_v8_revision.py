"""
checks_v8_revision.py -- analyses added in the November 2026 revision. Writes checks_v8_results.md.
A. Table 4: change in recovered mean achievement from the 2018-2019 average to 2022, by district poverty quartile
   and grade band (cell means, standard errors clustered by district), the late-minus-early difference, and a test
   that the difference is equal across quartiles. The difference column reproduces the contrast column of the former
   Supplementary Table S6 (checks_v7_quartiles_sample.py).
B. Section 4.4: the primary contrast after each grade's change is divided by the average annual achievement gain for
   that grade reported by Bloom et al. (2008) from nationally normed tests (reading: seven tests; mathematics: six),
   which expresses change in years of typical learning. Also reported with one gain per grade band and with the
   grade 3 gain replaced by the mean of the grade 4 and grade 5 gains.
Same analytic sample, poverty measure, equal district weights and district-clustered standard errors as
analysis_v5_manuscript.py. Run from the folder that holds the two district CSV files.
"""
import warnings
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import norm
warnings.filterwarnings("ignore")

YEARS = [2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]
o = pd.read_csv("pssa_district_latent_means.csv", dtype={"grade": str})
d = pd.read_csv("pssa_district_2015_2025.csv", dtype={"grade": str})
tot = d[d.grade == "Total"].pivot_table(index=["aun", "subject", "year"], columns="group", values="n_scored", aggfunc="sum").reset_index()
ed_pre = tot[tot.year <= 2019].groupby(["aun", "subject"]).apply(
    lambda x: 100 * x["Economically Disadvantaged"].sum() / x["All Students"].sum()).rename("ed").reset_index()
OUT = ["# checks_v8 results: analyses added in the revision\n"]
def P(x=""): OUT.append(x)

def prep(subject):
    a = o[(o.subject == subject) & (o.group == "All Students") & o.year.isin(YEARS)]
    w = a.pivot_table(index=["aun", "grade"], columns="year", values="mu_pool").dropna(subset=YEARS)
    ok = w.groupby(level="aun").size() == 6
    w = w[w.index.get_level_values("aun").isin(ok[ok].index)]
    L = w.reset_index().melt(id_vars=["aun", "grade"], value_vars=YEARS, var_name="t", value_name="mu")
    L["t"] = L.t.astype(int)
    L = L.merge(ed_pre[ed_pre.subject == subject][["aun", "ed"]], on="aun")
    L["ed_raw"] = L.ed
    L["ed"] = (L.ed - L.ed.mean()) / 10
    L["g"] = L.grade.astype(int)
    L["late"] = (L.g >= 6).astype(float)
    return L

def fit(y, X, groups):
    X = pd.DataFrame(X); cols = list(X.columns)
    mod = sm.OLS(np.asarray(y), X.to_numpy()).fit(cov_type="cluster", cov_kwds={"groups": np.asarray(groups)})
    V = mod.cov_params()
    def vec(name):
        z = np.zeros(len(cols)); z[cols.index(name)] = 1; return z
    def est(v):
        e = v @ mod.params; se = np.sqrt(v @ V @ v); return e, se, 2 * norm.sf(abs(e / se))
    return mod, vec, est

# ------------------------------------------------------------------ A. Table 4
P("## A. Table 4: change from the 2018-2019 average to 2022 by poverty quartile and grade band (SD units)\n")
P("| Subject | Poverty quartile | ED share (%) | Districts | Grades 3-5 (SE) | Grades 6-8 (SE) | Late minus early (SE) |")
P("|---|---|---|---|---|---|---|")
QS = ["Q1", "Q2", "Q3", "Q4"]
for subject in ["English Language Arts", "Math"]:
    L = prep(subject)
    edd = L.drop_duplicates("aun").set_index("aun").ed_raw
    q = pd.qcut(edd, 4, labels=QS); L["q"] = L.aun.map(q)
    X = {}
    for y in YEARS:
        m = (L.t == y).astype(float)
        for k in QS:
            qk = (L.q == k).astype(float) * m; X[f"{y}:e:{k}"] = qk * (1 - L.late); X[f"{y}:l:{k}"] = qk * L.late
    mod, vec, est = fit(L.mu, X, L.aun)
    def con(band, k): return vec(f"2022:{band}:{k}") - (vec(f"2018:{band}:{k}") + vec(f"2019:{band}:{k}")) / 2
    for k in QS:
        e, l, dd = est(con("e", k)), est(con("l", k)), est(con("l", k) - con("e", k))
        rng = edd[q == k]
        P(f"| {subject if k == 'Q1' else ''} | {k} | {rng.min():.1f}-{rng.max():.1f} (mean {rng.mean():.1f}) | {int((q == k).sum())} | {e[0]:+.3f} ({e[1]:.3f}) | {l[0]:+.3f} ({l[1]:.3f}) | {dd[0]:+.3f} ({dd[1]:.3f}) |")
    R = np.array([(con("l", "Q1") - con("e", "Q1")) - (con("l", k) - con("e", k)) for k in QS[1:]])
    Re = np.array([con("e", "Q1") - con("e", k) for k in QS[1:]]); Rl = np.array([con("l", "Q1") - con("l", k) for k in QS[1:]])
    P(f"\n{subject}: test of equal late-minus-early differences across quartiles p = {float(mod.wald_test(R, scalar=True).pvalue):.3f}; "
      f"equal grades 3-5 changes p = {float(mod.wald_test(Re, scalar=True).pvalue):.3g}; equal grades 6-8 changes p = {float(mod.wald_test(Rl, scalar=True).pvalue):.3g}\n")

# ------------------------------------------------------------------ B. Bloom et al. (2008) conversion
READ = {3: 0.60, 4: 0.36, 5: 0.40, 6: 0.32, 7: 0.23, 8: 0.26}   # annual gain during the tested grade, SD units (reading)
MATH = {3: 0.89, 4: 0.52, 5: 0.56, 6: 0.41, 7: 0.30, 8: 0.32}   # (mathematics)
P("## B. Primary contrast (2022 minus the mean of 2018 and 2019) in SD units and in years of typical learning\n")
P("Per 10 percentage points of economically disadvantaged students; estimate (SE) [95% CI]; ratio = grades 3-5 association divided by grades 6-8 association.\n")
P("| Subject | Outcome units | Grades 3-5 | Grades 6-8 | Late minus early | Ratio |")
P("|---|---|---|---|---|---|")
def f(t): return f"{t[0]:+.4f} ({t[1]:.4f}) [{t[0] - 1.96 * t[1]:+.4f}, {t[0] + 1.96 * t[1]:+.4f}]"
for subject, gain in [("English Language Arts", READ), ("Math", MATH)]:
    L = prep(subject)
    def bandmap(gm):
        eb = np.mean([gm[g] for g in (3, 4, 5)]); lb = np.mean([gm[g] for g in (6, 7, 8)]); return {3: eb, 4: eb, 5: eb, 6: lb, 7: lb, 8: lb}
    g3 = dict(gain); g3[3] = (gain[4] + gain[5]) / 2
    variants = [("SD units (submitted analysis)", None),
                ("years of learning, grade-specific gains", gain),
                ("years of learning, one gain per band", bandmap(gain)),
                ("years of learning, grade-specific gains, grade 3 gain set to the grade 4-5 mean", g3),
                ("years of learning, one gain per band, grade 3 gain set to the grade 4-5 mean", bandmap(g3))]
    for label, gm in variants:
        y = L.mu if gm is None else L.mu / L.g.map(gm)
        X = {}
        for yr in YEARS:
            m = (L.t == yr).astype(float)
            X[f"{yr}:i"] = m; X[f"{yr}:l"] = m * L.late; X[f"{yr}:e"] = m * L.ed; X[f"{yr}:le"] = m * L.late * L.ed
        mod, vec, est = fit(y, X, L.aun)
        def c(name): return vec(f"2022:{name}") - (vec(f"2018:{name}") + vec(f"2019:{name}")) / 2
        early, late, diff = est(c("e")), est(c("e") + c("le")), est(c("le"))
        P(f"| {subject} | {label} | {f(early)} | {f(late)} | {f(diff)} (p = {diff[2]:.2g}) | {early[0] / late[0]:.1f} |")
# ------------------------------------------------------------------ C. Gradient of achievement itself (levels), for scale
P("\n## C. Association between district economic disadvantage and mean achievement itself (levels), by grade band\n")
P("Per 10 percentage points of economically disadvantaged students; SD units; estimate (SE).\n")
P("| Subject | Year | Grades 3-5 | Grades 6-8 |"); P("|---|---|---|---|")
for subject in ["English Language Arts", "Math"]:
    L = prep(subject)
    for yr in [2017, 2022]:
        x = L[L.t == yr]
        mod, vec, est = fit(x.mu, {"i": np.ones(len(x)), "l": x.late.to_numpy(), "e": x.ed.to_numpy(), "le": (x.late * x.ed).to_numpy()}, x.aun)
        e, l = est(vec("e")), est(vec("e") + vec("le"))
        P(f"| {subject} | {yr} | {e[0]:+.3f} ({e[1]:.3f}) | {l[0]:+.3f} ({l[1]:.3f}) |")
open("checks_v8_results.md", "w").write("\n".join(OUT) + "\n"); print("\n".join(OUT))
