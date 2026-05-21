import json
import os
import re


DEFAULT_POLICY_PATH = "data/safe_text_policy.json"


def _load_policy() -> dict:
    path = os.getenv("SAFE_TEXT_POLICY_PATH", DEFAULT_POLICY_PATH)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {"safe_labels": {}, "default_label": "[redacted adversarial pattern]", "display_replacements": []}


def safe_pattern_label(key: str) -> str:
    policy = _load_policy()
    return policy.get("safe_labels", {}).get(str(key).lower(), policy.get("default_label", "[redacted adversarial pattern]"))


def sanitize_for_display(text: str) -> str:
    text = str(text or "")
    for replacement_rule in _load_policy().get("display_replacements", []):
        text = re.sub(replacement_rule.get("pattern", ""), replacement_rule.get("replacement", ""), text)
    return text
