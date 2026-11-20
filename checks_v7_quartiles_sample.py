"""
checks_v7_quartiles_sample.py -- the grade-band difference by district poverty quartile (Supplementary Table S6):
a version of the primary model in which the linear economic-disadvantage terms are replaced by quartile indicators
(quartile x band x year means with standard errors clustered by district), the 2022 late-minus-early difference,
its contrast with the check years (2022 minus the mean of 2018 and 2019), and a test of equal contrasts across quartiles.
Reuses the data loading and model helpers at the top of checks_v6_size_rounding.py. Writes checks_v7_results.md.
"""
import numpy as np, pandas as pd, statsmodels.api as sm, warnings
warnings.filterwarnings("ignore")
exec(open("checks_v6_size_rounding.py").read().split("# ---------------------------------------------------------------- A. small-district")[0])
OUT = ["# checks_v7 results: the grade-band difference by district poverty quartile\n"]
def P(x=""): OUT.append(x)

def quartile_contrasts(L, qcol="q"):
    """late-minus-early difference in mean change, by quartile: 2022 level and 2022 minus mean(2018, 2019); cluster SE."""
    X = {}
    for y in YRS:
        m = (L.t == y).astype(float)
        for k in ["Q1", "Q2", "Q3", "Q4"]:
            qk = (L[qcol] == k).astype(float) * m; X[f"{y}:i:{k}"] = qk; X[f"{y}:l:{k}"] = qk * L.late
    X = pd.DataFrame(X); cols = list(X.columns)
    mod = sm.OLS(L.D.to_numpy(), X.to_numpy()).fit(cov_type="cluster", cov_kwds={"groups": L.aun.to_numpy()})
    def v(n): z = np.zeros(len(cols)); z[cols.index(n)] = 1; return z
    res = {}
    for k in ["Q1", "Q2", "Q3", "Q4"]:
        c = v(f"2022:l:{k}") - (v(f"2018:l:{k}") + v(f"2019:l:{k}")) / 2
        e = c @ mod.params; se = np.sqrt(c @ mod.cov_params() @ c)
        res[k] = (mod.params[cols.index(f"2022:l:{k}")], e, se, int(L[L[qcol] == k].aun.nunique()))
    # test of equal contrasts across quartiles
    R = np.array([(v("2022:l:Q1") - (v("2018:l:Q1") + v("2019:l:Q1")) / 2) - (v(f"2022:l:{k}") - (v(f"2018:l:{k}") + v(f"2019:l:{k}")) / 2) for k in ["Q2", "Q3", "Q4"]])
    return res, mod.wald_test(R, scalar=True).pvalue

for subject in SUBJ:
    P(f"\n## {subject}")
    base, L = primary(subject); allaun = set(L.aun.unique())
    ed = ed_pre[ed_pre.subject == subject].set_index("aun").ed
    q = pd.qcut(ed.reindex(sorted(allaun)), 4, labels=["Q1", "Q2", "Q3", "Q4"])
    cuts = ed.reindex(sorted(allaun)).quantile([.25, .5, .75]).round(1).tolist()
    P(f"ED-share quartile cut points among analytic districts: {cuts}")
    P(f"Primary model, all analytic districts: {fmt(base)}")
    L["q"] = L.aun.map(q)
    full, pfull = quartile_contrasts(L)
    P(f"\nLate-minus-early difference by poverty quartile (2022 level; contrast = 2022 minus mean of 2018 and 2019; SE clustered by district)")
    P("| Quartile | n districts | 2022 late minus early | contrast with check years (SE) |")
    P("|---|---|---|---|")
    for k in ["Q1", "Q2", "Q3", "Q4"]:
        P(f"| {k} | {full[k][3]} | {full[k][0]:+.3f} | {full[k][1]:+.3f} ({full[k][2]:.3f}) |")
    P(f"Equality of contrasts across quartiles: p = {pfull:.3f}")

open("checks_v7_results.md", "w").write("\n".join(OUT)); print("\n".join(OUT))
