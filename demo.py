"""Interactive evaluator demo for the requirement-driven test agent."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent import TestCaseAgent, TestCase

ROOT = Path(__file__).resolve().parent
SPEC_DIR = ROOT / "specs"
OUT_DIR = ROOT / "outputs"


def load_specs() -> dict[str, dict[str, Any]]:
    specs: dict[str, dict[str, Any]] = {}
    for path in sorted(SPEC_DIR.glob("feature_*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        specs[spec["id"].lower()] = spec
    return specs


def make_results(specs):
    print("\nGenerating suites with generate -> critique -> repair...\n")
    results = {}
    for feature_id, spec in specs.items():
        result = TestCaseAgent().run(spec)
        results[feature_id] = result
        TestCaseAgent.write_outputs(result, OUT_DIR)
        print(f"[{feature_id.upper()}] {spec['name']}: {len(result['cases'])} cases | "
              f"{len(result['iterations'])} iterations | final gaps: {len(result['critique']['gaps'])}")
    return results


def header(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def show_loop(result):
    header("GENERATE -> CRITIQUE -> REPAIR LOOP")
    for it in result["iterations"]:
        print(f"Iteration {it['iteration']}: {it['case_count']} cases")
        gaps = it["critique"]["gaps"]
        print(f"  Gaps found: {len(gaps)}")
        for gap in gaps[:10]:
            print(f"    - {gap}")
    print(f"\nFinal gaps: {result['critique']['gaps'] or 'None'}")


def show_cases(cases: list[TestCase], feature_id: str, ac_id=None, category=None):
    selected = [c for c in cases if (ac_id is None or c.acceptance_criteria == ac_id)
                and (category is None or c.category == category)]
    header(f"TEST CASES — Feature {feature_id}")
    if not selected:
        print("No matching test cases found.")
        return
    for case in selected[:15]:
        print(f"{case.id} | {case.category.upper()} | {case.priority} | {case.acceptance_criteria}")
        print(f"  {case.title}")
        print(f"  Rule: {case.rule_trace}")
        print(f"  Steps: {case.steps}")
        print(f"  Expected: {case.expected_result}\n")
    if len(selected) > 15:
        print(f"Showing 15 of {len(selected)} matching cases.")


def ask_agent(results, question):
    q = question.lower().strip()
    feature_id = "a" if "login" in q else "b" if "promo" in q or "checkout" in q else None
    if feature_id is None:
        feature_id = input("Feature (A=Login, B=Promo): ").strip().lower()
    if feature_id not in results:
        print("Please choose feature A or B.")
        return
    result = results[feature_id]
    compact = re.sub(r"\s+", "", q)
    ac_id = next((f"AC{i}" for i in range(1, 20) if f"ac{i}" in compact), None)
    category = next((c for c in ("positive", "negative", "boundary", "edge") if c in q), None)
    if "gap" in q or "coverage" in q:
        header("AGENT COVERAGE ANSWER")
        print("No remaining coverage gaps." if not result["critique"]["gaps"] else "\n".join(result["critique"]["gaps"]))
    elif "why" in q or "explain" in q:
        header("AGENT REASONING TRACE")
        print("The agent maps tests to acceptance criteria and explicit business rules, critiques category/rule coverage, then repairs missing scenarios.")
    else:
        show_cases(result["cases"], feature_id.upper(), ac_id, category)


def menu():
    header("TEST CASE GENERATOR AGENT — INTERACTIVE DEMO")
    print("1. Generate / regenerate both feature suites")
    print("2. Show generate -> critique -> repair loop")
    print("3. Show test cases for an acceptance criterion")
    print("4. Ask the agent a coverage/reasoning question")
    print("5. Show final coverage summary")
    print("6. Show exported output location")
    print("0. Exit")


def main():
    specs = load_specs()
    results = make_results(specs)
    while True:
        menu()
        choice = input("\nChoose an option: ").strip()
        if choice == "0":
            print("\nDemo complete. Thank you.")
            return
        if choice == "1":
            results = make_results(specs)
        elif choice == "2":
            feature = input("Feature (A/B): ").strip().lower()
            if feature in results:
                show_loop(results[feature])
            else:
                print("Please choose A or B.")
        elif choice == "3":
            feature = input("Feature (A=Login, B=Promo): ").strip().lower()
            if feature not in results:
                print("Please choose A or B.")
                continue
            ac_id = input("Acceptance criterion (for example AC6): ").strip().upper()
            category = input("Category (positive/negative/boundary/edge, blank=all): ").strip().lower() or None
            show_cases(results[feature]["cases"], feature.upper(), ac_id, category)
        elif choice == "4":
            question = input("Ask the agent: ").strip()
            if question:
                ask_agent(results, question)
        elif choice == "5":
            header("FINAL COVERAGE SUMMARY")
            for fid, result in results.items():
                covered = len(result["critique"]["by_ac"])
                print(f"Feature {fid.upper()}: {len(result['cases'])} cases | {len(result['iterations'])} iterations | "
                      f"ACs covered: {covered} | gaps: {len(result['critique']['gaps'])}")
        elif choice == "6":
            header("EXPORTED OUTPUTS")
            print(OUT_DIR)
            print("CSV, Gherkin and coverage-gap reports are generated from the same agent state.")
        else:
            print("Invalid choice. Please select 0-6.")


if __name__ == "__main__":
    import re
    main()
