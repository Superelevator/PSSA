"""
recover_means.py -- recover a latent mean (and SD) for every district x subject x grade x
year x group cell from PDE's four performance-level shares.

Method (Ho & Reardon 2012; Reardon, Shear, Castellano & Ho 2017 -- the approach SEDA uses):
  * Within each subject x grade, the three cut scores are the same for every district and
    every year (PSSA is equated across years with fixed cut scores).  We place the cuts on a
    scale where the ANCHOR-year (2017) STATEWIDE distribution of students has mean 0 and SD 1:
        c_k = Phi^-1(statewide cumulative share below cut k, anchor year).
  * For a cell with cumulative shares p_k below cut k, if the cell's achievement is
    Normal(mu, sigma):  Phi^-1(p_k) = (c_k - mu) / sigma.
    The three points (c_k, Phi^-1(p_k)) lie on a line with slope 1/sigma and intercept
    -mu/sigma; we fit it by weighted least squares (weights = binomial precision of each
    probit-transformed share), giving mu_het (heteroskedastic fit).  A homoskedastic
    version (sigma fixed at 1) gives mu_hom = mean_k(c_k - Phi^-1(p_k)) as a robustness check.
  * Shares are rounded to 0.1% in the source, so counts are approximated as n * share and a
    (x + 0.5) / (n + 1) continuity correction keeps boundary shares finite.
Units: anchor-year (2017) statewide student SD within subject x grade.  mu = -0.20 means the cell's mean
lies 0.20 SD below the anchor-year statewide mean for that subject and grade.
Usage: python3 recover_means.py   (reads pssa_district_2015_2025.csv, pssa_state_2015_2025.csv;
       writes pssa_district_latent_means.csv)
"""
import numpy as np, pandas as pd
from scipy.stats import norm

ANCHOR = 2017   # statewide distribution of this year defines mean 0 / SD 1 for each subject-grade

LEVELS = ["pct_below_basic", "pct_basic", "pct_proficient", "pct_advanced"]  # low -> high

def cum_shares(df):
    """cumulative share BELOW each of the three cuts, from the four level shares (%)."""
    s = df[LEVELS].to_numpy() / 100.0
    s = s / s.sum(axis=1, keepdims=True)              # remove 0.1-rounding drift
    return np.cumsum(s, axis=1)[:, :3]

def fit_cells(d, cuts):
    """d: rows of one subject x grade; cuts: (3,) array. Returns mu_het, sd_het, mu_hom, flag."""
    n = d["n_scored"].to_numpy().astype(float)
    p = cum_shares(d)
    cnt = p * n[:, None]
    p = (cnt + 0.5) / (n[:, None] + 1.0)               # continuity correction
    q = norm.ppf(p)                                    # Phi^-1(p_k)
    w = n[:, None] * norm.pdf(q) ** 2 / (p * (1 - p))  # binomial precision of q_k
    c = np.broadcast_to(cuts, q.shape)
    # WLS of q on c: q = a + b*c,  b = 1/sigma, a = -mu/sigma
    W = w.sum(1); cm = (w * c).sum(1) / W; qm = (w * q).sum(1) / W
    b = (w * (c - cm[:, None]) * (q - qm[:, None])).sum(1) / (w * (c - cm[:, None]) ** 2).sum(1)
    a = qm - b * cm
    mu_hom = ((c - q) * w).sum(1) / W                  # sigma = 1, precision-weighted
    flag = ~(b > 0.2) | (b > 5)                        # sd > 5 or < 0.2 statewide SD (or NaN): unstable
    with np.errstate(divide="ignore", invalid="ignore"):
        sd_het = np.where(flag, np.nan, 1.0 / b)
        mu_het = np.where(flag, np.nan, -a / b)
    prec_b = (w * (c - cm[:, None]) ** 2).sum(1)       # WLS precision of the slope
    return mu_het, sd_het, mu_hom, flag, prec_b, (c, q, w)

def pooled_sigma_means(cell, cq):
    """mu_pool: sigma pooled within district x subject x group across all grades and years
    (precision-weighted mean of log sd_het), then mu = weighted mean_k (c_k - sigma_d * q_k).
    Reduces the noise in sigma from cells with nearly empty top bins (Reardon et al. 2017
    recommend partial pooling of SDs for small cells)."""
    c, q, w = cq
    ok = cell.sd_het.notna()
    ls = np.log(cell.sd_het.where(ok))
    pw = cell.prec_b.where(ok, 0.0)
    key = [cell.aun.values, cell.group.values]
    num = pd.Series(ls * pw).groupby(key).transform("sum")
    den = pd.Series(pw).groupby(key).transform("sum")
    sig_d = np.exp(num / den).fillna(1.0).to_numpy()   # districts with no usable cell: sigma = 1
    W = w.sum(1)
    mu_pool = ((c - sig_d[:, None] * q) * w).sum(1) / W
    return mu_pool, sig_d

def main():
    d = pd.read_csv("pssa_district_2015_2025.csv", dtype={"grade": str})
    s = pd.read_csv("pssa_state_2015_2025.csv", dtype={"grade": str})
    d = d[(d.grade != "Total") & d.pct_prof_above.notna()].copy()
    ref = s[(s.year == ANCHOR) & (s.group == "All Students") & (s.grade != "Total")]
    out, cqs = [], []
    for (sub, g), r in ref.groupby(["subject", "grade"]):
        cuts = norm.ppf(cum_shares(r)[0])               # anchor-year statewide -> N(0,1)
        cell = d[(d.subject == sub) & (d.grade == g)].copy()
        if cell.empty:
            continue
        mu, sd, muh, flag, prec, cq = fit_cells(cell, cuts)
        cell["cut_basic"], cell["cut_prof"], cell["cut_adv"] = cuts
        cell["mu_het"], cell["sd_het"], cell["mu_hom"], cell["unstable"], cell["prec_b"] = mu, sd, muh, flag, prec
        out.append(cell); cqs.append(cq)
    # pooled-sigma means need all grades and years of a district together: recompute per subject
    res = []
    for sub in sorted({c.subject.iloc[0] for c in out}):
        idx = [i for i, c in enumerate(out) if c.subject.iloc[0] == sub]
        big = pd.concat([out[i] for i in idx], ignore_index=True)
        cq = tuple(np.concatenate([cqs[i][k] for i in idx]) for k in range(3))
        big["mu_pool"], big["sd_pool"] = pooled_sigma_means(big, cq)
        res.append(big)
    out = pd.concat(res).sort_values(["subject", "grade", "year", "aun", "group"])
    # re-center so the anchor-year statewide student-weighted mean is exactly 0 in each subject-grade
    # (the raw anchor leaves a small constant offset because the statewide distribution is a
    # mixture of district normals); a constant shift changes no difference or slope.
    base = out[(out.year == ANCHOR) & (out.group == "All Students")]
    for col in ["mu_het", "mu_hom", "mu_pool"]:
        off = base.groupby(["subject", "grade"]).apply(
            lambda x: np.average(x[col].dropna(), weights=x.loc[x[col].notna(), "n_scored"])).rename("off")
        out = out.merge(off, on=["subject", "grade"], how="left")
        out[col] = out[col] - out["off"]; out = out.drop(columns="off")
    out.to_csv("pssa_district_latent_means.csv", index=False)
    # statewide reproduction check: student-weighted mean of district mu in the anchor year should be ~0
    chk = out[(out.year == ANCHOR) & (out.group == "All Students")]
    wm = chk.groupby(["subject", "grade"]).apply(lambda x: np.average(x.mu_het, weights=x.n_scored))
    print(f"{ANCHOR} student-weighted mean of district mu_het by subject-grade (should be near 0):")
    print(wm.round(3).unstack().to_string())
    print("corr(mu_pool, mu_het) = %.4f | corr(mu_pool, mu_hom) = %.4f | median sd_pool = %.2f (IQR %.2f-%.2f)" % (
        out[["mu_pool", "mu_het"]].corr().iloc[0, 1], out[["mu_pool", "mu_hom"]].corr().iloc[0, 1], out.sd_pool.median(), *out.sd_pool.quantile([.25, .75])))
    print("\ncells:", len(out), "| unstable:", int(out.unstable.sum()),
          "| corr(mu_het, mu_hom) = %.4f" % out[["mu_het", "mu_hom"]].corr().iloc[0, 1],
          "| median sd_het = %.2f (IQR %.2f-%.2f)" % (out.sd_het.median(), *out.sd_het.quantile([.25, .75])))
    print("corr(mu_het, pct_prof_above) within anchor-year All Students: %.3f | corr(mu_hom, pct_prof_above): %.3f" % (chk[["mu_het", "pct_prof_above"]].corr().iloc[0, 1], chk[["mu_hom", "pct_prof_above"]].corr().iloc[0, 1]))
    u = out[out.unstable]; print("unstable cells by group/n:", u.group.value_counts().to_dict(), "| n_scored median %.0f" % u.n_scored.median())

if __name__ == "__main__":
    main()
