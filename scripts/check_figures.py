"""Check that every committed figure is reproduced from the committed run
directories: regenerate figures/ and figures/diagrams/ into a temporary
directory with scripts/make_figures.py and scripts/make_diagrams.py and compare
each file byte for byte. PDF files are compared without their CreationDate and
ModDate entries, which record the time of writing. Exit 1 on any difference."""
import glob, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG = os.path.join(ROOT, "figures")
PDF_DATES = re.compile(rb"/(CreationDate|ModDate) *\(D:[^)]*\)")


def content(path):
    data = open(path, "rb").read()
    return PDF_DATES.sub(b"", data) if path.endswith(".pdf") else data


with tempfile.TemporaryDirectory() as out:
    env = dict(os.environ, FIGURES_OUT=out)
    for script in ("make_figures.py", "make_diagrams.py"):
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", script)], check=True, cwd=ROOT,
                       env=env, stdout=subprocess.DEVNULL)
    committed = sorted(os.path.relpath(p, FIG) for p in glob.glob(os.path.join(FIG, "**", "*.*"), recursive=True))
    generated = sorted(os.path.relpath(p, out) for p in glob.glob(os.path.join(out, "**", "*.*"), recursive=True))
    bad = sorted(set(committed) ^ set(generated))
    bad += [p for p in sorted(set(committed) & set(generated))
            if content(os.path.join(FIG, p)) != content(os.path.join(out, p))]
if bad:
    print(f"MISMATCH: {len(bad)} figure files")
    for path in bad:
        committed_path = os.path.join(FIG, path)
        generated_path = os.path.join(out, path)
        committed_size = os.path.getsize(committed_path) if os.path.isfile(committed_path) else None
        generated_size = os.path.getsize(generated_path) if os.path.isfile(generated_path) else None
        print(f"  {path}: committed_bytes={committed_size}; generated_bytes={generated_size}")
    sys.exit(1)
print(f"{len(committed)} figure files reproduced from the committed runs")
