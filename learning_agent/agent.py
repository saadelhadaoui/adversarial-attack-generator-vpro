from typing import Any

from memory.structured_memory import StructuredMemory


class LearningAgent:
    def __init__(self, memory: StructuredMemory | None = None):
        self.memory = memory or StructuredMemory()

    def learn(
        self,
        input_text: str,
        defender_decision: Any,
        evaluation_result: Any,
        attack_attempt: Any | None = None,
        learned_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        defender = defender_decision.to_dict() if hasattr(defender_decision, "to_dict") else dict(defender_decision)
        evaluator = evaluation_result.to_dict() if hasattr(evaluation_result, "to_dict") else dict(evaluation_result)
        family = defender.get("threat_family", "unknown")
        action = defender.get("action", "PASS")
        should_learn = bool(evaluator.get("attack_succeeded")) or action == "ALLOW_WITH_MONITORING"

        if not should_learn or family == "benign":
            return {
                "learner_update": "No learning trigger.",
                "learned_pattern": "",
                "generated_rule": "",
                "memory_updated": False,
                "confidence": 0.0,
            }

        pattern = self._pattern_for(input_text, family)
        rule = self._rule_for(family, pattern)
        self.memory.save_pattern(pattern, family, 0.86, "learning_agent")
        self.memory.save_rule(rule, family, pattern, 0.86)
        return {
            "learner_update": f"Stored defensive pattern for {family}.",
            "learned_pattern": pattern,
            "generated_rule": rule,
            "memory_updated": True,
            "confidence": 0.86,
        }

    def _pattern_for(self, input_text: str, family: str) -> str:
        text = (input_text or "").lower()
        if family == "data_exfiltration" and "employee" in text:
            return "employee_data_exfiltration_pattern"
        if family == "data_exfiltration" and ("api" in text or "key" in text):
            return "api_key_exfiltration_pattern"
        if family == "prompt_injection":
            return "instruction_override_pattern"
        if family == "jailbreak_attempt":
            return "policy_bypass_pattern"
        return f"{family}_pattern"

    def _rule_for(self, family: str, pattern: str) -> str:
        if family == "data_exfiltration":
            return f"Block future requests matching {pattern} before retrieving company data."
        return f"Block future requests matching {pattern}."
