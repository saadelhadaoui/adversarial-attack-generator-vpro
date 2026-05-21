import json
import os
from typing import Any


DEFAULT_POLICY_PATH = "data/chatbot_policy.json"


def load_chatbot_policy(path: str | None = None) -> dict[str, Any]:
    policy_path = path or os.getenv("CHATBOT_POLICY_PATH", DEFAULT_POLICY_PATH)
    if os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}
