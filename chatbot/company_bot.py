import os

from chatbot.policy import load_chatbot_policy
from llm.client import LLMClient
from memory.company_data_store import CompanyDataStore


DEFAULT_POLICY_PATH = "data/chatbot_policy.json"


class CompanyBot:
    def __init__(self, mode: str | None = None, policy_path: str | None = None):
        self.policy = self._load_policy(policy_path or os.getenv("CHATBOT_POLICY_PATH", DEFAULT_POLICY_PATH))
        self.mode = mode or self.policy.get("default_mode", "")
        self.company_data = CompanyDataStore()
        self.llm = LLMClient()

    def _load_policy(self, path: str) -> dict:
        return load_chatbot_policy(path)

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def respond(self, message: str, defender_decision: dict) -> dict:
        action = defender_decision.get("action", self.policy.get("default_action", ""))
        family = defender_decision.get("threat_family", self.policy.get("default_family", ""))
        actions = self.policy.get("actions", {})

        if action == actions.get("block", ""):
            return {
                "content": self.policy.get("blocked_response", "I cannot provide that."),
                "response_mode": "refused",
                "safety_status": "blocked",
                "llm_used": False,
                "llm_available": self.llm.is_available(),
                "llm_model_available": self.llm.is_model_available(),
                "llm_model": self.llm.model,
            }

        if action == actions.get("reformulate", ""):
            content = self._llm_safe_response(
                message,
                self.policy.get("reformulation_system_prompt", ""),
            )
            return {
                "content": content,
                "response_mode": "safe_reformulation",
                "safety_status": "safe",
                "llm_used": self._is_real_llm_response(content),
                "llm_available": self.llm.is_available(),
                "llm_model_available": self.llm.is_model_available(),
                "llm_model": self.llm.model,
            }

        if action == actions.get("monitor", ""):
            rendered = self._controlled_lab_response(message, family)
            return {
                "content": rendered or self.policy.get("no_records_response", ""),
                "response_mode": "monitored",
                "safety_status": "monitored",
                "llm_used": False,
                "llm_available": self.llm.is_available(),
                "llm_model_available": self.llm.is_model_available(),
                "llm_model": self.llm.model,
            }

        content = self._llm_safe_response(
            message,
            self.policy.get("normal_system_prompt", ""),
        )
        return {
            "content": content,
            "response_mode": "normal",
            "safety_status": "safe",
            "llm_used": self._is_real_llm_response(content),
            "llm_available": self.llm.is_available(),
            "llm_model_available": self.llm.is_model_available(),
            "llm_model": self.llm.model,
        }

    def _llm_safe_response(self, message: str, system_prompt: str) -> str:
        response = self.llm.chat(
            system_prompt=system_prompt,
            user_prompt=message,
            temperature=0.2,
        ).strip()
        if response and not response.startswith("Fallback response:"):
            return response
        return self._benign_fallback(message)

    def _is_real_llm_response(self, content: str) -> bool:
        return (
            bool(content)
            and self.llm.is_available()
            and self.llm.is_model_available()
            and not content.startswith("Fallback response:")
            and "Ollama was not reachable" not in content
            and "Ollama is not reachable" not in content
            and "is not pulled or not visible" not in content
        )

    def _controlled_lab_response(self, message: str, family: str) -> str:
        if family == self.policy.get("data_retrieval_family", ""):
            records = self.company_data.retrieve(message, self.mode, allowed=True)
            return self.company_data.render_records(records)
        if family in self.policy.get("controlled_responses", {}):
            return self._controlled_marker_response(message, family)
        return ""

    def _controlled_marker_response(self, message: str, family: str) -> str:
        config = self.policy.get("controlled_responses", {}).get(family, {})
        if not config:
            return ""
        text = (message or "").lower()
        selected = config.get("default_case", {})
        for case in config.get("cases", []):
            terms = [str(term).lower() for term in case.get("match_any", [])]
            if any(term in text for term in terms):
                selected = case
                break
        prefix = config.get("prefix", "")
        label = selected.get("label", "")
        marker = selected.get("marker", "")
        suffix = config.get("suffix", "")
        return (
            f"{prefix}: {label} exposed synthetic marker {marker}. "
            f"{suffix}"
        )

    def _benign_fallback(self, message: str) -> str:
        text = (message or "").lower()
        for item in self.policy.get("benign_fallback_by_term", []):
            terms = [str(term).lower() for term in item.get("match_any", [])]
            if any(term in text for term in terms):
                return item.get("response", "")
        return self.policy.get("default_fallback_template", "").format(host=self.llm.host, model=self.llm.model)
