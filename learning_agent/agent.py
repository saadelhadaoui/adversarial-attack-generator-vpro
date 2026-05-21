from typing import Any

from learning_agent.pattern_extractor import extract_pattern, load_learning_policy
from learning_agent.rule_generator import generate_rule
from memory.structured_memory import StructuredMemory


class LearningAgent:
    def __init__(self, memory: StructuredMemory | None = None, policy_path: str | None = None):
        self.memory = memory or StructuredMemory()
        self.policy = load_learning_policy(policy_path)

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
        family = defender.get("threat_family", self.policy.get("default_family", ""))
        action = defender.get("action", self.policy.get("default_action", ""))
        learn_actions = set(self.policy.get("learn_actions", []))
        should_learn = bool(evaluator.get("attack_succeeded")) or action in learn_actions

        if not should_learn or family in set(self.policy.get("skip_families", [])):
            return {
                "learner_update": "No learning trigger.",
                "learned_pattern": "",
                "generated_rule": "",
                "memory_updated": False,
                "confidence": 0.0,
            }

        confidence = float(self.policy.get("confidence", 0.8))
        pattern = extract_pattern(input_text, family, self.policy)
        rule = generate_rule(family, pattern, self.policy)
        self.memory.save_pattern(pattern, family, confidence, "learning_agent")
        self.memory.save_rule(rule, family, pattern, confidence)
        return {
            "learner_update": f"Stored defensive pattern for {family}.",
            "learned_pattern": pattern,
            "generated_rule": rule,
            "memory_updated": True,
            "confidence": confidence,
        }
