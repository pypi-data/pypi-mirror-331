"""Functions for interacting with Gemini models."""

from collections.abc import Iterator
from typing import Any, Dict, List, Optional, Union

from PIL import Image

from .config import GeminiClient
from .types import ModelResponse


class TextGenerator:
    """Generator for text and chat responses."""

    def __init__(self, client: GeminiClient) -> None:
        """Initialize the generator.

        Args:
            client: The Gemini API client
        """
        self.client = client

    def generate(
        self,
        prompt: Union[str, List[Union[str, Image.Image, bytes]]],
        system_prompt: Optional[str] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[ModelResponse, Iterator[ModelResponse]]:
        """Generate text from a prompt.

        Args:
            prompt: Text prompt or list of text/image prompts
            system_prompt: Optional system-level instruction
            stream: Whether to stream the response
            **kwargs: Additional generation parameters

        Returns:
            Generated text response or response stream
        """
        config: Dict[str, Any] = {}
        if system_prompt or kwargs:
            if system_prompt:
                config["system_instruction"] = system_prompt
            config.update(kwargs)

        if stream:
            return self._generate_stream(prompt, config)

        response = self._generate(prompt, config)
        # Handle both string and object responses
        response_text = (
            str(response.text) if hasattr(response, "text") else str(response)
        )
        return ModelResponse(text=response_text)

    def _generate(
        self,
        prompt: Union[str, List[Union[str, Image.Image, bytes]]],
        config: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Generate complete response."""
        return self.client.models.generate_content(prompt, config=config)

    def _generate_stream(
        self,
        prompt: Union[str, List[Union[str, Image.Image, bytes]]],
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterator[ModelResponse]:
        """Generate streaming response."""
        for chunk in self.client.models.generate_content_stream(prompt, config=config):
            if hasattr(chunk, "text") and chunk.text:
                yield ModelResponse(text=str(chunk.text))
