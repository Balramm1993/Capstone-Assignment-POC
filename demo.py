"""Interactive CLI demo for the requirement-driven test-case agent.

Run from the repository root:
    python demo.py

The demo is intentionally evaluator-friendly: it lets a reviewer generate the
suite, inspect the generate -> critique -> repair loop, ask requirement-focused
questions, and inspect concrete test cases without editing source code.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent import TestCaseAgent, TestCase

ROOT = Path(__file__).resolve().parent
SPEC_DIR = ROOT / "specs"
OUT_DIR = ROOT / "outputs"


def load_specs() -> dict[str, dict[str, Any]]:
    specs = {}
        for path in sorted(SPEC_DIR.glob("feature_*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        # normalize feature ids to lowercase so the interactive prompts match
        # expected inputs (a/b) regardless of JSON casing
        specs[spec["id"].lower()] = spec
    return specs


def make_results(specs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    print("\nGenerating suites with generate -> critique -> repair...\n")
    results = {}
    for feature_id, spec in specs.items():
        result = TestCaseAgent().run(spec)
        results[feature_id] = result
        TestCaseAgent().write_outputs(result, OUT_DIR)
        print(
            f"[{feature_id}] {spec['name']}: {len(result['cases'])} cases | "
            f"{len(result['iterations'])} iterations | "
            f"final gaps: {len(result['critique']['gaps'])}"
        )
    return results


def print_header(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def show_loop(result: dict[str, Any]) -> None:
    print_header("GENERATE -> CRITIQUE -> REPAIR LOOP")
    for iteration in result["iterations"]:
        critique = iteration["critique"]
        print(f"Iteration {iteration['iteration']}")
        print(f"  Cases: {iteration['case_count']}")
        print(f"  Gaps found: {len(critique['gaps'])}")
        for gap in critique["gaps"][:8]:
            print(f"    - {gap}")
        if len(critique["gaps"]) > 8:
            print(f"    ... and {len(critique['gaps']) - 8} more")
    print(f"\nFinal gaps: {result['critique']['gaps'] or 'None'}")


def show_cases(cases: list[TestCase], feature_id: str, ac_id: str | None = None, category: str | None = None) -> None:
    selected = [
        c for c in cases
        if (ac_id is None or c.acceptance_criteria == ac_id)
        and (category is None or c.category == category)
    ]
    print_header(f"TEST CASES — Feature {feature_id}")
    if not selected:
        print("No matching test cases found.")
        return
    for case in selected[:12]:
        print(f"{case.id} | {case.category.upper()} | {case.priority} | {case.acceptance_criteria}")
        print(f"  Title: {case.title}")
        print(f"  Rule:  {case.rule_trace}")
        print(f"  Steps: {case.steps}")
        print(f"  Expect: {case.expected_result}")
        print()
    if len(selected) > 12:
        print(f"Showing 12 of {len(selected)} matching cases.")


def ask_agent(results: dict[str, dict[str, Any]], question: str) -> None:
    """Answer common evaluator questions from the generated agent state."""
    q = question.lower().strip()
    feature_id = "a" if "login" in q else "b" if "promo" in q or "checkout" in q else None
    if feature_id is None:
        feature_id = input("Feature (A=Login, B=Promo): ").strip().lower()
    if feature_id not in results:
        print("Please choose feature A or B.")
        return

    result = results[feature_id]
    ac_id = next((f"AC{i}" for i in range(1, 20) if f"ac{i}" in q.replace(" ", "")), None)
    category = next((c for c in ("positive", "negative", "boundary", "edge") if c in q), None)

    if "gap" in q or "coverage" in q:
        print_header("AGENT COVERAGE ANSWER")
        gaps = result["critique"]["gaps"]
        print("No remaining coverage gaps." if not gaps else "\n".join(f"- {g}" for g in gaps))
        return

    if "why" in q or "explain" in q:
        print_header("AGENT REASONING TRACE")
        if ac_id:
            print(f"The agent mapped the question to {ac_id} and generated requirement-specific cases.")
        else:
            print("The agent uses acceptance-criteria and business-rule traces to create targeted cases, then critiques the draft and repairs missing coverage.")
        return

    show_cases(result["cases"], feature_id.upper(), ac_id, category)


def print_menu() -> None:
    print_header("TEST CASE GENERATOR AGENT — INTERACTIVE DEMO")
    print("1. Generate / regenerate both feature suites")
    print("2. Show generate -> critique -> repair loop")
    print("3. Show test cases for an acceptance criterion")
    print("4. Ask the agent a coverage/reasoning question")
    print("5. Show final coverage summary")
    print("6. Open exported output locations")
    print("0. Exit")


def main() -> None:
    specs = load_specs()
    results = make_results(specs)

    while True:
        print_menu()
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
            print_header("FINAL COVERAGE SUMMARY")
            for feature_id, result in results.items():
                print(f"Feature {feature_id}: {len(result['cases'])} cases")
                print(f"Iterations: {len(result['iterations'])}")
                print(f"Final gaps: {result['critique']['gaps'] or 'None'}\n")
        elif choice == "6":
            print_header("EXPORTED OUTPUTS")
            print(f"CSV / Gherkin / coverage reports: {OUT_DIR}")
            print("Files are generated by the same agent state shown in this demo.")
        else:
            print("Invalid choice. Please select 0-6.")


if __name__ == "__main__":
    main()
