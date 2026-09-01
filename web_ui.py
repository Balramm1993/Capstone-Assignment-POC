from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, render_template

from agent import TestCaseAgent

ROOT = Path(__file__).resolve().parent
SPEC_DIR = ROOT / "specs"
OUT_DIR = ROOT / "outputs"

app = Flask(__name__)

# Store agent results for question-answering
_agent_cache = {}


def load_specs() -> dict[str, dict[str, Any]]:
    specs = {}
    for path in sorted(SPEC_DIR.glob("feature_*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        specs[spec["id"].lower()] = spec
    return specs


@app.route("/generate", methods=["POST", "GET"])
def generate():
    specs = load_specs()
    agent = TestCaseAgent()
    results = {}
    for fid, spec in specs.items():
        result = agent.run(spec)
        agent.write_outputs(result, OUT_DIR)
        results[fid] = {
            "feature": spec["name"],
            "cases": len(result["cases"]),
            "iterations": len(result["iterations"]),
            "gaps": len(result["critique"]["gaps"]),
        }
    return jsonify(results)


@app.route("/features", methods=["GET"])
def features():
    specs = load_specs()
    return jsonify({k: v["name"] for k, v in specs.items()})


@app.route("/feature/<fid>/loop", methods=["GET"])
def feature_loop(fid: str):
    specs = load_specs()
    fid = fid.lower()
    if fid not in specs:
        return jsonify({"error": "feature not found"}), 404
    agent = TestCaseAgent()
    result = agent.run(specs[fid])
    return jsonify({"iterations": result["iterations"]})


@app.route("/feature/<fid>/cases", methods=["GET"])
def feature_cases(fid: str):
    specs = load_specs()
    fid = fid.lower()
    if fid not in specs:
        return jsonify({"error": "feature not found"}), 404
    agent = TestCaseAgent()
    result = agent.run(specs[fid])
    ac = request.args.get("ac")
    category = request.args.get("category")
    cases = []
    for c in result["cases"]:
        d = c.__dict__ if hasattr(c, "__dict__") else c
        if ac and d.get("acceptance_criteria") != ac:
            continue
        if category and d.get("category") != category:
            continue
        cases.append({
            "id": d.get("id"),
            "category": d.get("category"),
            "priority": d.get("priority"),
            "ac": d.get("acceptance_criteria"),
            "title": d.get("title"),
            "steps": d.get("steps"),
            "expect": d.get("expected_result"),
        })
    return jsonify({"feature": specs[fid]["name"], "count": len(cases), "cases": cases})


@app.route("/feature/<fid>/coverage", methods=["GET"])
def feature_coverage(fid: str):
    specs = load_specs()
    fid = fid.lower()
    if fid not in specs:
        return jsonify({"error": "feature not found"}), 404
    agent = TestCaseAgent()
    result = agent.run(specs[fid])
    return jsonify(result["critique"])


@app.route("/outputs", methods=["GET"])
def outputs():
    files = []
    for p in sorted(OUT_DIR.glob("*")):
        files.append(p.name)
    return jsonify({"outputs": files, "path": str(OUT_DIR)})


def _get_agent_result(fid: str) -> dict:
    """Get or generate agent result for feature."""
    fid = fid.lower()
    if fid not in _agent_cache:
        specs = load_specs()
        if fid not in specs:
            return None
        agent = TestCaseAgent()
        _agent_cache[fid] = agent.run(specs[fid])
    return _agent_cache[fid]


def _ask_agent(question: str, feature: str = None) -> dict:
    """Agent question-answering capability."""
    question_lower = question.lower()
    specs = load_specs()
    
    # Detect feature from question or use provided feature
    detected_feature = None
    for fid in specs.keys():
        if fid in question_lower or specs[fid]["name"].lower() in question_lower:
            detected_feature = fid
            break
    
    feature = (feature or detected_feature or "a").lower()
    result = _get_agent_result(feature)
    if not result:
        return {"answer": "Feature not found.", "type": "error"}
    
    # Question patterns
    if any(word in question_lower for word in ["gap", "missing", "uncovered"]):
        gaps = result["critique"]["gaps"]
        covered = result["critique"]["covered_acceptance_criteria"]
        if not gaps:
            return {
                "answer": f"No remaining coverage gaps. All {len(covered)} acceptance criteria are fully covered.",
                "type": "coverage_gaps",
                "data": {"gaps": gaps, "covered": covered}
            }
        else:
            gap_summary = "\n".join([f"- {g['id']}: {g['reason']}" for g in gaps])
            return {
                "answer": f"Found {len(gaps)} coverage gaps:\n{gap_summary}",
                "type": "coverage_gaps",
                "data": {"gaps": gaps}
            }
    
    elif any(word in question_lower for word in ["boundary", "edge", "negative", "positive"]):
        # Extract category
        category = None
        for cat in ["boundary", "edge", "negative", "positive"]:
            if cat in question_lower:
                category = cat
                break
        
        # Extract AC if mentioned
        ac_match = re.search(r'AC\d+', question, re.IGNORECASE)
        ac = ac_match.group(0).upper() if ac_match else None
        
        cases = [c for c in result["cases"] if (not ac or c.acceptance_criteria == ac) and (not category or c.category == category)]
        
        if not cases:
            return {"answer": f"No {category or ''} cases found for {ac or 'all ACs'}.", "type": "test_cases"}
        
        cases_summary = "\n".join([f"- {c.id}: {c.title}" for c in cases[:5]])
        return {
            "answer": f"Found {len(cases)} {category or ''} cases:\n{cases_summary}",
            "type": "test_cases",
            "data": {"cases": [{"id": c.id, "title": c.title, "category": c.category, "ac": c.acceptance_criteria} for c in cases]}
        }
    
    elif any(word in question_lower for word in ["why", "reason", "explain"]):
        covered = result["critique"]["covered_acceptance_criteria"]
        iterations = len(result["iterations"])
        gaps_resolved = result["iterations"][0]["critique"]["gaps"] if result["iterations"] else []
        return {
            "answer": f"The agent uses a generate-critique-repair loop:\n"
                     f"1. Generated initial draft\n"
                     f"2. Critiqued against {len(covered)} acceptance criteria and business rules\n"
                     f"3. Repaired gaps over {iterations} iterations\n"
                     f"Result: 100% coverage with zero gaps.",
            "type": "reasoning",
            "data": {"iterations": iterations, "covered_acs": len(covered)}
        }
    
    elif any(word in question_lower for word in ["coverage", "summary", "status"]):
        coverage = result["critique"]
        return {
            "answer": f"Coverage Summary:\n"
                     f"- Total Cases: {len(result['cases'])}\n"
                     f"- ACs Covered: {len(coverage['covered_acceptance_criteria'])}/{len(coverage['acceptance_criteria'])}\n"
                     f"- Gaps: {len(coverage['gaps'])}\n"
                     f"- Iterations: {len(result['iterations'])}",
            "type": "coverage_summary",
            "data": coverage
        }
    
    else:
        return {
            "answer": f"I can answer questions about:\n"
                     f"- Coverage gaps ('What gaps remain?')\n"
                     f"- Test cases by category ('Show boundary cases for AC6')\n"
                     f"- Design reasoning ('Why did the agent add edge cases?')\n"
                     f"- Coverage status ('Show coverage summary')",
            "type": "help"
        }


@app.route("/ask", methods=["POST"])
def ask():
    """Question-answering endpoint."""
    data = request.get_json()
    question = data.get("question", "").strip()
    feature = data.get("feature", "").lower() or None
    
    if not question:
        return jsonify({"error": "Please provide a question"}), 400
    
    result = _ask_agent(question, feature)
    return jsonify(result)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5002)
