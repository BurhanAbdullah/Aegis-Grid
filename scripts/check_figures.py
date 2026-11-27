"""Reproduce all committed figures and diagrams from committed source runs."""
import glob
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import pypdfium2 as pdfium
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG = os.path.join(ROOT, "figures")
PDF_DATES = re.compile(rb"/(CreationDate|ModDate) *\(D:[^)]*\)")

def content(path):
    data = open(path, "rb").read()
    return PDF_DATES.sub(b"", data) if path.endswith(".pdf") else data


def visual_array(path):
    if path.endswith(".png"):
        with Image.open(path) as image:
            return np.asarray(image.convert("RGBA")), None
    if path.endswith(".pdf"):
        document = pdfium.PdfDocument(path)
        if len(document) != 1:
            raise ValueError(f"{path}: expected one page, found {len(document)}")
        page = document[0]
        page_size = tuple(round(v, 4) for v in page.get_size())
        bitmap = page.render(scale=3)
        return np.asarray(bitmap.to_pil().convert("RGBA")), page_size
    return None, None


def visual_diagnostic(committed_path, generated_path):
    try:
        left, left_size = visual_array(committed_path)
        right, right_size = visual_array(generated_path)
        if left is None or right is None:
            return "not a raster/vector image"
        if left.shape != right.shape:
            return f"render dimensions differ: {left.shape} vs {right.shape}"
        delta = np.abs(left.astype(np.int16) - right.astype(np.int16))
        changed = np.any(delta != 0, axis=2)
        return (
            f"pixel_equal={not bool(np.any(changed))}; "
            f"changed_pixels={int(changed.sum())}/{changed.size}; "
            f"mean_abs_channel_delta={float(delta.mean()):.6f}; "
            f"max_channel_delta={int(delta.max())}; "
            f"pdf_page_points={left_size or right_size}"
        )
    except Exception as exc:
        return f"visual diagnostic unavailable: {type(exc).__name__}: {exc}"

with tempfile.TemporaryDirectory() as out:
    env = dict(os.environ, FIGURES_OUT=out)
    for script in ("make_figures.py", "make_diagrams.py"):
        print(f"RUNNING {script}", flush=True)
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", script)],
            check=False, cwd=ROOT, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if result.stdout:
            print(result.stdout, end="", flush=True)
        if result.returncode:
            raise SystemExit(f"{script} exited with status {result.returncode}")
    committed = sorted(
        os.path.relpath(p, FIG)
        for p in glob.glob(os.path.join(FIG, "**", "*.*"), recursive=True)
        if os.path.isfile(p)
    )
    generated = sorted(
        os.path.relpath(p, out)
        for p in glob.glob(os.path.join(out, "**", "*.*"), recursive=True)
        if os.path.isfile(p)
    )
    bad = sorted(set(committed) ^ set(generated))
    bad += [
        p for p in sorted(set(committed) & set(generated))
        if content(os.path.join(FIG, p)) != content(os.path.join(out, p))
    ]
    if bad:
        print(f"MISMATCH: {len(bad)} figure files")
        for path in bad:
            committed_path = os.path.join(FIG, path)
            generated_path = os.path.join(out, path)
            committed_size = os.path.getsize(committed_path) if os.path.isfile(committed_path) else None
            generated_size = os.path.getsize(generated_path) if os.path.isfile(generated_path) else None
            diagnostic = visual_diagnostic(committed_path, generated_path) if (
                os.path.isfile(committed_path) and os.path.isfile(generated_path)
            ) else "file missing on one side"
            print(
                f"  {path}: committed_bytes={committed_size}; "
                f"generated_bytes={generated_size}; {diagnostic}"
            )
        print("GENERATED FILES:")
        for path in generated:
            print(f"  {path}")
        sys.exit(1)
    print(f"{len(committed)} figure files reproduced from the committed runs")
