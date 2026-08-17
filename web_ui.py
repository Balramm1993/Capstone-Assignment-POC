from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, render_template

from agent import TestCaseAgent

ROOT = Path(__file__).resolve().parent
SPEC_DIR = ROOT / "specs"
OUT_DIR = ROOT / "outputs"

app = Flask(__name__)


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


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5002)
