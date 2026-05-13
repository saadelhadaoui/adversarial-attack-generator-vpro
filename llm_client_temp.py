import json
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, model_name: str = "qwen2.5:14b-instruct-q4_K_M", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.chat_url = f"{self.host}/api/chat"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if not self.is_available():
            logger.warning("Ollama unavailable. Returning fallback response.")
            return "Fallback response: Ollama not available."

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(self.chat_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"LLM chat error: {str(e)}")
            return "Fallback response: Error during LLM generation."

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        if not self.is_available():
            logger.warning("Ollama unavailable. Returning fallback JSON.")
            return {"error": "service_unavailable", "action": "BLOCK"}

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(self.chat_url, json=payload, timeout=30)
            response.raise_for_status()
            text_response = response.json().get("message", {}).get("content", "{}")
            return json.loads(text_response)
        except json.JSONDecodeError:
            return {"error": "parse_failure", "action": "BLOCK"}
        except Exception as e:
            return {"error": "system_failure", "action": "BLOCK"}
