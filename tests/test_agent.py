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

    def cases(self, feature):
        return TestCaseAgent().run(self.load(feature))["cases"]

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

    def test_login_has_explicit_password_boundaries(self):
        cases = self.cases("feature_a.json")
        text = " ".join(f"{c.title} {c.steps} {c.expected_result}" for c in cases if c.acceptance_criteria == "AC1")
        for value in ("7", "8", "64", "65"):
            self.assertIn(value, text)
        self.assertIn("8 and 64", text)

    def test_login_lockout_boundaries_are_explicit(self):
        cases = self.cases("feature_a.json")
        text = " ".join(f"{c.title} {c.steps} {c.expected_result}" for c in cases if c.acceptance_criteria == "AC6")
        for token in ("4", "5", "15", "30"):
            self.assertIn(token, text)

    def test_login_session_and_request_suppression_are_explicit(self):
        cases = self.cases("feature_a.json")
        all_text = " ".join(f"{c.title} {c.steps} {c.expected_result}" for c in cases)
        self.assertIn("no authentication request", all_text.lower())
        self.assertIn("23:59:59", all_text)
        self.assertIn("24:00:00", all_text)

    def test_promo_customer_scope_and_discount_cap_are_explicit(self):
        cases = self.cases("feature_b.json")
        ac7 = " ".join(f"{c.title} {c.steps} {c.expected_result}" for c in cases if c.acceptance_criteria == "AC7")
        ac8 = " ".join(f"{c.title} {c.steps} {c.expected_result}" for c in cases if c.acceptance_criteria == "AC8")
        self.assertIn("Customer B", ac7)
        for value in ("₹150", "₹200", "₹201"):
            self.assertIn(value, ac8)

    def test_promo_replacement_tax_and_cart_recalculation_are_explicit(self):
        cases = self.cases("feature_b.json")
        ac9 = " ".join(f"{c.title} {c.steps} {c.expected_result}" for c in cases if c.acceptance_criteria == "AC9")
        ac12 = " ".join(f"{c.title} {c.steps} {c.expected_result}" for c in cases if c.acceptance_criteria == "AC12")
        all_text = " ".join(f"{c.title} {c.steps} {c.expected_result}" for c in cases)
        self.assertIn("Cancel", ac9)
        self.assertIn("Only the new", ac9)
        self.assertIn("₹1000", ac12)
        self.assertIn("₹999", ac12)
        self.assertIn("shipping", all_text.lower())
        self.assertIn("tax", all_text.lower())

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
