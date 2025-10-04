#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Generate GitHub Actions Step Summary from test reports.
Outputs Markdown to stdout for use with $GITHUB_STEP_SUMMARY.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPORTS_DIR = Path("reports")
ROOT = Path(".")


def read_junit():
    """Parse JUnit XML for test results."""
    junit_paths = list(REPORTS_DIR.glob("**/junit.xml")) + list(ROOT.glob("junit.xml"))
    if not junit_paths:
        return None

    junit_file = junit_paths[0]
    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()

        # Handle both <testsuites> and <testsuite> root elements
        if root.tag == "testsuites":
            suites = root.findall("testsuite")
            tests = sum(int(s.get("tests", 0)) for s in suites)
            failures = sum(int(s.get("failures", 0)) for s in suites)
            errors = sum(int(s.get("errors", 0)) for s in suites)
            skipped = sum(int(s.get("skipped", 0)) for s in suites)
            time = sum(float(s.get("time", 0)) for s in suites)
        else:
            tests = int(root.get("tests", 0))
            failures = int(root.get("failures", 0))
            errors = int(root.get("errors", 0))
            skipped = int(root.get("skipped", 0))
            time = float(root.get("time", 0))

        return {
            "tests": tests,
            "failures": failures,
            "errors": errors,
            "skipped": skipped,
            "passed": tests - failures - errors - skipped,
            "time": time
        }
    except Exception as e:
        print(f"<!-- Warning: Failed to parse JUnit XML: {e} -->", file=sys.stderr)
        return None


def read_mutation():
    """Parse Stryker mutation.json for mutation score."""
    mutation_file = REPORTS_DIR / "mutation" / "mutation.json"
    if not mutation_file.exists():
        return None

    try:
        with open(mutation_file) as f:
            data = json.load(f)

        # Extract mutation metrics
        files = data.get("files", {})
        total_mutants = 0
        killed = 0
        survived = 0
        timeout = 0
        no_coverage = 0

        for file_data in files.values():
            mutants = file_data.get("mutants", [])
            total_mutants += len(mutants)
            for mutant in mutants:
                status = mutant.get("status", "")
                if status == "Killed":
                    killed += 1
                elif status == "Survived":
                    survived += 1
                elif status == "Timeout":
                    timeout += 1
                elif status == "NoCoverage":
                    no_coverage += 1

        score = (killed / total_mutants * 100) if total_mutants > 0 else 0

        return {
            "score": score,
            "total": total_mutants,
            "killed": killed,
            "survived": survived,
            "timeout": timeout,
            "no_coverage": no_coverage
        }
    except Exception as e:
        print(f"<!-- Warning: Failed to parse mutation.json: {e} -->", file=sys.stderr)
        return None


def read_coverage():
    """Parse coverage.xml for coverage percentage."""
    coverage_file = REPORTS_DIR / "coverage.xml"
    if not coverage_file.exists():
        return None

    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()

        # Cobertura format: <coverage line-rate="0.85" ...>
        line_rate = float(root.get("line-rate", 0))
        branch_rate = float(root.get("branch-rate", 0))

        return {
            "line": line_rate * 100,
            "branch": branch_rate * 100
        }
    except Exception as e:
        print(f"<!-- Warning: Failed to parse coverage.xml: {e} -->", file=sys.stderr)
        return None


def generate_summary():
    """Generate GitHub-flavored Markdown summary."""
    print("# 🤖 AI Pipeline - Test Results")
    print()

    # Test results
    junit = read_junit()
    if junit:
        passed = junit["passed"]
        total = junit["tests"]
        failures = junit["failures"]
        errors = junit["errors"]

        status_icon = "✅" if failures == 0 and errors == 0 else "❌"
        print(f"## {status_icon} Unit Tests")
        print()
        print(f"- **Total**: {total} tests")
        print(f"- **Passed**: {passed} ✅")
        if failures > 0:
            print(f"- **Failed**: {failures} ❌")
        if errors > 0:
            print(f"- **Errors**: {errors} ⚠️")
        if junit["skipped"] > 0:
            print(f"- **Skipped**: {junit['skipped']} ⏭️")
        print(f"- **Duration**: {junit['time']:.2f}s")
        print()
    else:
        print("## ⚠️ Unit Tests")
        print()
        print("No JUnit report found.")
        print()

    # Coverage
    coverage = read_coverage()
    if coverage:
        line_pct = coverage["line"]
        icon = "🟢" if line_pct >= 80 else "🟡" if line_pct >= 60 else "🔴"
        print(f"## {icon} Code Coverage")
        print()
        print(f"- **Line Coverage**: {line_pct:.1f}%")
        print(f"- **Branch Coverage**: {coverage['branch']:.1f}%")
        print()

    # Mutation testing
    mutation = read_mutation()
    if mutation:
        score = mutation["score"]
        icon = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        print(f"## {icon} Mutation Testing")
        print()
        print(f"- **Mutation Score**: {score:.1f}%")
        print(f"- **Total Mutants**: {mutation['total']}")
        print(f"- **Killed**: {mutation['killed']} 💀")
        print(f"- **Survived**: {mutation['survived']} 🧟")
        if mutation["timeout"] > 0:
            print(f"- **Timeout**: {mutation['timeout']} ⏱️")
        if mutation["no_coverage"] > 0:
            print(f"- **No Coverage**: {mutation['no_coverage']} ⚠️")
        print()

        # Thresholds
        thresholds = {"high": 80, "low": 60, "break": 50}
        if score >= thresholds["high"]:
            print("✅ **Status**: Excellent mutation coverage!")
        elif score >= thresholds["low"]:
            print("✅ **Status**: Good mutation coverage")
        elif score >= thresholds["break"]:
            print("⚠️ **Status**: Acceptable (above break threshold)")
        else:
            print("❌ **Status**: Below break threshold - improve tests!")
        print()

    # Artifacts
    print("## 📦 Artifacts")
    print()
    print("The following reports are available as artifacts:")
    print()

    if junit:
        print("- `junit.xml` - Unit test results")
    if coverage:
        print("- `reports/coverage.xml` - Coverage report (Cobertura)")
        print("- `reports/lcov.info` - Coverage report (LCOV)")
    if mutation:
        print("- `reports/mutation/mutation.html` - Interactive mutation report")
        print("- `reports/mutation/mutation.json` - Mutation data (JSON)")

    print()
    print("---")
    print()
    print("🤖 *Generated by orion-ai-kit CI pipeline*")


if __name__ == "__main__":
    generate_summary()
