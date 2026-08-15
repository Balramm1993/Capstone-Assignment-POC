"""Deterministic test-case generator using a generate -> critique -> repair loop."""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CATEGORIES = ("positive", "negative", "boundary", "edge")
PRIORITIES = ("P0", "P1", "P2", "P3")

@dataclass
class TestCase:
    id: str
    feature: str
    category: str
    priority: str
    acceptance_criteria: str
    title: str
    preconditions: str
    steps: str
    expected_result: str
    risk: str
    source: str = "generated"

def tc(feature, category, priority, ac, title, preconditions, steps, expected, risk):
    return TestCase("", feature, category, priority, ac, title, preconditions, steps, expected, risk)

class TestCaseAgent:
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.iterations: list[dict[str, Any]] = []

    def generate_initial(self, spec: dict[str, Any]) -> list[TestCase]:
        cases = []
        feature = spec["name"]
        for ac in spec["acceptance_criteria"]:
            ac_id, text = ac["id"], ac["text"]
            cases.append(tc(feature, "positive", "P0", ac_id, f"Verify {ac_id} happy path",
                            "Feature is available", f"Execute the behavior described by {ac_id}",
                            f"The acceptance criterion is satisfied: {text}", "Business-critical behavior"))
            cases.append(tc(feature, "negative", "P1", ac_id, f"Reject invalid condition for {ac_id}",
                            "Feature is available", "Exercise the requirement with an invalid, missing, expired, unauthorized, or otherwise prohibited condition",
                            "The invalid condition is rejected with the required validation/error/state behavior.", "Error handling"))
        return cases

    def critique(self, spec, cases):
        ac_ids = [x["id"] for x in spec["acceptance_criteria"]]
        covered = {ac: set() for ac in ac_ids}
        for case in cases:
            for ac in case.acceptance_criteria.split(","):
                ac = ac.strip()
                if ac in covered:
                    covered[ac].add(case.category)
        gaps = []
        for ac in ac_ids:
            missing = sorted(set(CATEGORIES) - covered[ac])
            if not covered[ac]:
                gaps.append({"ac": ac, "reason": "No test case traces to this acceptance criterion", "missing_categories": list(CATEGORIES)})
            elif missing:
                gaps.append({"ac": ac, "reason": "Category coverage gap", "missing_categories": missing})
        return {"covered_acceptance_criteria": [ac for ac in ac_ids if covered[ac]],
                "uncovered_acceptance_criteria": [ac for ac in ac_ids if not covered[ac]],
                "gaps": gaps, "case_count": len(cases)}

    def repair_from_gaps(self, spec, cases, critique):
        existing = {(c.acceptance_criteria, c.category, c.title) for c in cases}
        additions = []
        for gap in critique["gaps"]:
            for category in gap["missing_categories"]:
                additions.extend(self._missing_case(spec, gap["ac"], category, existing))
        return cases + additions

    def run(self, spec):
        self.iterations = []
        cases = self.generate_initial(spec)
        for i in range(1, self.max_iterations + 1):
            critique = self.critique(spec, cases)
            self.iterations.append({"iteration": i, "critique": critique})
            if not critique["gaps"]:
                break
            repaired = self.repair_from_gaps(spec, cases, critique)
            if len(repaired) == len(cases):
                break
            cases = repaired
        for n, case in enumerate(cases, 1):
            case.id = f"{spec['id']}-TC-{n:03d}"
        final = self.critique(spec, cases)
        return {"spec": spec, "cases": cases, "critique": final, "iterations": self.iterations}

    def _missing_case(self, spec, ac, category, existing):
        feature = spec["name"]
        text = next(x["text"] for x in spec["acceptance_criteria"] if x["id"] == ac)
        templates = {
            "positive": (f"Confirm {ac} with valid inputs", "Use valid inputs and follow the documented flow", f"The required behavior succeeds: {text}"),
            "negative": (f"Reject invalid input/state for {ac}", "Use an invalid, missing, unauthorized, expired, or otherwise prohibited condition", "The system rejects the condition and preserves the required error/state behavior."),
            "boundary": (f"Verify boundary condition for {ac}", "Execute the nearest documented minimum, maximum, threshold, count, amount, or timing boundary", "The system applies the requirement correctly at the boundary and does not cross the documented limit."),
            "edge": (f"Verify edge condition for {ac}", "Exercise an unusual sequence, normalization, timing, state transition, or combination relevant to the requirement", "The system handles the edge condition safely while preserving the acceptance criterion."),
        }
        title, steps, expected = templates[category]
        if (ac, category, title) in existing:
            return []
        priority = "P0" if category in ("positive", "negative", "boundary") else "P1"
        return [tc(feature, category, priority, ac, title, "Feature is available", steps, expected, "Coverage gap repair")]

def write_outputs(result, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    fields = [f.name for f in TestCase.__dataclass_fields__.values()]
    with (outdir / "test_cases.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for case in result["cases"]: writer.writerow(asdict(case))
    lines = []
    for feature in sorted({c.feature for c in result["cases"]}):
        lines.extend([f"Feature: {feature}", ""])
        for case in (c for c in result["cases"] if c.feature == feature):
            lines.extend([f"  # {case.id} | {case.category} | {case.priority} | {case.acceptance_criteria}",
                          f"  Scenario: {case.title}", f"    Given {case.preconditions}",
                          f"    When {case.steps}", f"    Then {case.expected_result}", ""])
    (outdir / "test_suite.feature").write_text("\n".join(lines), encoding="utf-8")
    report = {"features": [{"id": result["spec"]["id"], "name": result["spec"]["name"],
                             "generated_cases": len(result["cases"]), "coverage_gap_report": result["critique"]}],
              "iterations": result["iterations"]}
    (outdir / f"coverage_report_{result['spec']['id']}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Generate traceable test cases from JSON feature specifications")
    parser.add_argument("--spec-dir", default="specs"); parser.add_argument("--out-dir", default="outputs"); parser.add_argument("--iterations", type=int, default=3)
    args = parser.parse_args(); spec_dir, outdir = Path(args.spec_dir), Path(args.out_dir)
    all_cases, summary = [], []
    for path in sorted(spec_dir.glob("feature_*.json")):
        spec = json.loads(path.read_text(encoding="utf-8")); result = TestCaseAgent(args.iterations).run(spec)
        write_outputs(result, outdir); all_cases.extend(result["cases"])
        summary.append({"feature": spec["name"], "cases": len(result["cases"]), "gaps": result["critique"]["gaps"], "iterations": len(result["iterations"])})
    fields = [f.name for f in TestCase.__dataclass_fields__.values()]
    with (outdir / "all_test_cases.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for case in all_cases: writer.writerow(asdict(case))
    (outdir / "coverage_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"features": summary, "total_cases": len(all_cases)}, indent=2, ensure_ascii=False))

if __name__ == "__main__": main()
