#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproducible release builder for the Linkwave Technology website.

Builds every generated page from the frozen baseline commit plus the versioned
tools in this repository only. No file outside the repository is required.

Usage:
    python tools/build_release.py --check --repeat
    python tools/build_release.py --apply
    python tools/build_release.py --manifest tools/build-manifest.json

Exit codes: 0 = all checks passed, 1 = build/verification mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent
GENERATOR = TOOLS / "release_build.py"
DEFAULT_BASELINE = "da5ee8b"

OUTPUT_GLOBS = [
    "*.html",
    "ar/*.html",
    "css/*.css",
    "js/*.js",
    "sitemap.xml",
    "robots.txt",
    "site.webmanifest",
    "THIRD-PARTY-NOTICES.txt",
]

EXPECTED = {
    "english_pages": 19,      # 18 content pages + 404.html
    "arabic_pages": 18,
    "generated_text_files": 51,
    "sitemap_urls": 36,
    "hero_slides": 6,
    "service_rows": 10,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_baseline(dest: Path, baseline: str) -> None:
    """Extract the frozen baseline commit without any EOL conversion."""
    tar_path = dest.parent / ("baseline-%s.tar" % baseline)
    subprocess.run(
        ["git", "-C", str(REPO), "-c", "core.autocrlf=false", "archive",
         "--format=tar", "-o", str(tar_path), baseline],
        check=True, capture_output=True,
    )
    with tarfile.open(tar_path) as archive:
        archive.extractall(dest, filter="data")
    tar_path.unlink()


def run_generator(dest: Path) -> None:
    env = os.environ.copy()
    env["LINKWAVE_SITE"] = str(dest)
    env["PYTHONIOENCODING"] = "utf-8"
    config_path = TOOLS / "build-config.json"
    form_origin = ""
    if config_path.exists():
        form_origin = str(json.loads(config_path.read_text(encoding="utf-8")).get("formOrigin") or "")
    env_origin = os.environ.get("LINKWAVE_FORM_ORIGIN", "").strip()
    env["LINKWAVE_FORM_ORIGIN"] = env_origin or form_origin
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=str(REPO), env=env, capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stdout[-2000:])
        sys.stderr.write(result.stderr[-4000:])
        raise SystemExit("generator failed with exit code %d" % result.returncode)


def build_once(baseline: str) -> Path:
    temp = Path(tempfile.mkdtemp(prefix="linkwave-build-"))
    dest = temp / "site"
    dest.mkdir()
    extract_baseline(dest, baseline)
    run_generator(dest)
    return dest


def generated_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for pattern in OUTPUT_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                files[str(path.relative_to(root)).replace(os.sep, "/")] = path
    return files


def normalized_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def validate_structure(root: Path, label: str) -> list[str]:
    errors: list[str] = []
    en_pages = len(list(root.glob("*.html")))
    ar_pages = len(list((root / "ar").glob("*.html")))
    files = generated_files(root)
    if en_pages != EXPECTED["english_pages"]:
        errors.append("%s: English pages %d != %d" % (label, en_pages, EXPECTED["english_pages"]))
    if ar_pages != EXPECTED["arabic_pages"]:
        errors.append("%s: Arabic pages %d != %d" % (label, ar_pages, EXPECTED["arabic_pages"]))
    if len(files) != EXPECTED["generated_text_files"]:
        errors.append("%s: generated text files %d != %d" % (label, len(files), EXPECTED["generated_text_files"]))
    sitemap = root / "sitemap.xml"
    if sitemap.exists():
        urls = re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8"))
        if len(urls) != EXPECTED["sitemap_urls"]:
            errors.append("%s: sitemap %d != %d" % (label, len(urls), EXPECTED["sitemap_urls"]))
    else:
        errors.append("%s: sitemap.xml missing" % label)
    index = root / "index.html"
    if index.exists():
        html = index.read_text(encoding="utf-8")
        slides = len(re.findall(r'class="lw-slide(?: is-active)?"', html))
        rows = html.count('class="lw-service-row"') + html.count('class="lw-service-row ')
        if slides != EXPECTED["hero_slides"]:
            errors.append("%s: hero slides %d != %d" % (label, slides, EXPECTED["hero_slides"]))
        if rows != EXPECTED["service_rows"]:
            errors.append("%s: service rows %d != %d" % (label, rows, EXPECTED["service_rows"]))
    else:
        errors.append("%s: index.html missing" % label)
    return errors


def compare_with_repo(build_root: Path) -> list[str]:
    errors: list[str] = []
    for rel, path in generated_files(build_root).items():
        repo_file = REPO / rel
        if not repo_file.exists():
            errors.append("missing in repository: " + rel)
        elif normalized_bytes(path) != normalized_bytes(repo_file):
            errors.append("content differs from repository: " + rel)
    return errors


def copy_to_repo(build_root: Path) -> None:
    for rel, path in generated_files(build_root).items():
        target = REPO / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    print("applied %d generated files to %s" % (len(generated_files(build_root)), REPO))


def write_manifest(build_root: Path, path: Path, baseline: str) -> None:
    files = generated_files(build_root)
    data = {
        "baselineCommit": baseline,
        "generatorSha256": sha256(GENERATOR),
        "toolSha256": {
            name: sha256(TOOLS / name)
            for name in ["release_build.py", "ar_egyptian.py", "services_data.py", "hero_data.py",
                         "artifacts/linkwave.js", "artifacts/site-config.js"]
        },
        "expected": EXPECTED,
        "generatedFileCount": len(files),
        "generatedFiles": {rel: sha256(p) for rel, p in sorted(files.items())},
        "generatedAggregateSha256": hashlib.sha256(
            "\n".join("%s %s" % (rel, sha256(p)) for rel, p in sorted(files.items())).encode("utf-8")
        ).hexdigest(),
    }
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print("sealed manifest:", path, "| aggregate:", data["generatedAggregateSha256"][:24])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=DEFAULT_BASELINE)
    parser.add_argument("--apply", action="store_true", help="copy generated files into the working tree")
    parser.add_argument("--check", action="store_true", help="compare generated output with the working tree")
    parser.add_argument("--repeat", action="store_true", help="build twice and prove determinism")
    parser.add_argument("--manifest", type=Path, help="write a sealed build manifest to this path")
    args = parser.parse_args()

    if not args.apply and not args.check and not args.repeat and not args.manifest:
        args.check = True

    print("repo:", REPO)
    print("baseline:", args.baseline)
    print("generator:", GENERATOR)
    first = build_once(args.baseline)
    errors = validate_structure(first, "build#1")
    print("build#1 text files:", len(generated_files(first)))

    if args.repeat:
        second = build_once(args.baseline)
        errors += validate_structure(second, "build#2")
        files_a = {rel: sha256(p) for rel, p in generated_files(first).items()}
        files_b = {rel: sha256(p) for rel, p in generated_files(second).items()}
        if files_a != files_b:
            differing = sorted(set(files_a) | set(files_b))
            differing = [k for k in differing if files_a.get(k) != files_b.get(k)]
            errors.append("non-deterministic output files: " + ", ".join(differing[:10]))
        print("determinism:", "PASS (51/51 identical)" if not errors else "FAIL")

    if args.check:
        errors += compare_with_repo(first)
        print("repository comparison:", "PASS (51/51 identical)" if not errors else "FAIL")

    if args.manifest:
        write_manifest(first, args.manifest, args.baseline)

    if args.apply:
        copy_to_repo(first)

    if errors:
        print("RESULT: FAIL")
        for error in errors:
            print(" -", error)
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
