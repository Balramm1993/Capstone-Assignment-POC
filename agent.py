"""Requirement-driven test-case generation agent.

Implements a generate → critique → repair loop to produce categorized,
risk-prioritized test cases from requirements and acceptance criteria.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
from datetime import datetime


@dataclass
class TestCase:
    """A single test case with requirement traceability."""
    id: str
    title: str
    description: str
    steps: list[str]
    expected_result: str
    acceptance_criteria: str
    category: str
    risk_level: str
    positive: bool
    feature_id: str
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CritiqueResult:
    """Results from critiquing generated cases."""
    gaps: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    coverage: dict[str, int] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Result from one generation iteration."""
    cases: list[TestCase]
    critique: CritiqueResult
    iterations: list[dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class TestCaseAgent:
    """Requirement-driven test case generator with critique and repair."""
    
    CATEGORIES = ["positive", "negative", "boundary", "edge"]
    RISK_LEVELS = ["P0", "P1", "P2", "P3"]
    MAX_ITERATIONS = 3
    
    def __init__(self):
        self.iteration_count = 0
    
    def run(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Execute generate → critique → repair loop."""
        self.iteration_count = 0
        cases: list[TestCase] = []
        iterations: list[dict[str, Any]] = []
        
        for iteration in range(self.MAX_ITERATIONS):
            self.iteration_count = iteration + 1
            
            # Generate initial or repair batch
            if iteration == 0:
                batch = self._generate(spec, cases)
            else:
                batch = self._repair(spec, cases, critique)
            
            cases.extend(batch)
            
            # Critique all cases
            critique = self._critique(spec, cases)
            
            # Record iteration
            iterations.append({
                "iteration": self.iteration_count,
                "cases_generated": len(batch),
                "total_cases": len(cases),
                "gaps_found": len(critique.gaps),
                "issues": critique.issues,
                "suggestions": critique.suggestions
            })
            
            # Stop if no gaps
            if not critique.gaps:
                break
        
        return {
            "feature_id": spec["id"],
            "feature_name": spec["name"],
            "cases": cases,
            "critique": {
                "gaps": critique.gaps,
                "issues": critique.issues,
                "suggestions": critique.suggestions,
                "coverage": critique.coverage
            },
            "iterations": iterations,
            "total_cases": len(cases),
            "final_iteration": self.iteration_count
        }
    
    def _generate(self, spec: dict[str, Any], existing: list[TestCase]) -> list[TestCase]:
        """Generate initial test cases from acceptance criteria."""
        cases: list[TestCase] = []
        ac_list = spec.get("acceptance_criteria", [])
        feature_id = spec["id"]
        case_counter = 1
        
        for ac in ac_list:
            ac_id = ac["id"]
            criteria_text = ac["criteria"]
            is_positive = ac.get("positive", True)
            expected_msg = ac.get("expected_message", "")
            
            # Positive test case
            if is_positive:
                case = TestCase(
                    id=f"{feature_id}-{case_counter}",
                    title=f"{ac_id}: {criteria_text}",
                    description=f"Verify {criteria_text}",
                    steps=self._generate_steps(criteria_text, True),
                    expected_result=self._generate_expected_result(criteria_text, True, expected_msg),
                    acceptance_criteria=ac_id,
                    category="positive",
                    risk_level="P0",
                    positive=True,
                    feature_id=feature_id
                )
                cases.append(case)
                case_counter += 1
            
            # Negative test case
            case = TestCase(
                id=f"{feature_id}-{case_counter}",
                title=f"{ac_id}: {criteria_text} (negative)",
                description=f"Verify rejection when {criteria_text.lower()}",
                steps=self._generate_steps(criteria_text, False),
                expected_result=self._generate_expected_result(criteria_text, False, expected_msg),
                acceptance_criteria=ac_id,
                category="negative",
                risk_level="P1",
                positive=False,
                feature_id=feature_id
            )
            cases.append(case)
            case_counter += 1
        
        return cases
    
    def _generate_steps(self, criteria: str, positive: bool) -> list[str]:
        """Generate test steps from criteria."""
        if "login" in criteria.lower():
            if positive:
                return [
                    "Open login page",
                    "Enter valid username",
                    "Enter valid password",
                    "Click login button",
                    "Verify successful login"
                ]
            else:
                return [
                    "Open login page",
                    "Enter username",
                    "Enter invalid password",
                    "Click login button",
                    "Verify error message is displayed"
                ]
        elif "promo" in criteria.lower() or "discount" in criteria.lower():
            if positive:
                return [
                    "Navigate to checkout",
                    "Enter valid promo code",
                    "Apply promo code",
                    "Verify discount is applied",
                    "Verify total is recalculated"
                ]
            else:
                return [
                    "Navigate to checkout",
                    "Enter promo code",
                    "Apply promo code",
                    "Verify error message"
                ]
        else:
            return ["Execute step 1", "Execute step 2", "Verify result"]
    
    def _generate_expected_result(self, criteria: str, positive: bool, expected_msg: str) -> str:
        """Generate expected result description."""
        if positive:
            return f"✓ {criteria}"
        else:
            if expected_msg:
                return f"✗ Error: {expected_msg}"
            return f"✗ Request rejected"
    
    def _critique(self, spec: dict[str, Any], cases: list[TestCase]) -> CritiqueResult:
        """Critique generated cases against requirements."""
        result = CritiqueResult()
        ac_list = spec.get("acceptance_criteria", [])
        ac_ids = {ac["id"] for ac in ac_list}
        
        # Check coverage
        covered_ac = {case.acceptance_criteria for case in cases}
        result.coverage = {ac_id: len([c for c in cases if c.acceptance_criteria == ac_id]) 
                          for ac_id in ac_ids}
        
        # Find uncovered ACs
        uncovered = ac_ids - covered_ac
        for ac_id in uncovered:
            ac = next((a for a in ac_list if a["id"] == ac_id), None)
            if ac:
                result.gaps.append(f"Missing coverage for {ac_id}: {ac['criteria']}")
        
        # Find gaps in categories
        for ac_id in covered_ac:
            ac_cases = [c for c in cases if c.acceptance_criteria == ac_id]
            categories_present = {c.category for c in ac_cases}
            
            if "negative" in [ac.get("positive", True) for ac in ac_list if ac["id"] == ac_id]:
                for missing_cat in ["boundary", "edge"]:
                    if missing_cat not in categories_present:
                        result.gaps.append(f"Missing {missing_cat} cases for {ac_id}")
        
        # Validate business rules
        business_rules = spec.get("business_rules", [])
        if business_rules and len(cases) > 0:
            result.suggestions.append(f"Consider adding {len(business_rules)} business rule test cases")
        
        return result
    
    def _repair(self, spec: dict[str, Any], existing: list[TestCase], 
                critique: CritiqueResult) -> list[TestCase]:
        """Generate new cases to repair gaps found in critique."""
        new_cases: list[TestCase] = []
        ac_list = spec.get("acceptance_criteria", [])
        feature_id = spec["id"]
        case_counter = len(existing) + 1
        
        # For each gap, generate specific boundary/edge cases
        for gap in critique.gaps[:5]:  # Limit to first 5 gaps
            # Extract AC ID from gap
            ac_id = None
            for ac in ac_list:
                if ac["id"] in gap:
                    ac_id = ac["id"]
                    break
            
            if ac_id:
                ac = next((a for a in ac_list if a["id"] == ac_id), None)
                if ac:
                    # Add boundary case
                    boundary_case = TestCase(
                        id=f"{feature_id}-{case_counter}",
                        title=f"{ac_id}: Boundary test - {ac['criteria']}",
                        description=f"Boundary testing for {ac['criteria']}",
                        steps=self._generate_boundary_steps(ac["criteria"]),
                        expected_result="Validate boundary behavior",
                        acceptance_criteria=ac_id,
                        category="boundary",
                        risk_level="P2",
                        positive=ac.get("positive", True),
                        feature_id=feature_id
                    )
                    new_cases.append(boundary_case)
                    case_counter += 1
                    
                    # Add edge case
                    edge_case = TestCase(
                        id=f"{feature_id}-{case_counter}",
                        title=f"{ac_id}: Edge case - {ac['criteria']}",
                        description=f"Edge case testing for {ac['criteria']}",
                        steps=self._generate_edge_steps(ac["criteria"]),
                        expected_result="Handle edge condition gracefully",
                        acceptance_criteria=ac_id,
                        category="edge",
                        risk_level="P3",
                        positive=ac.get("positive", True),
                        feature_id=feature_id
                    )
                    new_cases.append(edge_case)
                    case_counter += 1
        
        return new_cases
    
    def _generate_boundary_steps(self, criteria: str) -> list[str]:
        """Generate boundary test steps."""
        return [
            "Set input to boundary value",
            "Submit request",
            "Verify boundary is handled correctly",
            "Test just below boundary",
            "Test just above boundary"
        ]
    
    def _generate_edge_steps(self, criteria: str) -> list[str]:
        """Generate edge case test steps."""
        return [
            "Prepare edge case scenario",
            "Execute action with edge input",
            "Verify system handles edge case",
            "Check for error recovery",
            "Confirm state consistency"
        ]
    
    def write_outputs(self, result: dict[str, Any], out_dir: Path) -> None:
        """Write test cases to CSV, Gherkin, and JSON formats."""
        out_dir.mkdir(parents=True, exist_ok=True)
        feature_id = result["feature_id"].lower()
        
        # Write CSV
        csv_path = out_dir / f"test_cases_{feature_id}.csv"
        self._write_csv(result["cases"], csv_path)
        
        # Write Gherkin
        feature_path = out_dir / f"test_suite_{feature_id}.feature"
        self._write_gherkin(result, feature_path)
        
        # Write JSON coverage report
        coverage_path = out_dir / f"coverage_report_{feature_id}.json"
        self._write_coverage_report(result, coverage_path)
    
    def _write_csv(self, cases: list[TestCase], path: Path) -> None:
        """Write test cases to CSV."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "ID", "Title", "Description", "Steps", "Expected Result",
                "AC ID", "Category", "Risk Level", "Type"
            ])
            writer.writeheader()
            for case in cases:
                writer.writerow({
                    "ID": case.id,
                    "Title": case.title,
                    "Description": case.description,
                    "Steps": " → ".join(case.steps),
                    "Expected Result": case.expected_result,
                    "AC ID": case.acceptance_criteria,
                    "Category": case.category,
                    "Risk Level": case.risk_level,
                    "Type": "Positive" if case.positive else "Negative"
                })
    
    def _write_gherkin(self, result: dict[str, Any], path: Path) -> None:
        """Write test cases to Gherkin BDD format."""
        path.parent.mkdir(parents=True, exist_ok=True)
        feature_name = result["feature_name"]
        cases = result["cases"]
        
        content = f"Feature: {feature_name}\n"
        content += f"  Test cases generated from acceptance criteria\n\n"
        
        for case in cases[:12]:  # First 12 for brevity
            content += f"  Scenario: {case.title}\n"
            for step in case.steps:
                content += f"    Given {step}\n" if step == case.steps[0] else f"    And {step}\n"
            content += f"    Then {case.expected_result}\n\n"
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _write_coverage_report(self, result: dict[str, Any], path: Path) -> None:
        """Write coverage report."""
        path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "feature_id": result["feature_id"],
            "feature_name": result["feature_name"],
            "total_cases": result["total_cases"],
            "iterations": result["final_iteration"],
            "coverage": result["critique"]["coverage"],
            "gaps": result["critique"]["gaps"],
            "timestamp": datetime.now().isoformat()
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
