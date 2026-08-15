"""
Test Case Generator Agent
-------------------------
Generates structured manual test cases and Gherkin scenarios from JSON feature specifications.

The implementation is intentionally deterministic and can run without an LLM/API key.  It uses
small, composable generators so the output is easy to inspect, test, and extend.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass
class TestCase:
    test_case_id: str
    feature: str
    scenario: str
    test_type: str
    priority: str
    preconditions: str
    steps: str
    expected_result: str
    source_requirement: str


class TestCaseGenerator:
    """Generate positive, negative, boundary, and validation cases from feature JSON."""

    def __init__(self, output_dir: str | Path = "outputs") -> None:
        self.output_dir = Path(output_dir)

    @staticmethod
    def _slug(value: str) -> str:
        value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
        return value or "FEATURE"

    @staticmethod
    def _normalise_steps(steps: Iterable[str]) -> str:
        return "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))

    def _generate_cases_for_feature(self, feature: dict[str, Any], feature_index: int) -> list[TestCase]:
        name = str(feature.get("name", f"Feature {feature_index}"))
        description = str(feature.get("description", ""))
        requirements = feature.get("requirements", [])
        if isinstance(requirements, str):
            requirements = [requirements]

        cases: list[TestCase] = []
        prefix = f"TC-{feature_index:02d}"
        for req_index, req in enumerate(requirements, 1):
            req_text = str(req)
            source = req_text
            base_id = f"{prefix}-{req_index:02d}"
            cases.append(
                TestCase(
                    test_case_id=f"{base_id}-POS",
                    feature=name,
                    scenario=f"Verify {req_text}",
                    test_type="Positive",
                    priority="High",
                    preconditions=description or "Application is available and the required test data is prepared.",
                    steps=self._normalise_steps([
                        "Open the application/feature.",
                        f"Perform the actions required to satisfy: {req_text}",
                        "Submit or complete the operation.",
                    ]),
                    expected_result=f"The system successfully satisfies the requirement: {req_text}.",
                    source_requirement=source,
                )
            )
            cases.append(
                TestCase(
                    test_case_id=f"{base_id}-NEG",
                    feature=name,
                    scenario=f"Reject invalid input for {req_text}",
                    test_type="Negative",
                    priority="High",
                    preconditions=description or "Application is available.",
                    steps=self._normalise_steps([
                        "Open the application/feature.",
                        f"Attempt the operation for: {req_text} using invalid, missing, or unauthorized data.",
                        "Submit or complete the operation.",
                    ]),
                    expected_result="The system rejects the invalid operation and displays a clear validation or authorization message without corrupting data.",
                    source_requirement=source,
                )
            )
            cases.append(
                TestCase(
                    test_case_id=f"{base_id}-BND",
                    feature=name,
                    scenario=f"Verify boundary conditions for {req_text}",
                    test_type="Boundary",
                    priority="Medium",
                    preconditions=description or "Application is available and boundary values are known.",
                    steps=self._normalise_steps([
                        "Open the application/feature.",
                        f"Execute: {req_text} with minimum, maximum, empty, and just-outside-boundary values as applicable.",
                        "Submit or complete the operation.",
                    ]),
                    expected_result="Boundary values accepted by the specification succeed; out-of-range values are rejected with appropriate validation feedback.",
                    source_requirement=source,
                )
            )

        if not cases:
            cases.append(
                TestCase(
                    test_case_id=f"{prefix}-01-POS",
                    feature=name,
                    scenario=f"Verify {name}",
                    test_type="Positive",
                    priority="Medium",
                    preconditions=description or "Application is available.",
                    steps=self._normalise_steps(["Open the feature.", "Execute the documented happy path.", "Complete the operation."]),
                    expected_result="The feature completes successfully and produces the documented result.",
                    source_requirement=description,
                )
            )
        return cases

    def generate(self, specs: list[dict[str, Any]]) -> list[TestCase]:
        cases: list[TestCase] = []
        for index, feature in enumerate(specs, 1):
            cases.extend(self._generate_cases_for_feature(feature, index))
        return cases

    @staticmethod
    def to_gherkin(cases: list[TestCase]) -> str:
        lines = ["Feature: Generated test suite", ""]
        for case in cases:
            lines.extend([
                f"  # {case.test_case_id} | {case.test_type} | {case.priority}",
                f"  Scenario: {case.scenario}",
                "    Given the application is available",
                "    When the test steps are executed",
                f"    And the requirement is exercised: {case.source_requirement}",
                f"    Then {case.expected_result}",
                "",
            ])
        return "\n".join(lines).rstrip() + "\n"

    def write_outputs(self, cases: list[TestCase]) -> dict[str, Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        csv_path = self.output_dir / "test_cases.csv"
        feature_path = self.output_dir / "test_suite.feature"
        fields = list(asdict(cases[0]).keys()) if cases else [f.name for f in TestCase.__dataclass_fields__.values()]
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(asdict(case) for case in cases)
        feature_path.write_text(self.to_gherkin(cases), encoding="utf-8")
        return {"csv": csv_path, "feature": feature_path}


def load_specs(spec_dir: str | Path) -> list[dict[str, Any]]:
    path = Path(spec_dir)
    specs: list[dict[str, Any]] = []
    for file in sorted(path.glob("*.json")):
        data = json.loads(file.read_text(encoding="utf-8"))
        if isinstance(data, list):
            specs.extend(data)
        else:
            specs.append(data)
    return specs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate test cases from JSON specifications")
    parser.add_argument("--specs", default="specs", help="Directory containing feature JSON files")
    parser.add_argument("--output", default="outputs", help="Directory for generated artifacts")
    args = parser.parse_args()
    generator = TestCaseGenerator(args.output)
    specs = load_specs(args.specs)
    cases = generator.generate(specs)
    outputs = generator.write_outputs(cases)
    print(f"Generated {len(cases)} test cases")
    for kind, path in outputs.items():
        print(f"{kind}: {path}")


if __name__ == "__main__":
    main()
