import json
import os
from typing import Any


DEFAULT_POLICY_PATH = "data/evaluator_policy.json"


def load_evaluator_policy(path: str | None = None) -> dict[str, Any]:
    policy_path = path or os.getenv("EVALUATOR_POLICY_PATH", DEFAULT_POLICY_PATH)
    if os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {"controlled_markers": [], "decision_results": [], "default_result": {}}


def clamp_score(score: float) -> float:
    return max(0.0, min(1.0, float(score)))
