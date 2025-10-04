#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Quality Gates: Enforce coverage and mutation testing thresholds.
Fails the build if metrics fall below minimum requirements.
"""
import argparse, json, os, sys, xml.etree.ElementTree as ET
from glob import glob

def find(path_patterns):
    """Find first matching file from pattern list."""
    for p in path_patterns:
        for m in glob(p, recursive=True):
            return m
    return None

def cobertura_coverage(path):
    """Parse Cobertura XML coverage report."""
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        # Try line-rate attribute (0..1) - most common
        rate = root.attrib.get("line-rate")
        if rate is not None:
            return float(rate)

        # Fallback: sum lines-valid/lines-covered per package
        lines_valid = lines_covered = 0
        for c in root.iter("class"):
            lv = c.attrib.get("lines-valid") or c.attrib.get("linesValid")
            lc = c.attrib.get("lines-covered") or c.attrib.get("linesCovered")
            if lv and lc:
                lines_valid += int(float(lv))
                lines_covered += int(float(lc))

        return (lines_covered / lines_valid) if lines_valid else 0.0
    except Exception as e:
        print(f"ERROR parsing coverage XML: {e}", file=sys.stderr)
        return 0.0

def mutation_score(path):
    """Parse Stryker mutation.json for mutation score."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        killed = total = 0
        for f in data.get("files", {}).values():
            for m in f.get("mutants", []):
                total += 1
                if m.get("status", "").lower() == "killed":
                    killed += 1

        return (killed / total) if total else 0.0
    except Exception as e:
        print(f"ERROR parsing mutation JSON: {e}", file=sys.stderr)
        return 0.0

def main():
    ap = argparse.ArgumentParser(
        description="Enforce quality gates for coverage and mutation testing"
    )
    ap.add_argument("--min-coverage", type=float, default=0.80,
                    help="Minimum line coverage (0..1, default: 0.80)")
    ap.add_argument("--min-mutation", type=float, default=0.60,
                    help="Minimum mutation score (0..1, default: 0.60)")
    ap.add_argument("--skip-coverage", action="store_true",
                    help="Skip coverage check (mutation only)")
    ap.add_argument("--skip-mutation", action="store_true",
                    help="Skip mutation check (coverage only)")
    args = ap.parse_args()

    # Find reports
    cov_path = find([
        "reports/cobertura-coverage.xml",
        "reports/coverage.xml",
        "reports/**/cobertura-coverage.xml",
        "reports/**/coverage.xml",
    ]) if not args.skip_coverage else None

    mut_path = find([
        "reports/mutation/mutation.json"
    ]) if not args.skip_mutation else None

    # Validate report existence
    if not args.skip_coverage and not cov_path:
        print("ERROR: Cobertura report not found in reports/", file=sys.stderr)
        print("Expected: reports/coverage.xml or reports/cobertura-coverage.xml", file=sys.stderr)
        sys.exit(2)

    if not args.skip_mutation and not mut_path:
        print("ERROR: Mutation report not found in reports/mutation/", file=sys.stderr)
        print("Expected: reports/mutation/mutation.json", file=sys.stderr)
        sys.exit(2)

    # Parse metrics
    cov = cobertura_coverage(cov_path) if cov_path else 1.0
    mut = mutation_score(mut_path) if mut_path else 1.0

    print(f"📊 Quality Metrics:")
    print(f"  Line coverage: {cov*100:.1f}% (min: {args.min_coverage*100:.1f}%)")
    print(f"  Mutation score: {mut*100:.1f}% (min: {args.min_mutation*100:.1f}%)")
    print()

    # Check thresholds
    failed = []
    if not args.skip_coverage and cov < args.min_coverage:
        failed.append(f"coverage {cov*100:.1f}% < {args.min_coverage*100:.1f}%")
    if not args.skip_mutation and mut < args.min_mutation:
        failed.append(f"mutation {mut*100:.1f}% < {args.min_mutation*100:.1f}%")

    if failed:
        print("❌ QUALITY GATES FAILED:", "; ".join(failed), file=sys.stderr)
        print()
        print("To fix:")
        if "coverage" in " ".join(failed):
            print("  - Add more unit tests to increase coverage")
        if "mutation" in " ".join(failed):
            print("  - Strengthen test assertions to kill more mutants")
            print("  - Cover edge cases and error conditions")
        sys.exit(1)

    print("✅ QUALITY GATES PASSED")
    print()

if __name__ == "__main__":
    main()
