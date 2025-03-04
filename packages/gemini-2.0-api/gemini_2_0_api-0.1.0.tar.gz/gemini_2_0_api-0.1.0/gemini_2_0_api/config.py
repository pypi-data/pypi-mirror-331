"""Configuration module for Gemini API client and settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TypedDict

from google.genai import types

MODEL_TYPE_MAPPING = {
    "flash": "gemini-2.0-flash",
    "pro": "gemini-2.0-pro",
    "vision": "gemini-2.0-vision",
}


class HttpOptions(TypedDict, total=False):
    """Type definition for HTTP client options."""

    timeout: float
    api_version: str
    retry_max_attempts: int
    retry_delay: float
    retry_multiplier: float


@dataclass
class GeminiConfig:
    """Configuration class for Gemini API settings."""

    api_key: str
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.7
    safety_settings: list[types.SafetySetting] | None = None
    http_options: HttpOptions | None = None

    @classmethod
    def from_env(
        cls, model_name: str = "flash", temperature: float = 0.7
    ) -> GeminiConfig:
        """Create config from environment variable GOOGLE_API_KEY."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        model = MODEL_TYPE_MAPPING.get(model_name, model_name)
        return cls(api_key=api_key, model_name=model, temperature=temperature)


class GeminiClient:
    """Client for the Gemini API."""

    def __init__(self, api_key: str, model_type: str = "pro"):
        """Initialize the client.

        Args:
            api_key: The API key for authentication
            model_type: The type of model to use (pro, flash, vision)
        """
        self.api_key = api_key
        self.model_type = model_type
        self.config = self._get_config()

    @classmethod
    def from_env(cls, model_type: str = "pro") -> GeminiClient:
        """Create a client from environment variables.

        Args:
            model_type: The type of model to use

        Returns:
            A configured client instance
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        return cls(api_key=api_key, model_type=model_type)

    def _get_config(self):
        """Get the configuration for the current model type."""
        # This would be expanded with actual model configurations
        return {
            "temperature": 0.7,
            "max_output_tokens": 2048,
        }
