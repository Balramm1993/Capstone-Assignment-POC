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
        agent = TestCaseAgent()
        result = agent.run(spec)
        results[feature_id] = result
        agent.write_outputs(result, OUT_DIR)
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
    spec = results[feature_id + "_spec"]
    compact = re.sub(r"\s+", "", q)
    ac_id = next((f"AC{i}" for i in range(1, 20) if f"ac{i}" in compact), None)
    category = next((c for c in ("positive", "negative", "boundary", "edge") if c in q), None)
    
    # Coverage and gaps
    if "gap" in q or ("coverage" in q and "gap" in q) or "missing" in q or "uncovered" in q:
        header("AGENT COVERAGE ANALYSIS")
        gaps = result["critique"]["gaps"]
        covered = result["critique"]["covered_acceptance_criteria"]
        if not gaps:
            print(f"✅ No remaining coverage gaps!")
            print(f"   All {len(covered)} acceptance criteria are fully covered.")
            print(f"   Iterations to full coverage: {len(result['iterations'])}")
        else:
            print(f"❌ Found {len(gaps)} coverage gaps:")
            for gap in gaps:
                print(f"   - {gap['id']}: {gap['reason']}")
    
    # Test cases by category or AC
    elif "case" in q or "test" in q or "scenario" in q or "boundary" in q or "edge" in q or "negative" in q or "positive" in q:
        if "boundary" in q:
            category = "boundary"
        elif "edge" in q:
            category = "edge"
        elif "negative" in q:
            category = "negative"
        elif "positive" in q:
            category = "positive"
        
        header(f"TEST CASES — Feature {feature_id.upper()}")
        show_cases(result["cases"], feature_id.upper(), ac_id, category)
    
    # Design reasoning
    elif "why" in q or "explain" in q or "reason" in q or "design" in q:
        header("AGENT REASONING & DESIGN RATIONALE")
        print("\n🤖 AGENT EXPLANATION:\n")
        print("The agent implements a generate-critique-repair loop:")
        print("  1. GENERATE: Creates initial draft of positive/negative cases")
        print("  2. CRITIQUE: Analyzes coverage against:")
        print("     - All acceptance criteria (positive/negative/boundary/edge)")
        print("     - Explicit business rules")
        print("     - Required error messages")
        print("     - Category completeness")
        print("  3. REPAIR: Adds targeted cases for detected gaps")
        print("  4. RE-CRITIQUE: Validates that all gaps are resolved")
        print("\n📊 GENERATION STATISTICS:")
        print(f"  - Initial cases: {result['iterations'][0]['case_count']}")
        if len(result['iterations']) > 1:
            print(f"  - After repair: {result['iterations'][-1]['case_count']}")
        print(f"  - Total iterations: {len(result['iterations'])}")
        print(f"  - Final gaps: {len(result['critique']['gaps'])}")
        print("\n🎯 WHY THESE SPECIFIC CASES:")
        ac_report = result['critique']['acceptance_criteria']
        print(f"  Each of {len(ac_report)} acceptance criteria has all 4 required categories:")
        for ac in ac_report[:3]:
            print(f"    - {ac['ac']}: {', '.join(ac['categories_present'])}")
        if len(ac_report) > 3:
            print(f"    ... and {len(ac_report) - 3} more")
    
    # Coverage summary
    elif "coverage" in q or "summary" in q or "status" in q:
        header("COMPREHENSIVE COVERAGE REPORT")
        coverage = result["critique"]
        print(f"\n📈 OVERALL METRICS:")
        print(f"  - Total test cases: {len(result['cases'])}")
        print(f"  - Feature: {spec['name']}")
        print(f"  - Acceptance criteria: {len(coverage['acceptance_criteria'])}")
        print(f"  - Covered ACs: {len(coverage['covered_acceptance_criteria'])}")
        print(f"  - Coverage gaps: {len(coverage['gaps'])}")
        print(f"  - Iterations to completion: {len(result['iterations'])}")
        
        print(f"\n✅ ACCEPTANCE CRITERIA COVERAGE:")
        for ac in coverage['acceptance_criteria'][:5]:
            status = "✓" if not ac['missing_categories'] else "✗"
            print(f"  {status} {ac['ac']}: {', '.join(ac['categories_present'])}")
        if len(coverage['acceptance_criteria']) > 5:
            print(f"  ... and {len(coverage['acceptance_criteria']) - 5} more")
        
        if coverage['required_messages']:
            print(f"\n💬 REQUIRED MESSAGE COVERAGE:")
            for msg in coverage['required_messages'][:3]:
                status = "✓" if msg['covered'] else "✗"
                print(f"  {status} {msg['ac']}: '{msg['message']}'")
            if len(coverage['required_messages']) > 3:
                print(f"  ... and {len(coverage['required_messages']) - 3} more")
    
    # General help
    else:
        header("AGENT CAPABILITIES")
        print("\n🤖 I can answer questions like:")
        print("  • 'What coverage gaps remain?' - Gap analysis")
        print("  • 'Show boundary cases for AC6' - Filtered test cases")
        print("  • 'Why did you add edge cases?' - Design reasoning")
        print("  • 'Show coverage summary' - Complete coverage report")
        print("  • 'What boundary cases exist?' - Category filtering")
        print("\nTry asking in natural language - I'll understand! 😊")


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
    # Store specs in results for ask_agent to access
    for spec_id, spec in specs.items():
        results[spec_id + "_spec"] = spec
    
    while True:
        menu()
        choice = input("\nChoose an option: ").strip()
        if choice == "0":
            print("\nDemo complete. Thank you.")
            return
        if choice == "1":
            results = make_results(specs)
            for spec_id, spec in specs.items():
                results[spec_id + "_spec"] = spec
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
                covered = len(result["critique"]["covered_acceptance_criteria"])
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
