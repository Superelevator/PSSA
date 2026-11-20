"""revise_supplement.py -- revised supplement (November 2026) from Supplementary_Material_v4.md (the output of
build_supplement.py). Table S6 (poverty quartiles) moved to the main text as Table 4 and the district-size part of
Table S2 moved into Table 3, so both are removed here; the rest of Table S2 (the two district-size restrictions that
are not in Table 3, the leave-one-district-out check, the rounding check and the continuity-correction row) becomes
Supplementary Note S1; the remaining tables are renumbered S1-S5; figure references follow the new numbering of the
main text.
Usage: python3 revise_supplement.py   (reads Supplementary_Material_v4.md, writes Supplementary_Material_v7.md)"""
import re
s = open("Supplementary_Material_v4.md").read()
def block(start, end):
    i = s.index(start); j = s.index(end, i); return i, j
i, j = block("## Supplementary Table S2.", "## Supplementary Table S3.")
s2 = s[i:j]
loo = s2[s2.index("Leave-one-district-out:"): s2.index("Rounding:")].strip()
rnd = s2[s2.index("Rounding:"):].strip()
_a = "within its rounding interval of ±0.05 percentage points"; assert rnd.count(_a) == 1
rnd = rnd.replace(_a, _a + ", the four shares then renormalized to sum to 100,")
def cells(label):
    """Estimates (value, SE or p) and district counts from one row of the former Table S2."""
    line = next(l for l in s2.split("\n") if l.startswith("| " + label))
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    return [re.fullmatch(r"(\S+) \((.+)\)", x).groups() for x in c[1:5]], [x.strip() for x in c[5].split("/")]
def left(n): return f"{n[0]} districts in each subject" if n[0] == n[1] else f"{n[0]} districts in ELA and {n[1]} in mathematics"
a, na = cells("Exclude districts with median cell below 50 students")
b, nb = cells("Exclude districts with median cell below 100 students")
size = ("District size: excluding districts whose size, the median number of students scored per grade-year over 2015–2019 as in Table 3, "
        f"is below 50 students (leaving {left(na)}), δ_2022 is {a[0][0]} (SE {a[0][1]}) in ELA and {a[2][0]} ({a[2][1]}) in mathematics, "
        f"and the contrast with the check years is {a[1][0]} (p = {a[1][1]}) and {a[3][0]} (p = {a[3][1]}). "
        f"With a threshold of 100 students (leaving {left(nb)}), δ_2022 is {b[0][0]} ({b[0][1]}) and {b[2][0]} ({b[2][1]}), "
        f"and the contrast is {b[1][0]} (p = {b[1][1]}) and {b[3][0]} (p = {b[3][1]}).")
s = s[:i] + s[j:]
i, j = block("## Supplementary Table S6.", "## Supplementary Table S7.")
s = s[:i] + s[j:]
m = {"S3": "S2", "S4": "S3", "S5": "S4", "S7": "S5"}
s = re.sub(r"\bTable (S[3457])\b", lambda x: "Table @@" + m[x.group(1)], s).replace("@@", "")
for a, b in [("The 2019 and 2022 rows are plotted in Figure 2.", "The 2019 and 2022 rows are plotted in Figure 3."),
             ("## Supplementary Figure S1. Figure 1 with 2015 as the reference year", "## Supplementary Figure S1. Figure 2 with 2015 as the reference year"),
             ("in the same district-contrast units as Figure 1, with 2016–2019 as check years.", "in the same district-contrast units as Figure 2, with 2016–2019 as check years."),
             ("Level correlations are between our recovered mean", "Single-year correlations are between our recovered mean"),
             ("r, level (median)", "r, single year (median)"), ("r, level (min–max)", "r, single year (min–max)"), ("r, ED level", "r, ED group"),
             ("[File: FigA2015_eventstudy_2015]", "[File: Figure_S1]")]:
    assert s.count(a) == 1, a; s = s.replace(a, b)
note = ("## Supplementary Note S1. Leave-one-district-out, district-size, and rounding checks\n\n" + loo + "\n\n" + size + "\n\n" + rnd + "\n\n"
        "Continuity correction: without the continuity correction in the scoring step, δ_2022 is 0.016 (SE 0.004) in both subjects and the contrast with the check years is 0.012 (p = 0.001 in ELA and 0.0008 in mathematics).\n\n")
i = s.index("## Supplementary Figure S1."); s = s[:i] + note + s[i:]
open("Supplementary_Material_v7.md", "w").write(s); print(len(s.split()), "words written to Supplementary_Material_v7.md")
