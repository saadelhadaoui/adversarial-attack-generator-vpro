import json
import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, model: str | None = None, host: str | None = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:14b-instruct-q4_K_M")
        self.host = (host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")).rstrip("/")
        self.chat_url = f"{self.host}/api/chat"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def available_models(self) -> list[str]:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model.get("name", "") for model in models if model.get("name")]
        except Exception:
            return []

    def is_model_available(self) -> bool:
        return self.model in self.available_models()

    def health(self) -> dict[str, Any]:
        models = self.available_models()
        return {
            "host": self.host,
            "model": self.model,
            "server_available": bool(models) or self.is_available(),
            "model_available": self.model in models,
            "available_models": models,
        }

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if not self.is_available():
            return f"Fallback response: Ollama is not reachable at {self.host}."
        if not self.is_model_available():
            return f"Fallback response: Ollama is reachable, but model {self.model} is not pulled or not visible."

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
        if not self.is_model_available():
            return {"error": "model_unavailable", "model": self.model}

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
