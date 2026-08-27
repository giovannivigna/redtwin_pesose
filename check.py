#!/usr/bin/env python3
"""NSF 26-506 (PESOSE) Track 3 + PAPPG 24-1 compliance check for main.pdf.

Run:  make check      (or)   python3 check.py
Requires: pdfinfo, pdftotext, mutool.
"""
import subprocess, re, sys

PDF = "main.pdf"
LIMIT_PD, LIMIT_SUMMARY = 15, 1
ok = True

def run(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout

def report(label, passed, detail=""):
    global ok
    ok = ok and passed
    print(f"[{'PASS' if passed else 'FAIL'}] {label}" + (f"  -- {detail}" if detail else ""))

n = int(run("pdfinfo", PDF).split("Pages:")[1].split()[0])
# Locate the section boundaries rather than assuming a one-page summary.
pdstart = ref = None
for p in range(1, n + 1):
    t = run("pdftotext", "-f", str(p), "-l", str(p), PDF, "-").strip()
    if pdstart is None and t.startswith("Project Description"):
        pdstart = p
    if t.startswith("References"):
        ref = p
        break
if pdstart is None or ref is None:
    print("could not locate the Project Description / References boundaries"); sys.exit(1)

summary = pdstart - 1
pd = ref - pdstart
report(f"Project Summary <= {LIMIT_SUMMARY} page", summary <= LIMIT_SUMMARY,
       f"{summary} page(s) (pp. 1-{pdstart-1})")
report(f"Project Description <= {LIMIT_PD} pages", pd <= LIMIT_PD,
       f"{pd} pages (pp. {pdstart}-{ref-1})")

# Margins (>= 1 in on all sides). ~2pt of glyph overhang from microtype is normal.
worst = [999.0] * 4
for p in range(1, n + 1):
    b = [tuple(map(float, m)) for m in
         re.findall(r'<line bbox="([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)"', run("mutool", "draw", "-F", "stext", "-o", "-", PDF, str(p)))]
    if not b:
        continue
    worst = [min(worst[0], min(x[0] for x in b)), min(worst[1], 612 - max(x[2] for x in b)),
             min(worst[2], min(x[1] for x in b)), min(worst[3], 792 - max(x[3] for x in b))]
report("Margins >= 1 in (2pt glyph overhang tolerated)", min(worst) >= 69.0,
       "L%.0f R%.0f T%.0f B%.0f pt" % tuple(worst))

# No URLs in the Project Description (PAPPG II.D.2.d(ii)).
pdtext = run("pdftotext", "-f", str(pdstart), "-l", str(ref - 1), PDF, "-")
urls = re.findall(r"https?://\S+", pdtext)
report("No URLs in Project Description", not urls, "; ".join(urls[:3]))

# Project Summary keywords: 2-5, on the last line.
kw = re.search(r"Keywords:(.*)", run("pdftotext", "-f", "1", "-l", "1", PDF, "-"))
count = len([k for k in kw.group(1).split(";") if k.strip()]) if kw else 0
report("Project Summary has 2-5 keywords", kw is not None and 2 <= count <= 5, f"{count} keywords")

# Body font >= 11pt for Times.
sizes = {}
for p in range(pdstart, ref):
    for s in re.findall(r'size="([\d.]+)"', run("mutool", "draw", "-F", "stext", "-o", "-", PDF, str(p))):
        s = round(float(s), 1); sizes[s] = sizes.get(s, 0) + 1
body = max(sizes, key=sizes.get)
report("Body font >= 11 pt (Times)", body >= 10.9, f"{body} pt")

# No proposer-supplied page numbers (Research.gov stamps its own).
last = run("pdftotext", "-f", str(ref - 1), "-l", str(ref - 1), PDF, "-").strip().split("\n")[-1].strip()
report("No proposer-supplied page numbers", not last.isdigit(), f"last line: {last[:40]!r}")

# Line spacing: PAPPG II.C.2.b allows at most six lines of text per vertical inch.
from collections import Counter
o = run("mutool", "draw", "-F", "stext", "-o", "-", PDF, "5")
ys = sorted(set(round(float(m), 1) for m in re.findall(r'<line bbox="[\d.-]+ ([\d.-]+)', o)))
diffs = [round(ys[i + 1] - ys[i], 2) for i in range(len(ys) - 1)]
pitch = Counter(x for x in diffs if 5 < x < 25).most_common(1)[0][0]
report("Line spacing <= 6 lines/inch", 72 / pitch <= 6.0, f"{72/pitch:.2f} lines/inch")

# Track 3 required sections.
for name in ["The Target Open-Source Ecosystem", "Societal, National, and Economic Impact",
             "Targeted Vulnerabilities and Risks", "Build and Test Infrastructure",
             "Evaluation Plan", "Milestones and Timeline", "Broader Impacts",
             "Results from Prior NSF Support"]:
    report(f"Section present: {name}", name in " ".join(pdtext.split()))

# Placeholders that must be resolved before submission.
todos = re.findall(r"PI TO SUPPLY: [^\]]*", pdtext)
report("No unresolved [PI TO SUPPLY] placeholders", not todos, f"{len(todos)} remaining")
for t in todos:
    print(f"         - {t}")

print("\n" + ("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED (see above)"))
sys.exit(0 if ok else 1)
