import json
import unittest
from pathlib import Path
from agent import TestCaseAgent

ROOT=Path(__file__).parents[1]

class AgentTests(unittest.TestCase):
    def test_both_specs_have_full_ac_coverage(self):
        for spec_path in (ROOT/"specs").glob("feature_*.json"):
            spec=json.loads(spec_path.read_text(encoding="utf-8"))
            result=TestCaseAgent().run(spec)
            self.assertFalse(result["critique"]["gaps"], result["critique"]["gaps"])
            self.assertTrue(result["cases"])

    def test_categories_are_valid_and_traceable(self):
        for spec_path in (ROOT/"specs").glob("feature_*.json"):
            spec=json.loads(spec_path.read_text(encoding="utf-8"))
            acs={x["id"] for x in spec["acceptance_criteria"]}
            result=TestCaseAgent().run(spec)
            for c in result["cases"]:
                self.assertIn(c.category, {"positive","negative","boundary","edge"})
                self.assertTrue(all(x.strip() in acs for x in c.acceptance_criteria.split(",")))

    def test_agent_uses_generate_critique_repair_loop(self):
        spec=json.loads((ROOT/"specs/feature_a.json").read_text(encoding="utf-8"))
        result=TestCaseAgent(max_iterations=3).run(spec)
        self.assertGreaterEqual(len(result["iterations"]), 2)
        self.assertTrue(result["iterations"][0]["critique"]["gaps"])
        self.assertFalse(result["critique"]["gaps"])

if __name__=="__main__":
    unittest.main()
