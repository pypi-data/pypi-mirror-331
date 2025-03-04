"""Example usage of the Gemini 2.0 API wrapper."""

from collections.abc import Iterator
from typing import Optional, Union

from dotenv import load_dotenv
from google.genai import types
from PIL import Image

from gemini_2_0_api import Chat, GeminiClient, ModelTuner, TextGenerator, Utils
from gemini_2_0_api.types import TuningExample


def generate_text(
    prompt: str,
    model_type: str = "flash",
    system_prompt: Optional[str] = None,
    stream: bool = False,
    temperature: float = 0.7,
    **kwargs,  # Additional config options
) -> Union[str, Iterator[str]]:
    """Generate text using the Gemini API.

    Args:
        prompt: The text prompt to generate from
        model_type: Model type (e.g. 'flash', 'pro', 'vision')
        system_prompt: Optional system-level instruction
        stream: Whether to stream the response
        temperature: Temperature for generation (0.0-1.0)
        **kwargs: Additional configuration options like:
                 response_mime_type, response_schema, tools, etc.

    Returns:
        Generated text or text stream if stream=True
    """
    client = GeminiClient.from_env(model_type=model_type, temperature=temperature)
    generator = TextGenerator(client)

    if system_prompt:
        kwargs["system_instruction"] = system_prompt

    return generator.generate(
        prompt=prompt,
        stream=stream,
        **kwargs,
    )


def analyze_image(
    prompt: str,
    image: Image.Image,
    model_type: str = "vision",
    stream: bool = False,
    **kwargs,  # Additional config options
) -> Union[str, Iterator[str]]:
    """Analyze an image using the vision model.

    Args:
        prompt: Text prompt about the image
        image: PIL Image object to analyze
        model_type: Model type (defaults to 'vision')
        stream: Whether to stream responses
        **kwargs: Additional configuration options

    Returns:
        Generated analysis text or text stream if stream=True
    """
    client = GeminiClient.from_env(model_type=model_type)
    generator = TextGenerator(client)

    return generator.generate(
        [prompt, image],
        stream=stream,
        **kwargs,
    )


def generate_with_tool(
    prompt: str,
    tool: types.Tool,
    model_type: str = "pro",
    stream: bool = False,
    **kwargs,
) -> Union[str, Iterator[str]]:
    """Generate content with a specific tool enabled.

    Args:
        prompt: The input prompt
        tool: The tool configuration (code execution, search, etc.)
        model_type: Model type to use
        stream: Whether to stream the response
        **kwargs: Additional configuration options

    Returns:
        Generated text or text stream
    """
    client = GeminiClient.from_env(model_type=model_type)
    generator = TextGenerator(client)

    kwargs["tools"] = [tool]
    return generator.generate(
        prompt,
        stream=stream,
        **kwargs,
    )


def chat_session(
    system_prompt: Optional[str] = None,
    model_type: str = "pro",
    temperature: Optional[float] = None,
    **kwargs,  # Additional config options
) -> Chat:
    """Create a new chat session.

    Args:
        system_prompt: Optional system-level instruction
        model_type: Model type (defaults to 'pro')
        temperature: Optional temperature override for this chat session
        **kwargs: Additional configuration options

    Returns:
        Chat session object
    """
    client = GeminiClient.from_env(model_type=model_type)
    return Chat(
        client,
        system_prompt=system_prompt,
        temperature=temperature,
        **kwargs,
    )


def tune_model(
    examples: list[TuningExample],
    base_model: Optional[str] = None,
    display_name: Optional[str] = None,
    learning_rate: float = 0.001,
    batch_size: int = 4,
    epoch_count: int = 5,
) -> str:
    """Fine-tune a model with examples.

    Args:
        examples: List of training examples
        base_model: Optional base model name
        display_name: Optional display name for tuned model
        learning_rate: Learning rate for tuning
        batch_size: Batch size for training
        epoch_count: Number of epochs to train

    Returns:
        Name/ID of the tuned model
    """
    client = GeminiClient.from_env()
    tuner = ModelTuner(client)

    return tuner.tune(
        examples=examples,
        base_model=base_model,
        display_name=display_name,
        learning_rate=learning_rate,
        batch_size=batch_size,
        epoch_count=epoch_count,
    )


def example_usage() -> None:
    """Demonstrate usage of the API wrapper."""
    load_dotenv()  # Load API key from .env file

    # Text generation example with JSON output
    text_response = generate_text(
        "Give me information about New York City.",
        system_prompt="You are a knowledgeable city guide.",
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "population": {"type": "number"},
                "nicknames": {"type": "array", "items": {"type": "string"}},
                "famous_landmarks": {"type": "array", "items": {"type": "string"}},
                "brief_history": {"type": "string"},
            },
        },
    )
    if isinstance(text_response, str):
        print(f"\nStructured city information:\n{text_response}\n")

    # Streaming example with function calling (now enabled by default)
    def get_weather(location: str) -> str:
        """Get weather for a location (mock function)."""
        return "sunny and 72°F"

    print("\nStreaming story with weather info:")
    stream_response = generate_text(
        "Tell me a story about a sunny day in Central Park.",
        stream=True,
        tools=[get_weather],  # Function calling enabled by default
    )
    if isinstance(stream_response, Iterator):
        for chunk in stream_response:
            print(chunk, end="", flush=True)
    print("\n")

    # Chat example with code execution
    chat = chat_session(
        system_prompt="You are a helpful Python programming assistant.",
        tools=[types.Tool(code_execution=types.CodeExecution())],
    )
    chat_response = chat.send(
        "Write and run a Python function to calculate the first 10 Fibonacci numbers."
    )
    if isinstance(chat_response, str):
        print(f"\nChat response with code execution:\n{chat_response}\n")

    # Image analysis example (if image exists)
    try:
        image = Image.open("example.jpg")
        image_response = analyze_image(
            prompt="Describe what you see in this image in detail:",
            image=image,
        )
        if isinstance(image_response, str):
            print(f"\nImage analysis:\n{image_response}\n")
    except FileNotFoundError:
        print("\nSkipping image example - no example.jpg found\n")

    # Model tuning example
    examples = [
        TuningExample(
            input_text="Translate to Spanish: Hello, how are you?",
            output_text="¡Hola! ¿Cómo estás?",
        ),
        TuningExample(
            input_text="Translate to Spanish: Good morning!",
            output_text="¡Buenos días!",
        ),
    ]

    try:
        model_name = tune_model(
            examples=examples,
            display_name="spanish-translator",
            epoch_count=3,  # Reduced for example
        )
        print(f"\nTuned model created: {model_name}\n")

        # Test the tuned model
        response = generate_text(
            "Translate to Spanish: Have a nice day!",
            model_type=model_name,  # Use the tuned model
        )
        if isinstance(response, str):
            print(f"Translation test:\n{response}\n")

    except Exception as e:
        print(f"\nTuning example failed: {e}\n")

    # Utility examples
    utils = Utils(GeminiClient.from_env())

    # Token counting
    text = "The quick brown fox jumps over the lazy dog."
    token_count = utils.count_tokens(text)
    print(f"\nToken count for '{text}': {token_count}")

    # Text embedding
    embedding = utils.embed_text(text)
    print(f"Embedding dimension: {len(embedding)}\n")


if __name__ == "__main__":
    example_usage()
