from datetime import datetime
from typing import Any

from attacker_agent.agent import AttackerAgent
from chatbot.assistant import ProtectedAssistant
from defender_agent.agent import DefenderAgent
from evaluator_agent.agent import EvaluatorAgent
from learning_agent.agent import LearningAgent
from memory.company_data_store import CompanyDataStore
from memory.structured_memory import StructuredMemory
from memory.vector_memory import VectorMemory
from orchestration.state import AttackAttempt, ChatbotResponse, DefenderDecision, EvaluationResult


class DefenseGraph:
    def __init__(
        self,
        attacker_agent=None,
        defender_agent=None,
        chatbot=None,
        evaluator_agent=None,
        learning_agent=None,
        structured_memory=None,
        vector_memory=None,
        mode: str = "PROTECTION",
    ):
        self.structured_memory = structured_memory or StructuredMemory()
        self.vector_memory = vector_memory or VectorMemory()
        self.attacker_agent = attacker_agent or AttackerAgent()
        self.defender_agent = defender_agent or DefenderAgent(memory=self.structured_memory, mode=mode)
        self.chatbot = chatbot or ProtectedAssistant(mode=mode)
        self.evaluator_agent = evaluator_agent or EvaluatorAgent()
        self.learning_agent = learning_agent or LearningAgent(memory=self.structured_memory)
        self.mode = mode
        self.interaction_counter = 0

    def set_mode(self, mode: str) -> None:
        if mode in {"PROTECTION", "CONTROLLED_EXFILTRATION"}:
            self.mode = mode
            self.defender_agent.set_mode(mode)
            self.chatbot.set_mode(mode)

    def process_user_message(
        self,
        message: str,
        chat_history: list[dict[str, Any]] | None = None,
        learned_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.step(message, input_source="user", learned_memory=learned_memory)

    def run_attack_round(
        self,
        attack_family: str = "Balanced",
        strategy: str = "Template Probe",
        round_number: int = 0,
        learned_memory: dict[str, Any] | None = None,
        aggressiveness: float = 0.5,
    ) -> dict[str, Any]:
        attack = self.attacker_agent.generate_attack(
            attack_family=attack_family,
            strategy=strategy,
            round_number=round_number,
            learned_memory=learned_memory,
            aggressiveness=aggressiveness,
        )
        attempt = AttackAttempt(
            source=attack.get("source", "attacker_agent"),
            attack_family=attack.get("attack_family", "unknown"),
            attack_strategy=attack.get("attack_strategy", strategy),
            display_text=attack.get("display_text", ""),
            pattern_label=attack.get("pattern_label", ""),
            risk_hint=attack.get("risk_hint", 0.5),
        )
        return self.step(attempt.display_text, input_source="attacker_agent", attack_attempt=attempt)

    def step(
        self,
        input_message: str,
        input_source: str = "user",
        attack_attempt: AttackAttempt | None = None,
        learned_memory: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.interaction_counter += 1
        timestamp = datetime.now().isoformat()

        defender_dict = self.defender_agent.analyze(input_message, learned_memory)
        defender = DefenderDecision(
            action=defender_dict.get("action", "PASS"),
            risk_score=defender_dict.get("risk_score", 0.0),
            threat_family=defender_dict.get("threat_family", "benign"),
            reason=defender_dict.get("reason", ""),
            matched_pattern=defender_dict.get("matched_pattern", ""),
            used_memory=defender_dict.get("used_memory", False),
        )

        chatbot_dict = self.chatbot.respond(input_message, defender_dict)
        chatbot = ChatbotResponse(
            response_text=chatbot_dict.get("content", ""),
            response_mode=chatbot_dict.get("response_mode", "normal"),
            safety_status=chatbot_dict.get("safety_status", "safe"),
        )

        company_data = CompanyDataStore()
        company_data_retrieved = company_data.detect_internal_data_leak(chatbot.response_text)
        rag_event = {
            "retrieval_type": "pattern_and_rule",
            "query": input_message[:160],
            "retrieved_pattern": defender.matched_pattern,
            "retrieved_rule": "",
            "company_data_allowed": defender.action == "ALLOW_WITH_MONITORING",
            "company_data_retrieved": company_data_retrieved,
        }

        evaluator_dict = self.evaluator_agent.evaluate(input_message, defender.to_dict(), chatbot.to_dict(), attack_attempt)
        evaluator = EvaluationResult(
            attack_succeeded=evaluator_dict.get("attack_succeeded", False),
            defense_score=evaluator_dict.get("defense_score", 0.5),
            false_positive=evaluator_dict.get("false_positive", False),
            evaluation_reason=evaluator_dict.get("evaluation_reason", ""),
        )

        learner_dict = self.learning_agent.learn(input_message, defender.to_dict(), evaluator_dict, attack_attempt, learned_memory)

        interaction_id = self.structured_memory.log_interaction(
            {
                "timestamp": timestamp,
                "input_source": input_source,
                "raw_input": input_message,
                "sanitized_input": input_message,
                "threat_family": defender.threat_family,
                "defender_action": defender.action,
                "risk_score": defender.risk_score,
                "matched_pattern": defender.matched_pattern,
                "used_memory": defender.used_memory,
                "rag_used": defender_dict.get("rag_used", False),
                "chatbot_response": chatbot.response_text,
                "response_mode": chatbot.response_mode,
                "data_returned": company_data_retrieved,
                "honeytoken_detected": evaluator_dict.get("honeytoken_detected", False),
                "attack_succeeded": evaluator.attack_succeeded,
                "defense_score": evaluator.defense_score,
                "false_positive": evaluator.false_positive,
                "evaluation_reason": evaluator.evaluation_reason,
                "mode": self.mode,
            }
        )
        self.structured_memory.log_rag_event(interaction_id, rag_event)

        return {
            "interaction_id": interaction_id,
            "timestamp": timestamp,
            "source": input_source,
            "safe_input": input_message,
            "assistant_response": chatbot.response_text,
            "defender": {**defender_dict, "used_memory": defender.used_memory},
            "chatbot": chatbot_dict,
            "evaluator": evaluator_dict,
            "learner": learner_dict,
            "rag_event": rag_event,
            "mode": self.mode,
        }

    def should_continue(self, iteration: int, max_iterations: int, convergence_status: str = "") -> bool:
        return iteration < max_iterations

    def reached_convergence(self, recent_scores: list[float]) -> bool:
        return len(recent_scores) >= 5 and all(score > 0.9 for score in recent_scores[-5:])

    def get_metrics(self) -> dict[str, Any]:
        return self.structured_memory.get_metrics()

    def get_learned_patterns(self) -> list[dict[str, Any]]:
        return self.structured_memory.get_patterns()

    def get_defender_rules(self) -> list[dict[str, Any]]:
        return self.structured_memory.get_rules()

    def get_recent_interactions(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.structured_memory.get_recent_interactions(limit)

    def get_rag_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.structured_memory.get_rag_events(limit)
