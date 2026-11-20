"""
build_dataset.py -- harmonize the raw PDE PSSA files (Raw_PDE/) into two clean CSVs.

  python3 build_dataset.py district   -> pssa_district_2015_2025.csv
  python3 build_dataset.py state      -> pssa_state_2015_2025.csv

District file: All Students + Economically Disadvantaged, all subjects, grades 3-8 and
district Total, years 2015-2019 and 2021-2025 (2020: no test). Four performance levels
kept as reported by PDE (percentages); suppressed cells (n <= 10) keep Number Scored and
have blank percentages, exactly as in the source. No values are altered.
State file: all reporting groups, same columns minus aun/county/district.
"""
import sys, glob, os, re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "Raw_PDE")

RENAME = {
    "Year": "year", "AUN": "aun", "County": "county", "District Name": "district",
    "Subject": "subject", "Group": "group", "Grade": "grade", "Number Scored": "n_scored",
    "Percent Advanced": "pct_advanced", "Percent Proficient": "pct_proficient",
    "Percent Basic": "pct_basic", "Percent Below Basic": "pct_below_basic",
    "Percent Proficient and above": "pct_prof_above",
    # state files use other spellings in some years
    "% Advanced": "pct_advanced", "% Proficient": "pct_proficient", "% Basic": "pct_basic",
    "% Below Basic": "pct_below_basic", "% Advanced/Proficient": "pct_prof_above",
    "% Proficient and above": "pct_prof_above", "Percent Advanced/Proficient": "pct_prof_above",
}
COLS = ["year", "aun", "county", "district", "subject", "group", "grade", "n_scored",
        "pct_advanced", "pct_proficient", "pct_basic", "pct_below_basic", "pct_prof_above"]
GROUP_FIX = {  # 2024 file spells two groups differently
    "American Indian/Alaskan Native (not Hispanic)": "American Indian / Alaskan Native (not Hispanic)",
    "Native Hawaiian or other Pacific Islander": "Native Hawaiian or other Pacific Islander (not Hispanic)",
}

def read_pde(path, key_col):
    """Read one PDE file; the header row is the first row containing key_col."""
    x = pd.ExcelFile(path)
    raw = x.parse(x.sheet_names[0], header=None, nrows=12)
    hdr = next(i for i in range(12)
               if raw.iloc[i].astype(str).str.strip().str.fullmatch(key_col, case=False).any())
    d = x.parse(x.sheet_names[0], header=hdr)
    d.columns = [str(c).strip().lower() for c in d.columns]      # spellings vary by year
    d = d.rename(columns={k.lower(): v for k, v in RENAME.items()})
    src_year = int(re.search(r"(20\d\d)", os.path.basename(path)).group(1))
    if "year" not in d.columns:            # some state files omit the Year column
        d["year"] = src_year
    if "pct_prof_above" not in d.columns:  # derive when the file lacks the combined column
        d["pct_prof_above"] = pd.to_numeric(d["pct_advanced"], errors="coerce") + pd.to_numeric(d["pct_proficient"], errors="coerce")
    d = d[[c for c in COLS if c in d.columns]]
    d["year"] = pd.to_numeric(d["year"], errors="coerce").astype("Int64")
    d = d.dropna(subset=["year", "subject", "grade"])
    d["grade"] = (d["grade"].astype(str).str.strip().str.replace(r"^Grade\s*", "", regex=True)
                  .replace({"District Total": "Total", "State Total": "Total"}))
    num = d["grade"].str.fullmatch(r"\d+(\.0)?")          # '03', '3.0' -> '3'
    d.loc[num, "grade"] = d.loc[num, "grade"].astype(float).astype(int).astype(str)
    d["group"] = d["group"].astype(str).str.strip().replace(GROUP_FIX)
    d["subject"] = d["subject"].astype(str).str.strip()
    for c in ["n_scored", "pct_advanced", "pct_proficient", "pct_basic", "pct_below_basic", "pct_prof_above"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    bad = (d["year"] != src_year).sum()
    if bad:
        print(f"  WARNING {os.path.basename(path)}: {bad} rows whose Year != {src_year}")
    return d

def build(level):
    pat = "*district*.xlsx" if level == "district" else "*state*.xlsx"
    files = sorted(glob.glob(os.path.join(RAW, pat)))
    key = "AUN" if level == "district" else "Subject"
    parts = []
    for f in files:
        d = read_pde(f, key)
        print(f"  {os.path.basename(f)}: {len(d)} rows, years {sorted(d.year.unique().tolist())}")
        parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    if level == "district":
        d["aun"] = d["aun"].astype("int64")
        d = d[d["group"].isin(["All Students", "Economically Disadvantaged"])]
        keys = ["year", "aun", "subject", "group", "grade"]
    else:
        keys = ["year", "subject", "group", "grade"]
    dups = d.duplicated(keys).sum()
    assert dups == 0, f"{dups} duplicate keys"
    d = d.sort_values(keys).reset_index(drop=True)
    out = os.path.join(HERE, f"pssa_{level}_2015_2025.csv")
    d.to_csv(out, index=False)
    print(f"wrote {out}: {len(d)} rows, {d.year.nunique()} years, groups={d.group.nunique()}, subjects={sorted(d.subject.unique())}")
    return d

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "district")
