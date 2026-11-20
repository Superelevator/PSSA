"""
checks_v6_size_rounding.py -- two background checks requested by JY (2 Oct 2026):
  A. small-district influence on the primary (equal-weight) result:
     A1 district-size restrictions; A2 estimates by district-size tercile; A3 leave-one-district-out.
  B. sensitivity of the recovered means to the one-decimal rounding of the published percentages:
     B1 Monte Carlo perturbation of every published percentage within its rounding interval (+-0.05);
     B2 no continuity correction (reported proportions used directly).
  C. R^2 decomposition of the primary model (year effects only / year x band / full).
Primary model as in analysis_v5_manuscript.py (D = mu_pool[y] - mu_pool[2017]; years 2018, 2019, 2022-2025).
Writes checks_v6_results.md.
"""
import numpy as np, pandas as pd, statsmodels.api as sm, warnings, time
from scipy.stats import norm
import recover_means as rm
warnings.filterwarnings("ignore")
YEARS = [2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]; YRS = [2018, 2019, 2022, 2023, 2024, 2025]; GR = ["3", "4", "5", "6", "7", "8"]
SUBJ = ["English Language Arts", "Math"]
o = pd.read_csv("pssa_district_latent_means.csv", dtype={"grade": str})
d = pd.read_csv("pssa_district_2015_2025.csv", dtype={"grade": str})
s = pd.read_csv("pssa_state_2015_2025.csv", dtype={"grade": str})
tot = d[d.grade == "Total"].pivot_table(index=["aun", "subject", "year"], columns="group", values="n_scored", aggfunc="sum").reset_index()
ed_pre = tot[tot.year <= 2019].groupby(["aun", "subject"]).apply(lambda x: 100 * x["Economically Disadvantaged"].sum() / x["All Students"].sum()).rename("ed").reset_index()
names = d.drop_duplicates("aun").set_index("aun").district
OUT = ["# checks_v6 results: small-district influence, rounding sensitivity, R² decomposition\n"]
def P(x=""): OUT.append(x)

# ---------------------------------------------------------------- helpers (as in analysis_v5)
def wide(subject, col, src=None, group="All Students"):
    a = (o if src is None else src); a = a[(a.subject == subject) & (a.group == group) & a.year.isin(YEARS)]
    return a.pivot_table(index=["aun", "grade"], columns="year", values=col)

def stack(w, base, years, edtab, subject, need_years=None):
    need = [base] + years if need_years is None else need_years
    w = w.dropna(subset=need); ok = w.groupby(level="aun").size() == 6; w = w[w.index.get_level_values("aun").isin(ok[ok].index)]
    L = pd.concat([(w[y] - w[base]).rename("D").reset_index().assign(t=y) for y in years], ignore_index=True)
    L = L.merge(edtab[edtab.subject == subject][["aun", "ed"]], on="aun"); L["ed"] = (L.ed - L.ed.mean()) / 10
    L["late"] = (L.grade.astype(int) >= 6).astype(float); return L, w

def design(L, years, with_ed=True, with_band=True):
    X = {}
    for y in years:
        m = (L.t == y).astype(float); X[f"{y}:i"] = m
        if with_band: X[f"{y}:l"] = m * L.late
        if with_ed: X[f"{y}:e"] = m * L.ed; X[f"{y}:le"] = m * L.late * L.ed
    X = pd.DataFrame(X); return X, list(X.columns)

def fit_band(L, years, weights=None):
    X, cols = design(L, years)
    mod = sm.WLS(L.D.to_numpy(), X.to_numpy(), weights=np.ones(len(L)) if weights is None else weights).fit(cov_type="cluster", cov_kwds={"groups": L.aun.to_numpy()})
    def v(name): z = np.zeros(len(cols)); z[cols.index(name)] = 1; return z
    def est(vec): e = vec @ mod.params; se = np.sqrt(vec @ mod.cov_params() @ vec); return e, se, 2 * norm.sf(abs(e / se))
    pre = [y for y in years if y < 2020]
    d22 = est(v("2022:le")); con = est(v("2022:le") - sum(v(f"{y}:le") for y in pre) / len(pre))
    return d22, con, mod.rsquared, len(L), L.aun.nunique()

def primary(subject, src=None, keep=None):
    w = wide(subject, "mu_pool", src)
    if keep is not None: w = w[w.index.get_level_values("aun").isin(keep)]
    L, _ = stack(w, 2017, YRS, ed_pre, subject, need_years=YEARS)
    return fit_band(L, YRS), L

def fmt(r):
    (e, se, p), (ce, cse, cp), r2, n, nd = r
    return f"δ_2022 {e:+.4f} (SE {se:.4f}) | contrast {ce:+.4f} (SE {cse:.4f}, p = {cp:.2g}) | N districts {nd}"

# ---------------------------------------------------------------- A. small-district influence
P("## A. Small-district influence (primary model, equal district weights)")
# district size = median students scored per grade-year, All Students, 2015-2019, within subject
cnt = d[(d.group == "All Students") & d.grade.isin(GR) & d.year.isin([2015, 2016, 2017, 2018, 2019])]
size = cnt.groupby(["subject", "aun"]).n_scored.median().rename("size").reset_index()
minc = d[(d.group == "All Students") & d.grade.isin(GR) & d.year.isin(YEARS)].groupby(["subject", "aun"]).n_scored.min().rename("minc").reset_index()
for subject in SUBJ:
    base, L = primary(subject); keep_all = L.aun.unique()
    sz = size[size.subject == subject].set_index("aun")["size"].reindex(keep_all); mn = minc[minc.subject == subject].set_index("aun").minc.reindex(keep_all)
    P(f"\n### {subject}")
    P(f"Primary: {fmt(base)}")
    P(f"District size (median students scored per grade-year, 2015–19) among analytic districts: min {sz.min():.0f}, P10 {sz.quantile(.1):.0f}, Q1 {sz.quantile(.25):.0f}, median {sz.median():.0f}, Q3 {sz.quantile(.75):.0f}, max {sz.max():.0f}")
    P("\n**A1. Size restrictions**")
    P("| Restriction | result |"); P("|---|---|")
    for lab, keep in [("exclude districts with any grade-year cell < 30 students", mn[mn >= 30].index),
                      ("exclude districts with any grade-year cell < 50 students", mn[mn >= 50].index),
                      ("exclude districts with median cell < 50 students", sz[sz >= 50].index),
                      ("exclude districts with median cell < 100 students", sz[sz >= 100].index)]:
        P(f"| {lab} ({len(keep)} districts) | {fmt(primary(subject, keep=keep)[0])} |")
    P("\n**A2. By district-size tercile**")
    P("| Tercile (median students per grade-year) | result |"); P("|---|---|")
    ter = pd.qcut(sz, 3, labels=["small", "medium", "large"])
    for t in ["small", "medium", "large"]:
        keep = ter[ter == t].index; rng = f"{sz[keep].min():.0f}–{sz[keep].max():.0f}"
        P(f"| {t} ({rng}) | {fmt(primary(subject, keep=keep)[0])} |")
    # A3 leave-one-district-out (point estimates via OLS; jackknife SE)
    P("\n**A3. Leave-one-district-out**")
    X, cols = design(L, YRS); Xn = X.to_numpy(); y = L.D.to_numpy(); g = L.aun.to_numpy()
    i22 = cols.index("2022:le"); i18 = cols.index("2018:le"); i19 = cols.index("2019:le")
    def ols(mask):
        b = np.linalg.lstsq(Xn[mask], y[mask], rcond=None)[0]; return b[i22], b[i22] - (b[i18] + b[i19]) / 2
    full = ols(np.ones(len(y), bool)); t0 = time.time()
    loo = {a: ols(g != a) for a in keep_all}
    L22 = pd.Series({a: v[0] for a, v in loo.items()}); Lc = pd.Series({a: v[1] for a, v in loo.items()})
    n = len(keep_all); jse22 = np.sqrt((n - 1) / n * ((L22 - L22.mean()) ** 2).sum()); jsec = np.sqrt((n - 1) / n * ((Lc - Lc.mean()) ** 2).sum())
    P(f"Full-sample δ_2022 {full[0]:+.4f}, contrast {full[1]:+.4f}. Leaving out one district at a time ({n} refits, {time.time()-t0:.1f}s):")
    P(f"- δ_2022 ranges {L22.min():+.4f} to {L22.max():+.4f} (largest single-district change {np.abs(L22 - full[0]).max():.4f}); jackknife SE {jse22:.4f} vs cluster SE {base[0][1]:.4f}")
    P(f"- contrast ranges {Lc.min():+.4f} to {Lc.max():+.4f} (largest single-district change {np.abs(Lc - full[1]).max():.4f}); jackknife SE {jsec:.4f} vs cluster SE {base[1][1]:.4f}")
    P(f"- smallest contrast after any single omission = {Lc.min():+.4f}, i.e. {Lc.min() / base[1][1]:.1f} cluster SEs from zero")
    inf = (Lc - full[1]).abs().sort_values(ascending=False).head(5)
    P("- most influential districts for the contrast (omitting the district changes it by): " + "; ".join(
        f"{names[a]} ({'+' if (Lc[a]-full[1])>0 else '−'}{abs(Lc[a]-full[1]):.4f}; size {sz[a]:.0f}; ED {ed_pre[(ed_pre.subject==subject)&(ed_pre.aun==a)].ed.iloc[0]:.0f}%)" for a in inf.index))

# ---------------------------------------------------------------- B. rounding sensitivity
P("\n## B. Sensitivity to one-decimal rounding of the published percentages")
LV = rm.LEVELS
def score(dd, ss, cc=True, rng=None, jitter=0.0):
    """re-run the scoring pipeline for All Students, ELA + Math; optional jitter (uniform +-jitter) on every
    published level percentage (district and statewide) and optional removal of the continuity correction."""
    dd = dd[(dd.grade != "Total") & dd.pct_prof_above.notna() & (dd.group == "All Students") & dd.subject.isin(SUBJ)].copy()
    ss = ss[(ss.year == rm.ANCHOR) & (ss.group == "All Students") & (ss.grade != "Total") & ss.subject.isin(SUBJ)].copy()
    if jitter > 0:
        for df in (dd, ss):
            v = df[LV].to_numpy(dtype=float) + rng.uniform(-jitter, jitter, size=(len(df), 4)); df[LV] = np.clip(v, 0, None)
    out, cqs = [], []
    for (sub, gq), r in ss.groupby(["subject", "grade"]):
        cuts = norm.ppf(rm.cum_shares(r)[0]); cell = dd[(dd.subject == sub) & (dd.grade == gq)].copy()
        if cc:
            mu, sd, muh, flag, prec, cq = rm.fit_cells(cell, cuts)
        else:
            nn = cell["n_scored"].to_numpy().astype(float); p = rm.cum_shares(cell)
            p = np.clip(p, 0.5 / nn[:, None], 1 - 0.5 / nn[:, None])            # only empty bins are moved
            q = norm.ppf(p); w = nn[:, None] * norm.pdf(q) ** 2 / (p * (1 - p)); c = np.broadcast_to(cuts, q.shape)
            W = w.sum(1); cm = (w * c).sum(1) / W; qm = (w * q).sum(1) / W
            b = (w * (c - cm[:, None]) * (q - qm[:, None])).sum(1) / (w * (c - cm[:, None]) ** 2).sum(1); a = qm - b * cm
            flag = ~(b > 0.2) | (b > 5)
            with np.errstate(divide="ignore", invalid="ignore"):
                sd = np.where(flag, np.nan, 1.0 / b); mu = np.where(flag, np.nan, -a / b)
            prec = (w * (c - cm[:, None]) ** 2).sum(1); cq = (c, q, w)
        cell["mu_het"], cell["sd_het"], cell["unstable"], cell["prec_b"] = mu, sd, flag, prec
        out.append(cell); cqs.append(cq)
    res = []
    for sub in SUBJ:
        idx = [i for i, c in enumerate(out) if c.subject.iloc[0] == sub]
        big = pd.concat([out[i] for i in idx], ignore_index=True); cq = tuple(np.concatenate([cqs[i][k] for i in idx]) for k in range(3))
        big["mu_pool"], big["sd_pool"] = rm.pooled_sigma_means(big, cq); res.append(big)
    out = pd.concat(res)
    base = out[out.year == rm.ANCHOR]
    off = base.groupby(["subject", "grade"]).apply(lambda x: np.average(x.mu_pool.dropna(), weights=x.loc[x.mu_pool.notna(), "n_scored"])).rename("off")
    out = out.merge(off, on=["subject", "grade"], how="left"); out["mu_pool"] = out.mu_pool - out.off
    return out

chk = score(d, s)   # reproduction check against the file used by the manuscript
for subject in SUBJ:
    a = o[(o.subject == subject) & (o.group == "All Students")].set_index(["aun", "grade", "year"]).mu_pool
    b = chk[chk.subject == subject].set_index(["aun", "grade", "year"]).mu_pool
    P(f"- reproduction check, {subject}: max |mu_pool(rebuilt) − mu_pool(file)| = {(a - b).abs().max():.2e}")
P("\n**B2. No continuity correction** (reported proportions used directly; only empty bins moved to 0.5/n)")
nc = score(d, s, cc=False)
for subject in SUBJ:
    P(f"- {subject}: {fmt(primary(subject, src=nc)[0])}")
P("\n**B1. Monte Carlo: every published percentage (district and statewide anchor) perturbed by U(−0.05, +0.05) percentage points, 30 draws**")
rng = np.random.default_rng(20261002); draws = {sub: [] for sub in SUBJ}
for r_ in range(30):
    sc = score(d, s, rng=rng, jitter=0.05)
    for subject in SUBJ:
        (e, se, p), (ce, cse, cp), *_ = primary(subject, src=sc)[0]; draws[subject].append((e, ce, cp))
for subject in SUBJ:
    a = np.array(draws[subject])
    P(f"- {subject}: δ_2022 mean {a[:,0].mean():+.4f}, range {a[:,0].min():+.4f} to {a[:,0].max():+.4f}, SD across draws {a[:,0].std():.5f}; "
      f"contrast mean {a[:,1].mean():+.4f}, range {a[:,1].min():+.4f} to {a[:,1].max():+.4f}; contrast p range {a[:,2].min():.2g} to {a[:,2].max():.2g}")
# how big is the rounding error in student terms?
nn = d[(d.group == "All Students") & d.grade.isin(GR) & d.year.isin(YEARS) & d.subject.isin(SUBJ)].n_scored
P(f"- for scale: ±0.05 percentage points is ±{0.0005 * nn.median():.2f} students at the median cell (n = {nn.median():.0f}) and ±{0.0005 * nn.quantile(.1):.2f} at the 10th percentile (n = {nn.quantile(.1):.0f}); the continuity correction moves each cumulative count by 0.5 student")

# ---------------------------------------------------------------- C. R² decomposition
P("\n## C. R² of the primary model and of nested versions")
P("| Subject | year effects only | year × band | year × band × poverty (primary) |"); P("|---|---|---|---|")
for subject in SUBJ:
    _, L = primary(subject); y = L.D.to_numpy(); r = []
    for we, wb in [(False, False), (False, True), (True, True)]:
        X, _ = design(L, YRS, with_ed=we, with_band=wb); r.append(sm.OLS(y, X.to_numpy()).fit().rsquared)
    P(f"| {subject} | {r[0]:.3f} | {r[1]:.3f} | {r[2]:.3f} |")
    sd_by_year = L.groupby("t").D.std().round(3).to_dict()
    P(f"  SD of district-grade changes since 2017 by year ({subject}): {sd_by_year}")

open("checks_v6_results.md", "w").write("\n".join(OUT)); print("\n".join(OUT))
