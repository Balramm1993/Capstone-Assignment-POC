import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from agent import CATEGORIES, TestCaseAgent, generate_all

class AgentTests(unittest.TestCase):
    def load(self, feature):
        return json.loads((ROOT / "specs" / feature).read_text(encoding="utf-8"))

    def test_both_specs_have_zero_final_gaps(self):
        for feature in ("feature_a.json", "feature_b.json"):
            result = TestCaseAgent().run(self.load(feature))
            self.assertFalse(result["critique"]["gaps"], result["critique"]["gaps"])
            self.assertGreaterEqual(len(result["cases"]), 36)

    def test_every_ac_has_all_required_categories(self):
        for feature in ("feature_a.json", "feature_b.json"):
            result = TestCaseAgent().run(self.load(feature))
            for ac in result["critique"]["acceptance_criteria"]:
                self.assertEqual(set(ac["categories_present"]), set(CATEGORIES), ac)

    def test_exact_required_messages_are_asserted(self):
        for feature in ("feature_a.json", "feature_b.json"):
            result = TestCaseAgent().run(self.load(feature))
            messages = result["critique"]["required_messages"]
            self.assertTrue(messages)
            self.assertTrue(all(m["covered"] for m in messages), messages)

    def test_business_rules_are_covered_for_promo(self):
        result = TestCaseAgent().run(self.load("feature_b.json"))
        self.assertTrue(result["critique"]["business_rules"])
        self.assertTrue(all(r["covered"] for r in result["critique"]["business_rules"]))

    def test_agent_has_real_generate_critique_repair_iterations(self):
        result = TestCaseAgent(max_iterations=4).run(self.load("feature_a.json"))
        self.assertGreaterEqual(len(result["iterations"]), 2)
        self.assertTrue(result["iterations"][0]["critique"]["gaps"])
        self.assertFalse(result["critique"]["gaps"])
        self.assertGreater(result["iterations"][-1]["case_count"], result["iterations"][0]["case_count"])

    def test_outputs_are_importable_and_requirement_traceable(self):
        out = ROOT / "outputs" / "_test"
        summary = generate_all(ROOT / "specs", out)
        self.assertEqual(len(summary["features"]), 2)
        rows = (out / "all_test_cases.csv").read_text(encoding="utf-8-sig").splitlines()
        self.assertGreater(len(rows), 70)
        self.assertIn("acceptance_criteria", rows[0])
        self.assertIn("rule_trace", rows[0])

if __name__ == "__main__":
    unittest.main()
