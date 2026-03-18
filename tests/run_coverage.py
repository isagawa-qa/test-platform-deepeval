"""Requirements coverage checker for platform-deepeval spec."""

import re
import os
import json
import glob

GATE_CONTRACT = os.path.join(
    os.path.dirname(__file__), "..", ".claude", "skills",
    "deepeval-management-layer", "gate-contract.md"
)
FRAMEWORK_DIR = os.path.join(os.path.dirname(__file__), "..", "framework")


def extract_reqs_from_gate_contract(path):
    """Extract REQ IDs from gate-contract.md Requirements Registry."""
    reqs = {}
    with open(path, "r") as f:
        content = f.read()
    pattern = r"\|\s*(REQ-[A-Z]+-\d+)\s*\|[^|]+\|\s*([^|]+)\|"
    for match in re.finditer(pattern, content):
        req_id = match.group(1).strip()
        requirement = match.group(2).strip()
        reqs[req_id] = requirement
    return reqs


def extract_reqs_from_tests(framework_dir):
    """Extract REQ IDs from test function names."""
    found = {}
    test_files = glob.glob(os.path.join(framework_dir, "**", "test_*.py"), recursive=True)
    for test_file in test_files:
        with open(test_file, "r") as f:
            content = f.read()
        for match in re.finditer(r"def (test_\w*REQ_[A-Z]+_\d+\w*)", content):
            func_name = match.group(1)
            req_match = re.search(r"REQ_([A-Z]+)_(\d+)", func_name)
            if req_match:
                req_id = f"REQ-{req_match.group(1)}-{req_match.group(2)}"
                found[req_id] = func_name
    return found


def run_coverage():
    """Run coverage check and print report."""
    reqs = extract_reqs_from_gate_contract(GATE_CONTRACT)
    implemented = extract_reqs_from_tests(FRAMEWORK_DIR)

    print("Requirements Coverage Report")
    print("=" * 40)
    print(f"Total REQs: {len(reqs)}")
    print(f"Implemented: {len(implemented)} (tests found with matching REQ ID)")
    missing = set(reqs.keys()) - set(implemented.keys())
    print(f"Missing: {len(missing)}")
    print()

    for req_id in sorted(reqs.keys()):
        if req_id in implemented:
            print(f"[PASS] {req_id}: {implemented[req_id]}")
        else:
            print(f"[MISS] {req_id}: No test found")

    coverage_pct = (len(implemented) / len(reqs) * 100) if reqs else 0
    print(f"\nCoverage: {coverage_pct:.1f}%")

    report = {
        "requirements_coverage": {
            "total_reqs": len(reqs),
            "implemented": len(implemented),
            "missing": len(missing),
            "coverage_pct": round(coverage_pct, 1),
            "missing_reqs": sorted(list(missing))
        }
    }

    report_path = os.path.join(os.path.dirname(__file__), "validation-report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    run_coverage()
