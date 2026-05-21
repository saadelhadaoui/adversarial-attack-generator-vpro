import json
import os
from typing import Any

from memory.structured_memory import StructuredMemory


DEFAULT_POLICY_PATH = "data/defender_policy.json"


def _default_policy() -> dict[str, Any]:
    return {
        "modes": ["PROTECTION", "CONTROLLED_EXFILTRATION"],
        "default_mode": "PROTECTION",
        "controlled_mode": "CONTROLLED_EXFILTRATION",
        "default_family": "benign",
        "benign_family": "benign",
        "controlled_monitor_families": ["data_exfiltration", "prompt_injection", "jailbreak_attempt"],
        "risk_scores": {
            "pass": 0.05,
            "matched_pattern": 0.9,
            "controlled_monitor": 0.75,
            "reformulate": 0.45,
            "block": 0.85,
        },
        "actions": {
            "benign": "PASS",
            "matched_pattern": "BLOCK",
            "controlled_monitor": "ALLOW_WITH_MONITORING",
            "ambiguous_security": "REFORMULATE",
            "default_threat": "BLOCK",
        },
        "classification_rules": [],
        "pattern_match_terms": {},
    }


class DefenderAgent:
    def __init__(
        self,
        memory: StructuredMemory | None = None,
        mode: str | None = None,
        policy_path: str | None = None,
    ):
        self.memory = memory or StructuredMemory()
        self.policy_path = policy_path or os.getenv("DEFENDER_POLICY_PATH", DEFAULT_POLICY_PATH)
        self.policy = self._load_policy(self.policy_path)
        self.mode = mode or self.policy.get("default_mode", "")

    def _load_policy(self, path: str) -> dict[str, Any]:
        policy = _default_policy()
        if not os.path.exists(path):
            return policy
        try:
            with open(path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
            if isinstance(loaded, dict):
                policy.update(loaded)
        except Exception:
            return policy
        return policy

    def set_mode(self, mode: str) -> None:
        if mode in set(self.policy.get("modes", [])):
            self.mode = mode

    def analyze(self, input_text: str, learned_memory: dict[str, Any] | None = None) -> dict[str, Any]:
        text = (input_text or "").lower()
        threat_family = self._classify(text)
        retrieved_patterns = self._retrieve_patterns(text, threat_family)
        used_memory = bool(retrieved_patterns)
        matched_pattern = retrieved_patterns[0]["pattern_label"] if retrieved_patterns else ""

        if threat_family == "benign":
            action = self.policy["actions"]["benign"]
            risk = self.policy["risk_scores"]["pass"]
            reason = "Benign request passed."
        elif matched_pattern:
            action = self.policy["actions"]["matched_pattern"]
            risk = self.policy["risk_scores"]["matched_pattern"]
            reason = f"Matched learned pattern: {matched_pattern}"
        elif self.mode == self.policy.get("controlled_mode", "") and threat_family in set(
            self.policy.get("controlled_monitor_families", [])
        ):
            action = self.policy["actions"]["controlled_monitor"]
            risk = self.policy["risk_scores"]["controlled_monitor"]
            reason = f"First-time {threat_family} pattern allowed for controlled learning."
        elif threat_family == "ambiguous_security":
            action = self.policy["actions"]["ambiguous_security"]
            risk = self.policy["risk_scores"]["reformulate"]
            reason = "Security request is allowed with a defensive framing."
        else:
            action = self.policy["actions"]["default_threat"]
            risk = self.policy["risk_scores"]["block"]
            reason = f"{threat_family} blocked in {self.mode} mode."

        return {
            "action": action,
            "risk_score": risk,
            "threat_family": threat_family,
            "reason": reason,
            "matched_pattern": matched_pattern,
            "used_memory": used_memory,
            "rag_used": used_memory,
        }

    def _classify(self, text: str) -> str:
        for rule in self.policy.get("classification_rules", []):
            if self._rule_matches(rule, text):
                return rule.get("family", self.policy.get("default_family", "benign"))
        return self.policy.get("default_family", "benign")

    def _rule_matches(self, rule: dict[str, Any], text: str) -> bool:
        match_all = [str(term).lower() for term in rule.get("match_all", [])]
        match_any = [str(term).lower() for term in rule.get("match_any", [])]
        if match_all and not all(term in text for term in match_all):
            return False
        if match_any and not any(term in text for term in match_any):
            return False
        return bool(match_all or match_any)

    def _retrieve_patterns(self, text: str, threat_family: str) -> list[dict[str, Any]]:
        patterns = self.memory.search_patterns_by_family(threat_family) if threat_family != "benign" else []
        if not patterns:
            return []
        matched = [pattern for pattern in patterns if self._pattern_matches_text(pattern.get("pattern_label", ""), text)]
        return matched[:5]

    def _pattern_matches_text(self, pattern_label: str, text: str) -> bool:
        terms = self.policy.get("pattern_match_terms", {}).get(pattern_label, [])
        return bool(terms and any(term in text for term in terms))
