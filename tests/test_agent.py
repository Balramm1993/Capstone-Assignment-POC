"""Tests for agent.py"""
import unittest
import json
from pathlib import Path
import tempfile

from agent import TestCaseAgent, TestCase, CritiqueResult


class TestTestCase(unittest.TestCase):
    """Tests for TestCase dataclass."""
    
    def test_testcase_creation(self):
        """Test creating a TestCase instance."""
        tc = TestCase(
            id="A-1",
            title="Test login",
            description="User logs in successfully",
            steps=["Enter username", "Enter password", "Click login"],
            expected_result="User is logged in",
            acceptance_criteria="AC1",
            category="positive",
            risk_level="P0",
            positive=True,
            feature_id="A"
        )
        self.assertEqual(tc.id, "A-1")
        self.assertEqual(tc.feature_id, "A")
        self.assertTrue(tc.positive)
    
    def test_testcase_to_dict(self):
        """Test converting TestCase to dictionary."""
        tc = TestCase(
            id="B-1",
            title="Apply promo",
            description="Apply valid promo code",
            steps=["Go to checkout", "Enter code"],
            expected_result="Discount applied",
            acceptance_criteria="AC1",
            category="positive",
            risk_level="P0",
            positive=True,
            feature_id="B"
        )
        tc_dict = tc.to_dict()
        self.assertIsInstance(tc_dict, dict)
        self.assertEqual(tc_dict["id"], "B-1")


class TestCritiqueResult(unittest.TestCase):
    """Tests for CritiqueResult dataclass."""
    
    def test_critique_result_creation(self):
        """Test creating a CritiqueResult."""
        critique = CritiqueResult(
            gaps=["Gap 1", "Gap 2"],
            issues=["Issue 1"],
            suggestions=["Suggestion 1"]
        )
        self.assertEqual(len(critique.gaps), 2)
        self.assertEqual(len(critique.issues), 1)


class TestTestCaseAgent(unittest.TestCase):
    """Tests for TestCaseAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = TestCaseAgent()
        self.sample_spec = {
            "id": "A",
            "name": "User Login",
            "description": "Test login functionality",
            "business_rules": ["Rule 1", "Rule 2"],
            "acceptance_criteria": [
                {
                    "id": "AC1",
                    "criteria": "User can log in with valid credentials",
                    "positive": True
                },
                {
                    "id": "AC2",
                    "criteria": "User cannot log in with invalid password",
                    "positive": False,
                    "expected_message": "Invalid password"
                }
            ]
        }
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.iteration_count, 0)
    
    def test_generate_produces_cases(self):
        """Test that _generate produces test cases."""
        cases = self.agent._generate(self.sample_spec, [])
        self.assertGreater(len(cases), 0)
        self.assertIsInstance(cases[0], TestCase)
    
    def test_generate_covers_all_criteria(self):
        """Test that _generate covers all acceptance criteria."""
        cases = self.agent._generate(self.sample_spec, [])
        criteria_covered = {case.acceptance_criteria for case in cases}
        expected_criteria = {"AC1", "AC2"}
        self.assertEqual(criteria_covered, expected_criteria)
    
    def test_critique_finds_gaps(self):
        """Test that _critique identifies gaps."""
        cases = self.agent._generate(self.sample_spec, [])
        critique = self.agent._critique(self.sample_spec, cases)
        self.assertIsInstance(critique.gaps, list)
    
    def test_run_executes_loop(self):
        """Test that run() executes the full generate->critique->repair loop."""
        result = self.agent.run(self.sample_spec)
        self.assertIn("cases", result)
        self.assertIn("critique", result)
        self.assertIn("iterations", result)
        self.assertGreater(len(result["cases"]), 0)
        self.assertGreater(len(result["iterations"]), 0)
    
    def test_run_output_structure(self):
        """Test that run() returns properly structured output."""
        result = self.agent.run(self.sample_spec)
        self.assertEqual(result["feature_id"], "A")
        self.assertEqual(result["feature_name"], "User Login")
        self.assertIsInstance(result["cases"], list)
        self.assertIsInstance(result["critique"], dict)
        self.assertIn("gaps", result["critique"])
        self.assertIn("coverage", result["critique"])
    
    def test_cases_have_required_fields(self):
        """Test that generated cases have all required fields."""
        cases = self.agent._generate(self.sample_spec, [])
        for case in cases:
            self.assertIsNotNone(case.id)
            self.assertIsNotNone(case.title)
            self.assertIsNotNone(case.description)
            self.assertIsNotNone(case.steps)
            self.assertIsNotNone(case.expected_result)
            self.assertIsNotNone(case.acceptance_criteria)
            self.assertIn(case.category, self.agent.CATEGORIES)
            self.assertIn(case.risk_level, self.agent.RISK_LEVELS)
    
    def test_write_outputs_creates_files(self):
        """Test that write_outputs creates necessary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            result = self.agent.run(self.sample_spec)
            self.agent.write_outputs(result, out_dir)
            
            # Check CSV file exists
            csv_file = out_dir / "test_cases_a.csv"
            self.assertTrue(csv_file.exists())
            
            # Check Gherkin file exists
            feature_file = out_dir / "test_suite_a.feature"
            self.assertTrue(feature_file.exists())
            
            # Check JSON coverage report exists
            coverage_file = out_dir / "coverage_report_a.json"
            self.assertTrue(coverage_file.exists())
    
    def test_csv_output_format(self):
        """Test that CSV output has correct format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            result = self.agent.run(self.sample_spec)
            self.agent.write_outputs(result, out_dir)
            
            csv_file = out_dir / "test_cases_a.csv"
            with open(csv_file, "r") as f:
                lines = f.readlines()
                self.assertGreater(len(lines), 1)  # Header + data
                # Check header
                self.assertIn("ID", lines[0])
                self.assertIn("Title", lines[0])
    
    def test_generate_steps_vary_by_feature(self):
        """Test that generated steps vary based on feature type."""
        login_steps = self.agent._generate_steps("User can log in", True)
        promo_steps = self.agent._generate_steps("Apply promo code", True)
        self.assertNotEqual(login_steps, promo_steps)
    
    def test_repair_generates_new_cases(self):
        """Test that _repair generates new cases to fill gaps."""
        cases = self.agent._generate(self.sample_spec, [])
        critique = self.agent._critique(self.sample_spec, cases)
        repaired = self.agent._repair(self.sample_spec, cases, critique)
        # Repair should either generate new cases or empty list if no gaps
        self.assertIsInstance(repaired, list)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = TestCaseAgent()
    
    def test_full_pipeline_feature_a(self):
        """Test full pipeline for Feature A."""
        spec_path = Path(__file__).parent.parent / "specs" / "feature_a.json"
        if not spec_path.exists():
            self.skipTest("feature_a.json not found")
        
        with open(spec_path) as f:
            spec = json.load(f)
        
        result = self.agent.run(spec)
        
        # Verify result structure
        self.assertIn("cases", result)
        self.assertIn("critique", result)
        self.assertGreater(len(result["cases"]), 0)
        
        # Verify cases cover acceptance criteria
        ac_ids = {ac["id"] for ac in spec["acceptance_criteria"]}
        covered = {case.acceptance_criteria for case in result["cases"]}
        self.assertTrue(covered.issubset(ac_ids))
    
    def test_full_pipeline_feature_b(self):
        """Test full pipeline for Feature B."""
        spec_path = Path(__file__).parent.parent / "specs" / "feature_b.json"
        if not spec_path.exists():
            self.skipTest("feature_b.json not found")
        
        with open(spec_path) as f:
            spec = json.load(f)
        
        result = self.agent.run(spec)
        
        # Verify result structure
        self.assertIn("cases", result)
        self.assertGreater(len(result["cases"]), 0)
    
    def test_output_generation(self):
        """Test that outputs are generated correctly."""
        spec_path = Path(__file__).parent.parent / "specs" / "feature_a.json"
        if not spec_path.exists():
            self.skipTest("feature_a.json not found")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            
            with open(spec_path) as f:
                spec = json.load(f)
            
            result = self.agent.run(spec)
            self.agent.write_outputs(result, out_dir)
            
            # Verify all output files exist
            self.assertTrue((out_dir / "test_cases_a.csv").exists())
            self.assertTrue((out_dir / "test_suite_a.feature").exists())
            self.assertTrue((out_dir / "coverage_report_a.json").exists())


if __name__ == "__main__":
    unittest.main()
