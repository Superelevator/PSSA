"""figures_v5.py -- figures for the revised manuscript (November 2026).
Figure 1 (new): statewide recovered mean achievement relative to 2017, by grade band and year (the values in Table 1).
Figure 2: the former Figure 1 (late-minus-early difference in the poverty gradient of the change, by year), unchanged.
Figure 3: the former Figure 2 (grade-specific associations, 2019 and 2022), unchanged.
Figure S1: Figure 2 with 2015 as the reference year, unchanged.
Reads pssa_district_latent_means.csv, pssa_district_2015_2025.csv and pssa_state_2015_2025.csv from the working directory.
Writes Figure_1/2/3 as .png (600 dpi), .pdf, .tif (LZW) and .jpg, and Figure_S1.png."""
import numpy as np, pandas as pd, statsmodels.api as sm, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import norm
from PIL import Image
warnings.filterwarnings("ignore")
BLUE, ORANGE, DARK, GRAY = "#2a78d6", "#eb6834", "#104281", "#7a7975"
INK, INK2, GRID, AXIS = "#0b0b0b", "#52514e", "#f0efec", "#b5b4ae"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.edgecolor": AXIS, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titleweight": "bold", "axes.titlesize": 10,
                     "legend.frameon": False, "figure.dpi": 150})
YEARS = [2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]
SUBJECTS = ["English Language Arts", "Math"]
def title(s): return ("(A) " if s != "Math" else "(B) ") + ("Mathematics" if s == "Math" else s)

def save(fig, name):
    fig.savefig(name + ".png", dpi=600, bbox_inches="tight"); fig.savefig(name + ".pdf", bbox_inches="tight"); plt.close(fig)
    im = Image.open(name + ".png").convert("RGB")
    im.save(name + ".tif", compression="tiff_lzw", dpi=(600, 600)); im.save(name + ".jpg", quality=95, dpi=(600, 600))
    print(f"{name}: {im.size[0]} x {im.size[1]} px = {im.size[0] / 600 * 25.4:.0f} x {im.size[1] / 600 * 25.4:.0f} mm at 600 dpi")

# ------------------------------------------------------------------ Figure 1: statewide means (Table 1)
s = pd.read_csv("pssa_state_2015_2025.csv", dtype={"grade": str})
LV = ["pct_below_basic", "pct_basic", "pct_proficient", "pct_advanced"]
a = s[(s.group == "All Students") & (s.grade != "Total") & s.subject.isin(SUBJECTS) & s.year.isin(YEARS)].dropna(subset=LV)
def shares(r):
    v = r[LV].to_numpy(dtype=float); return np.cumsum(v / v.sum())[:3]
rows = []
for (sub, g), grp in a.groupby(["subject", "grade"]):
    cuts = norm.ppf(shares(grp[grp.year == 2017].iloc[0]))
    for _, r in grp.iterrows():
        q = norm.ppf(np.clip(shares(r), 1e-4, 1 - 1e-4)); b = np.polyfit(cuts, q, 1); rows.append((sub, int(g), int(r.year), -b[1] / b[0]))
st = pd.DataFrame(rows, columns=["subject", "grade", "year", "mu"])
print("Statewide recovered mean relative to 2017 (Table 1):")
for sub in SUBJECTS: print(sub); print(st[st.subject == sub].pivot(index="year", columns="grade", values="mu").round(2).to_string())

xpos, x = {}, 0
for y in YEARS:
    if y == 2022: x += 1
    xpos[y] = x; x += 1
PRE, POST = [y for y in YEARS if y < 2020], [y for y in YEARS if y > 2020]
fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.3), sharey=True)
for ax, sub in zip(axes, SUBJECTS):
    t = st[st.subject == sub].pivot(index="year", columns="grade", values="mu")
    ax.axhline(0, color=AXIS, lw=1, zorder=1); g = xpos[2019] + 1
    ax.axvspan(g - 0.4, g + 0.4, color=GRID, zorder=0)
    ax.text(g, 0.165, "no test\n2020;\n2021\nexcluded", ha="center", va="top", fontsize=8, color=INK2)
    for grades, col, lab in [((3, 4, 5), BLUE, "Grades 3–5"), ((6, 7, 8), ORANGE, "Grades 6–8")]:
        for seg in (PRE, POST):
            xs = [xpos[y] for y in seg]
            for gr in grades: ax.plot(xs, t.loc[seg, gr], color=col, lw=0.8, alpha=0.45, zorder=2)
            m = t.loc[seg, list(grades)].mean(axis=1)
            ax.plot(xs, m, color=col, lw=2, marker="o", ms=4.5, mec="white", mew=0.8, zorder=3, label=lab if seg is PRE else None)
        end = t.loc[2025, list(grades)].mean()
        ax.text(xpos[2025] + 0.3, end, lab.replace("Grades ", ""), ha="left", va="center", fontsize=8, color=INK)
    ax.set_xticks(list(xpos.values())); ax.set_xticklabels([str(y) for y in YEARS], rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim(-0.5, xpos[2025] + 1.3); ax.set_ylim(-0.44, 0.17); ax.set_title(title(sub), loc="left")
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True); ax.spines["right"].set_visible(False)
axes[0].set_ylabel("Statewide mean achievement\nrelative to 2017 (SD units)")
h, l = axes[0].get_legend_handles_labels()
h.append(plt.Line2D([], [], color=GRAY, lw=0.8, alpha=0.7)); l.append("individual grades")
axes[0].legend(h, l, loc="lower left", fontsize=8, handlelength=2.2)
fig.tight_layout(); save(fig, "Figure_1")

# ------------------------------------------------------------------ Figures 2, 3 and S1: as in figures_v4.py
o = pd.read_csv("pssa_district_latent_means.csv", dtype={"grade": str})
d = pd.read_csv("pssa_district_2015_2025.csv", dtype={"grade": str})
tt = d[(d.grade == "Total") & (d.year <= 2019)].pivot_table(index=["aun", "subject"], columns="group", values="n_scored", aggfunc="sum")
ED = (100 * tt["Economically Disadvantaged"] / tt["All Students"]).rename("ed").reset_index()

def panel(subject):
    aa = o[(o.subject == subject) & (o.group == "All Students") & o.year.isin(YEARS)]
    w = aa.pivot_table(index=["aun", "grade"], columns="year", values="mu_pool").dropna()
    ok = w.groupby(level="aun").size() == 6; w = w[w.index.get_level_values("aun").isin(ok[ok].index)].reset_index()
    w = w.merge(ED[ED.subject == subject][["aun", "ed"]], on="aun")
    q25, q75 = w.drop_duplicates("aun").ed.quantile([.25, .75]); iqr10 = (q75 - q25) / 10
    w["ed"] = (w.ed - w.ed.mean()) / 10; w["late"] = (w.grade.astype(int) >= 6).astype(float)
    return w, (q25, q75, iqr10)

def event_study(w, base, yrs):
    L = pd.concat([w[["aun", "grade", "ed", "late"]].assign(t=y, D=w[y] - w[base]) for y in yrs], ignore_index=True)
    X = {}
    for y in yrs:
        m = (L.t == y).astype(float)
        X[f"{y}:i"] = m; X[f"{y}:l"] = m * L.late; X[f"{y}:e"] = m * L.ed; X[f"{y}:le"] = m * L.late * L.ed
    X = pd.DataFrame(X); mod = sm.OLS(L.D.to_numpy(), X.to_numpy()).fit(cov_type="cluster", cov_kwds={"groups": L.aun.to_numpy()})
    cols = list(X.columns); est, se = {}, {}
    for y in yrs:
        i = cols.index(f"{y}:le"); est[y] = mod.params[i]; se[y] = np.sqrt(mod.cov_params()[i, i])
    return est, se

W = {sub: panel(sub) for sub in SUBJECTS}

def fig_A(base, yrs, ylim):
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.3), sharey=True)
    allyears = [base] + yrs; xp, x = {}, 0
    for y in allyears:
        if y == 2022: x += 1
        xp[y] = x; x += 1
    for ax, sub in zip(axes, SUBJECTS):
        w, (q25, q75, k) = W[sub]; est, se = event_study(w, base, yrs)
        ax.axhline(0, color=AXIS, lw=1, zorder=1); g = xp[2019] + 1
        ax.axvspan(g - 0.4, g + 0.4, color=GRID, zorder=0)
        ax.text(g, ylim[0] + 0.004, "no test\n2020;\n2021\nexcluded", ha="center", va="bottom", fontsize=8, color=INK2)
        ax.plot([xp[base]], [0], marker="D", ms=5, color=GRAY, zorder=3); ax.text(xp[base], -0.012, "ref.", ha="center", va="top", fontsize=8, color=INK2)
        xs = [xp[y] for y in yrs]; ys = [est[y] * k for y in yrs]; ci = [1.96 * se[y] * k for y in yrs]
        pre = [i for i, y in enumerate(yrs) if y < 2020]; post = [i for i, y in enumerate(yrs) if y > 2020]
        ax.plot([xs[i] for i in pre], [ys[i] for i in pre], color=BLUE, lw=1.5, alpha=0.6); ax.plot([xs[i] for i in post], [ys[i] for i in post], color=BLUE, lw=1.5, alpha=0.6)
        ax.errorbar(xs, ys, yerr=ci, fmt="o", ms=5, color=BLUE, ecolor=BLUE, elinewidth=1.2, capsize=2.5, zorder=3)
        v = est[2022] * k
        ax.annotate(f"+{v:.3f} SD", (xp[2022], v + 1.96 * se[2022] * k), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8.5, color=INK)
        ax.set_xticks(list(xp.values())); ax.set_xticklabels([str(y) for y in allyears]); ax.set_title(title(sub), loc="left"); ax.set_ylim(*ylim)
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True); ax.spines["right"].set_visible(False)
    axes[0].set_ylabel("Extra decline in grades 3–5 relative to grades 6–8,\nhigh- vs low-poverty district (SD units)")
    fig.tight_layout(); return fig

save(fig_A(2017, [2018, 2019, 2022, 2023, 2024, 2025], (-0.05, 0.08)), "Figure_2")
f = fig_A(2015, [2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025], (-0.06, 0.12))
f.savefig("Figure_S1.png", dpi=600, bbox_inches="tight"); plt.close(f)

fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.3), sharey=True); gx = np.arange(3, 9)
for ax, sub in zip(axes, SUBJECTS):
    w, (q25, q75, k) = W[sub]
    ax.axhline(0, color=AXIS, lw=1, zorder=1); ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True); ax.spines["right"].set_visible(False)
    for j, (y, col, ls, lab) in enumerate([(2019, GRAY, "--", "2019 vs 2017 (pre-pandemic check year)"), (2022, DARK, "-", "2022 vs 2017")]):
        b, e = [], []
        for g in gx:
            xx = w[w.grade == str(g)]; m = sm.OLS((xx[y] - xx[2017]).to_numpy(), sm.add_constant(xx.ed.to_numpy())).fit(cov_type="HC1")
            b.append(m.params[1] * k); e.append(1.96 * m.bse[1] * k)
        ax.errorbar(gx + (j - 0.5) * 0.12, b, yerr=e, fmt="o", ms=4.5, color=col, ecolor=col, elinewidth=1, capsize=2, ls=ls, lw=1.5, label=lab, zorder=3)
    ax.axvspan(2.6, 5.5, color=GRID, zorder=0); ax.text(4.05, 0.075, "grades 3–5", ha="center", fontsize=8, color=INK2); ax.text(7.0, 0.075, "grades 6–8", ha="center", fontsize=8, color=INK2)
    ax.set_xticks(gx); ax.set_xlabel("Grade"); ax.set_title(title(sub), loc="left"); ax.set_ylim(-0.10, 0.085)
axes[0].set_ylabel("Change since 2017, high- vs low-poverty\ndistrict (SD units)")
axes[0].legend(loc="lower left", fontsize=8)
fig.tight_layout(); save(fig, "Figure_3")
q25, q75, k = W["English Language Arts"][1]; print(f"ED share quartiles: 25th {q25:.1f}%, 75th {q75:.1f}% -> scale factor {k:.2f}")
