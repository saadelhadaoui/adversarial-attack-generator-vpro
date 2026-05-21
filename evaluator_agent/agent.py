from typing import Any

from evaluator_agent.scoring import clamp_score, load_evaluator_policy
from memory.company_data_store import CompanyDataStore


class EvaluatorAgent:
    def __init__(self, policy_path: str | None = None):
        self.company_data = CompanyDataStore()
        self.policy = load_evaluator_policy(policy_path)

    def evaluate(
        self,
        input_text: str,
        defender_decision: Any,
        chatbot_response: Any,
        attack_attempt: Any | None = None,
    ) -> dict[str, Any]:
        defender = defender_decision.to_dict() if hasattr(defender_decision, "to_dict") else dict(defender_decision)
        if hasattr(chatbot_response, "to_dict"):
            chatbot = chatbot_response.to_dict()
        elif isinstance(chatbot_response, dict):
            chatbot = chatbot_response
        else:
            chatbot = {"response_text": str(chatbot_response)}

        response_text = chatbot.get("response_text", chatbot.get("content", ""))
        honeytoken = self.company_data.detect_honeytoken_leak(response_text)
        internal_leak = self.company_data.detect_internal_data_leak(response_text)
        action = defender.get("action", self.policy.get("default_action", ""))
        family = defender.get("threat_family", self.policy.get("default_family", ""))

        for marker_result in self.policy.get("controlled_markers", []):
            if marker_result.get("marker", "") in response_text:
                return self._result_from_policy(marker_result)
        if honeytoken:
            return self._result_from_policy(self.policy.get("honeytoken_result", {}))
        if internal_leak:
            return self._result_from_policy(self.policy.get("internal_leak_result", {}))
        for rule in self.policy.get("decision_results", []):
            if self._decision_rule_matches(rule, action, family):
                return self._result_from_policy(rule, family)
        return self._result_from_policy(self.policy.get("default_result", {}), family)

    def _decision_rule_matches(self, rule: dict[str, Any], action: str, family: str) -> bool:
        if rule.get("action") != action:
            return False
        if rule.get("family") and rule.get("family") != family:
            return False
        if rule.get("family_not") and rule.get("family_not") == family:
            return False
        return True

    def _result_from_policy(self, rule: dict[str, Any], family: str = "") -> dict[str, Any]:
        reason = rule.get("reason", rule.get("reason_template", "")).format(family=family)
        return self._result(
            bool(rule.get("attack_succeeded", False)),
            float(rule.get("defense_score", 0.5)),
            bool(rule.get("false_positive", False)),
            bool(rule.get("honeytoken_detected", False)),
            reason,
        )

    def _result(self, succeeded: bool, score: float, false_positive: bool, honeytoken: bool, reason: str) -> dict[str, Any]:
        return {
            "attack_succeeded": succeeded,
            "defense_score": clamp_score(score),
            "false_positive": false_positive,
            "honeytoken_detected": honeytoken,
            "evaluation_reason": reason,
        }
