"""Tests for demo.py"""
import unittest
import json
import tempfile
from pathlib import Path

from agent import TestCaseAgent


class TestDemoExecution(unittest.TestCase):
    """Tests for demo.py functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = TestCaseAgent()
        self.specs_dir = Path(__file__).parent.parent / "specs"
    
    def test_load_specs(self):
        """Test that specs can be loaded."""
        if not self.specs_dir.exists():
            self.skipTest("specs directory not found")
        
        specs = {}
        for path in sorted(self.specs_dir.glob("feature_*.json")):
            spec = json.loads(path.read_text(encoding="utf-8"))
            specs[spec["id"].lower()] = spec
        
        self.assertGreater(len(specs), 0)
        self.assertIn("a", specs)
        self.assertIn("b", specs)
    
    def test_generate_both_suites(self):
        """Test generating both feature suites."""
        if not self.specs_dir.exists():
            self.skipTest("specs directory not found")
        
        specs = {}
        for path in sorted(self.specs_dir.glob("feature_*.json")):
            spec = json.loads(path.read_text(encoding="utf-8"))
            specs[spec["id"].lower()] = spec
        
        results = {}
        for feature_id, spec in specs.items():
            result = self.agent.run(spec)
            results[feature_id] = result
            
            # Verify result
            self.assertIn("cases", result)
            self.assertGreater(len(result["cases"]), 0)
        
        self.assertEqual(len(results), 2)
    
    def test_output_writing(self):
        """Test writing outputs for demo."""
        if not self.specs_dir.exists():
            self.skipTest("specs directory not found")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            
            specs = {}
            for path in sorted(self.specs_dir.glob("feature_*.json")):
                spec = json.loads(path.read_text(encoding="utf-8"))
                specs[spec["id"].lower()] = spec
            
            for feature_id, spec in specs.items():
                result = self.agent.run(spec)
                self.agent.write_outputs(result, out_dir)
            
            # Verify outputs
            self.assertTrue((out_dir / "test_cases_a.csv").exists())
            self.assertTrue((out_dir / "test_cases_b.csv").exists())
            self.assertTrue((out_dir / "test_suite_a.feature").exists())
            self.assertTrue((out_dir / "test_suite_b.feature").exists())


if __name__ == "__main__":
    unittest.main()
