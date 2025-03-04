"""Chat and model interfaces for the Gemini API."""

from collections.abc import Iterator
from typing import Any, Dict, List, Optional, Union

from .config import GeminiClient
from .types import ChatMessage, ModelResponse


class Chat:
    """Manages chat conversations with the Gemini API."""

    def __init__(
        self,
        client: GeminiClient,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> None:
        """Initialize a chat session.

        Args:
            client: The Gemini API client
            system_prompt: Optional system-level instruction
            temperature: Optional temperature override
        """
        self.client = client
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.history: List[ChatMessage] = []
        if system_prompt:
            self.history.append(ChatMessage(role="system", content=system_prompt))

    def send(
        self,
        message: str,
        stream: bool = False,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> Union[ModelResponse, Iterator[ModelResponse]]:
        """Send a message and get response.

        Args:
            message: The message to send
            stream: Whether to stream the response
            temperature: Optional temperature override
            **kwargs: Additional configuration options

        Returns:
            The model's response or response stream
        """
        # Add user message to history
        self.history.append(ChatMessage(role="user", content=message))

        # Build configuration
        config_dict: Dict[str, Any] = {}
        if temperature is not None:
            config_dict["temperature"] = temperature
        elif self.temperature is not None:
            config_dict["temperature"] = self.temperature
        config_dict.update(kwargs)

        if stream:
            return self._stream_message(message, config_dict)

        response = self._send_message(message, config_dict)
        response_text = (
            str(response.text) if hasattr(response, "text") else str(response)
        )
        self.history.append(ChatMessage(role="assistant", content=response_text))
        return ModelResponse(text=response_text)

    def _send_message(
        self, message: str, config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Send a message and get complete response."""
        chat = self.client.client.chats.create()
        return chat.send_message(message, config=config)

    def _stream_message(
        self, message: str, config: Optional[Dict[str, Any]] = None
    ) -> Iterator[ModelResponse]:
        """Stream message response chunks."""
        chat = self.client.client.chats.create()
        for chunk in chat.send_message_stream(message, config=config):
            if hasattr(chunk, "text") and chunk.text:
                yield ModelResponse(text=str(chunk.text))

    def reset(self) -> None:
        """Clear chat history."""
        self.history = []
        if self.system_prompt:
            self.history.append(ChatMessage(role="system", content=self.system_prompt))

    def get_history(self) -> List[ChatMessage]:
        """Get conversation history.

        Returns:
            List of chat messages
        """
        return self.history
