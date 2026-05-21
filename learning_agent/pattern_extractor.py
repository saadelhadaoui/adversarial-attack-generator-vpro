import json
import os
from typing import Any


DEFAULT_POLICY_PATH = "data/learning_policy.json"


def load_learning_policy(path: str | None = None) -> dict[str, Any]:
    policy_path = path or os.getenv("LEARNING_POLICY_PATH", DEFAULT_POLICY_PATH)
    if os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {"pattern_rules": [], "family_default_patterns": {}, "confidence": 0.8}


def extract_pattern(input_text: str, family: str, policy: dict[str, Any] | None = None) -> str:
    policy = policy or load_learning_policy()
    text = (input_text or "").lower()
    for rule in policy.get("pattern_rules", []):
        if rule.get("family") != family:
            continue
        terms = [str(term).lower() for term in rule.get("match_any", [])]
        if terms and any(term in text for term in terms):
            return rule.get("pattern", f"{family}_pattern")
    return policy.get("family_default_patterns", {}).get(family, f"{family}_pattern")
