"""Script to generate outputs automatically."""
import json
from pathlib import Path
from agent import TestCaseAgent

ROOT = Path(__file__).resolve().parent
SPEC_DIR = ROOT / "specs"
OUT_DIR = ROOT / "outputs"

def generate_all():
    """Generate test suites for all features."""
    specs = {}
    for path in sorted(SPEC_DIR.glob("feature_*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        specs[spec["id"].lower()] = spec
    
    print("\nGenerating suites with generate -> critique -> repair...\n")
    
    for feature_id, spec in specs.items():
        result = TestCaseAgent().run(spec)
        TestCaseAgent().write_outputs(result, OUT_DIR)
        print(
            f"[{feature_id.upper()}] {spec['name']}: {len(result['cases'])} cases | "
            f"{len(result['iterations'])} iterations | "
            f"final gaps: {len(result['critique']['gaps'])}"
        )
    
    # Write summary
    summary_path = OUT_DIR / "coverage_summary.json"
    summary = {
        "total_features": len(specs),
        "features": list(specs.keys()),
        "generated_at": str(Path(__file__).resolve().parent / "outputs")
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✓ Outputs written to {OUT_DIR}")

if __name__ == "__main__":
    generate_all()
