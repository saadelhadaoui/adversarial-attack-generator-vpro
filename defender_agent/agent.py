from typing import Any

from memory.structured_memory import StructuredMemory


class DefenderAgent:
    def __init__(self, memory: StructuredMemory | None = None, mode: str = "PROTECTION"):
        self.memory = memory or StructuredMemory()
        self.mode = mode

    def set_mode(self, mode: str) -> None:
        if mode in {"PROTECTION", "CONTROLLED_EXFILTRATION"}:
            self.mode = mode

    def analyze(self, input_text: str, learned_memory: dict[str, Any] | None = None) -> dict[str, Any]:
        text = (input_text or "").lower()
        threat_family = self._classify(text)
        retrieved_patterns = self._retrieve_patterns(text, threat_family)
        used_memory = bool(retrieved_patterns)
        matched_pattern = retrieved_patterns[0]["pattern_label"] if retrieved_patterns else ""

        if threat_family == "benign":
            action = "PASS"
            risk = 0.05
            reason = "Benign request passed."
        elif matched_pattern:
            action = "BLOCK"
            risk = 0.9
            reason = f"Matched learned pattern: {matched_pattern}"
        elif self.mode == "CONTROLLED_EXFILTRATION" and threat_family == "data_exfiltration":
            action = "ALLOW_WITH_MONITORING"
            risk = 0.75
            reason = "First-time data exfiltration pattern allowed for controlled learning."
        elif threat_family == "ambiguous_security":
            action = "REFORMULATE"
            risk = 0.45
            reason = "Security request is allowed with a defensive framing."
        else:
            action = "BLOCK"
            risk = 0.85
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
        if any(term in text for term in ["employee record", "internal employee", "api key", "secret", "confidential", "internal data"]):
            return "data_exfiltration"
        if "redacted" in text and any(term in text for term in ["data", "sensitive", "internal", "information"]):
            return "data_exfiltration"
        if any(term in text for term in ["prompt injection", "instruction hierarchy", "override", "ignore previous"]):
            return "prompt_injection"
        if any(term in text for term in ["jailbreak", "policy bypass", "bypass policy"]):
            return "jailbreak_attempt"
        if any(term in text for term in ["protect", "defend", "mitigate", "security", "prompt injection means"]):
            return "benign"
        return "benign"

    def _retrieve_patterns(self, text: str, threat_family: str) -> list[dict[str, Any]]:
        patterns = self.memory.search_patterns_by_family(threat_family) if threat_family != "benign" else []
        if not patterns:
            return []
        if threat_family == "data_exfiltration" and any(term in text for term in ["employee", "internal", "data", "record", "api", "key"]):
            return patterns[:5]
        if threat_family in {"prompt_injection", "jailbreak_attempt"}:
            return patterns[:5]
        return []
