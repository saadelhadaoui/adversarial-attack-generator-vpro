from memory.company_data_store import CompanyDataStore


class CompanyBot:
    def __init__(self, mode: str = "PROTECTION"):
        self.mode = mode
        self.company_data = CompanyDataStore()

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def respond(self, message: str, defender_decision: dict) -> dict:
        action = defender_decision.get("action", "PASS")
        family = defender_decision.get("threat_family", "benign")

        if action == "BLOCK":
            return {
                "content": "I cannot provide that. I can help with a safe, high-level defensive explanation instead.",
                "response_mode": "refused",
                "safety_status": "blocked",
            }

        if action == "REFORMULATE":
            return {
                "content": "Here is a safe framing: focus on defensive controls, monitoring, and user education.",
                "response_mode": "safe_reformulation",
                "safety_status": "safe",
            }

        if action == "ALLOW_WITH_MONITORING" and family == "data_exfiltration":
            records = self.company_data.retrieve(message, self.mode, allowed=True)
            rendered = self.company_data.render_records(records)
            return {
                "content": rendered or "No matching synthetic company records were found.",
                "response_mode": "monitored",
                "safety_status": "monitored",
            }

        return {
            "content": self._benign_answer(message),
            "response_mode": "normal",
            "safety_status": "safe",
        }

    def _benign_answer(self, message: str) -> str:
        if "prompt injection" in (message or "").lower():
            return (
                "Prompt injection is an attempt to manipulate an AI system with instructions "
                "that conflict with its intended behavior. Defenses include instruction hierarchy, "
                "input validation, scoped tools, monitoring, and least-privilege data access."
            )
        return "I can help with safe defensive security analysis and high-level AI safety guidance."
