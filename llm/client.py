import json
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, model: str = "qwen2.5:14b-instruct-q4_K_M", host: str = "http://127.0.0.1:11434"):
        self.model = model
        self.host = host.rstrip("/")
        self.chat_url = f"{self.host}/api/chat"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if not self.is_available():
            return "Fallback response: Ollama is not available, so deterministic safety logic handled this request."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            response = requests.post(self.chat_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except Exception as exc:
            logger.warning("LLM chat failed: %s", exc)
            return "Fallback response: deterministic safety logic handled this request."

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> dict[str, Any]:
        if not self.is_available():
            return {"error": "service_unavailable"}

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            response = requests.post(self.chat_url, json=payload, timeout=30)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "{}")
            return json.loads(content)
        except Exception as exc:
            logger.warning("LLM JSON chat failed: %s", exc)
            return {"error": "system_failure"}
