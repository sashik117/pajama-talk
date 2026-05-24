from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import settings


class AIProvider:
    def generate_json(self, prompt: str) -> dict[str, Any] | None:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    def generate_json(self, prompt: str) -> dict[str, Any] | None:
        return None


class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate_json(self, prompt: str) -> dict[str, Any] | None:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                    ],
                },
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.55,
            },
        }
        try:
            response = httpx.post(
                url,
                params={"key": self.api_key},
                json=payload,
                timeout=20,
            )
            response.raise_for_status()
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError):
            return None


def get_ai_provider() -> AIProvider:
    if settings.gemini_api_key:
        return GeminiAIProvider(settings.gemini_api_key, settings.gemini_model)
    return MockAIProvider()
