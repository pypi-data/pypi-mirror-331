"""Type definitions for the Gemini API wrapper."""

from typing import Dict, Optional, Union

from pydantic import BaseModel


class GenerationConfig(BaseModel):
    """Configuration for text generation."""

    temperature: float = 0.7
    max_output_tokens: int = 2048
    top_p: float = 0.95
    top_k: int = 40
    system_instruction: Optional[str] = None

    def to_dict(self) -> Dict[str, Union[float, int, str]]:
        """Convert to dictionary."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class TuningExample(BaseModel):
    """Example for model tuning."""

    input_text: str
    output_text: str


class ChatMessage(BaseModel):
    """A chat message."""

    role: str  # "user", "assistant", or "system"
    content: str


class FileConfig(BaseModel):
    """Configuration for file operations."""

    mime_type: Optional[str] = None
    chunk_size: Optional[int] = None


class ImageData(BaseModel):
    """Image data for vision models."""

    data: bytes
    mime_type: Optional[str] = None


class ToolCall(BaseModel):
    """A tool/function call."""

    name: str
    args: Dict[str, str]


class ModelResponse:
    """Response from a model."""

    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        return self.text
