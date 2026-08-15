from pathlib import Path
import json
from agent import TestCaseAgent

for name in ("feature_a.json", "feature_b.json"):
    spec=json.loads(Path("specs",name).read_text(encoding="utf-8"))
    result=TestCaseAgent().run(spec)
    print("\n===", spec["name"], "===")
    print("Cases:", len(result["cases"]))
    print("Iterations:", len(result["iterations"]))
    print("Remaining gaps:", result["critique"]["gaps"])
    for it in result["iterations"]:
        print(f"Iteration {it['iteration']}: {len(it['critique']['gaps'])} gaps")
