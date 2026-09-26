#!/usr/bin/env python3
"""Recompress the paper PDFs with a visual gate.

Downsamples embedded images, subsets fonts and rewrites the file with
PyMuPDF, then renders every page of the original and the candidate at low
resolution and compares the amount of ink. A candidate is rejected when the
page count differs or any page loses more than MAX_INK_LOSS of its ink; a
candidate that saves less than MIN_SAVING is not worth the change.

Not a project dependency: `pip install pymupdf` into the venv first.

    python3 tools/recompress_pdfs.py content/files/papers/*.pdf --out /tmp/rc
    python3 tools/recompress_pdfs.py content/files/papers/*.pdf --replace
"""
import argparse
import os
import sys

import pymupdf

RENDER_DPI = 36
MAX_INK_LOSS = 0.07
MIN_SAVING = 0.10


def ink_per_page(path):
    doc = pymupdf.open(path)
    inks = []
    for page in doc:
        pix = page.get_pixmap(dpi=RENDER_DPI, colorspace=pymupdf.csGRAY, alpha=False)
        inks.append(len(pix.samples) * 255 - sum(pix.samples))
    doc.close()
    return inks


def candidate(src, dst, dpi_target, quality):
    doc = pymupdf.open(src)
    doc.rewrite_images(dpi_threshold=dpi_target + 50, dpi_target=dpi_target,
                       quality=quality, set_to_gray=False)
    doc.subset_fonts()
    doc.save(dst, garbage=4, deflate=True, clean=True)
    doc.close()


def gate(src, dst):
    before, after = ink_per_page(src), ink_per_page(dst)
    if len(before) != len(after):
        return False, f'page count {len(before)} -> {len(after)}'
    worst = 0.0
    for b, a in zip(before, after):
        if b == 0:
            continue
        worst = max(worst, (b - a) / b)
    return worst <= MAX_INK_LOSS, f'worst page ink loss {worst:.1%}'


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pdfs', nargs='+')
    ap.add_argument('--out', default='/tmp/recompress', help='where candidates go')
    ap.add_argument('--dpi', type=int, default=150)
    ap.add_argument('--quality', type=int, default=80)
    ap.add_argument('--replace', action='store_true',
                    help='overwrite each source with its accepted candidate')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pymupdf.TOOLS.mupdf_display_errors(False)

    total_before = total_after = 0
    for src in a.pdfs:
        dst = os.path.join(a.out, os.path.basename(src))
        size = os.path.getsize(src)
        try:
            candidate(src, dst, a.dpi, a.quality)
        except Exception as exc:  # a PDF PyMuPDF cannot rewrite stays as it is
            print(f'{os.path.basename(src):40} {size/1e6:6.2f} MB  SKIP ({exc})')
            total_before += size; total_after += size
            continue
        new = os.path.getsize(dst)
        ok, why = gate(src, dst)
        saving = 1 - new / size
        verdict = 'ok' if ok and saving >= MIN_SAVING else (
            'REJECT' if not ok else 'keep')
        print(f'{os.path.basename(src):40} {size/1e6:6.2f} -> {new/1e6:6.2f} MB '
              f'({saving:5.1%})  {verdict:6} {why}')
        total_before += size
        if verdict == 'ok':
            total_after += new
            if a.replace:
                os.replace(dst, src)
        else:
            total_after += size
            os.remove(dst)
    print(f'{"total":40} {total_before/1e6:6.2f} -> {total_after/1e6:6.2f} MB')
    return 0


if __name__ == '__main__':
    sys.exit(main())
