"""Google Gemini API wrapper module."""

from collections.abc import Generator
from typing import Any, Dict, List, Optional, Union

import google.genai


class GeminiAPIWrapper:
    """Wrapper class for the Google Gemini API."""

    def __init__(self, api_key: str = None) -> None:
        """Initializes the Gemini API wrapper.

        Args:
            api_key: Optional API key for authentication.
        """
        # Configure API key
        google.genai.configure(api_key=api_key)

        # Store the genai module for direct access
        self.genai = google.genai

    def generate_content(
        self,
        model_name: str,
        contents: Union[str, List[Union[str, Any]]],
        generation_config: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Generates content using the specified Gemini model.

        Args:
            model_name: The name of the model to use
            contents: The input content to generate from
            generation_config: Optional configuration for generation

        Returns:
            The generated content response
        """
        model = google.genai.GenerativeModel(model_name)
        response = model.generate_content(contents, generation_config=generation_config)
        return response

    def generate_content_stream(
        self,
        model_name: str,
        contents: Union[str, List[Union[str, Any]]],
        generation_config: Optional[Dict[str, Any]] = None,
    ) -> Generator[Any, None, None]:
        """Generates content using streaming.

        Args:
            model_name: The name of the model to use
            contents: The input content to generate from
            generation_config: Optional configuration for generation

        Returns:
            A generator of content responses
        """
        model = google.genai.GenerativeModel(model_name)
        response = model.generate_content(
            contents, generation_config=generation_config, stream=True
        )
        yield from response

    def count_tokens(
        self,
        model_name: str,
        contents: Union[str, List[Union[str, Any]]],
    ) -> Any:
        """Counts tokens for the given content.

        Args:
            model_name: The name of the model to use
            contents: The content to count tokens for

        Returns:
            The token count response
        """
        model = google.genai.GenerativeModel(model_name)
        response = model.count_tokens(contents)
        return response

    def embed_content(
        self,
        model_name: str,
        contents: Union[str, List[Union[str, Any]]],
    ) -> Any:
        """Embeds the given content.

        Args:
            model_name: The name of the model to use
            contents: The content to embed

        Returns:
            The embedding response
        """
        model = google.genai.EmbeddingModel(model_name)
        response = model.embed_content(contents)
        return response

    def list_models(self) -> List[Any]:
        """Lists available models.

        Returns:
            List of available models
        """
        return list(google.genai.list_models())

    # Chat Module
    def create_chat_session(
        self,
        model_name: str,
        system_instruction: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Any:
        """Creates a new chat session.

        Args:
            model_name: The name of the model to use
            system_instruction: Optional system instruction/prompt
            generation_config: Optional configuration for generation
            history: Optional chat history

        Returns:
            A new chat session
        """
        model = google.genai.GenerativeModel(
            model_name,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
        chat = model.start_chat(history=history)
        return chat

    def send_message(
        self,
        chat_session: Any,
        message: str,
        generation_config: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Sends a message to the chat session.

        Args:
            chat_session: The chat session
            message: The message to send
            generation_config: Optional configuration

        Returns:
            The response from the chat
        """
        return chat_session.send_message(message, generation_config=generation_config)

    def send_message_stream(
        self,
        chat_session: Any,
        message: str,
        generation_config: Optional[Dict[str, Any]] = None,
    ) -> Generator[Any, None, None]:
        """Streams chat messages.

        Args:
            chat_session: The chat session
            message: The message to send
            generation_config: Optional configuration

        Returns:
            A generator of response chunks
        """
        response = chat_session.send_message(
            message, generation_config=generation_config, stream=True
        )
        yield from response

    # File operations - keep simple interfaces without complex types
    def upload_file(self, file_path: str) -> Any:
        """Uploads a file to the Gemini API.

        Args:
            file_path: Path to the file

        Returns:
            The uploaded file object
        """
        return google.genai.upload_file(path=file_path)

    def list_files(self) -> List[Any]:
        """Lists uploaded files.

        Returns:
            List of file objects
        """
        return list(google.genai.list_files())

    def get_file_info(self, name: str) -> Any:
        """Gets file information.

        Args:
            name: The file name/id

        Returns:
            File information
        """
        return google.genai.get_file(name=name)

    def delete_file(self, name: str) -> None:
        """Deletes a file.

        Args:
            name: The file name/id
        """
        google.genai.delete_file(name=name)

    # The tuning interface may vary significantly between
    # different versions of the genai library
    # Simplified approach using Any types
    def tune_model(
        self,
        base_model: str,
        training_data: Any,
        tuned_model_name: Optional[str] = None,
    ) -> Any:
        """Tunes a model with custom data.

        Args:
            base_model: Base model to tune
            training_data: Training data to use
            tuned_model_name: Optional name for the tuned model

        Returns:
            Information about the tuning job
        """
        # Interface may vary depending on genai version
        return google.genai.create_tuning_job(
            base_model=base_model,
            training_data=training_data,
            tuned_model_display_name=tuned_model_name,
        )

    def get_tuning_job(self, name: str) -> Any:
        """Gets information about a tuning job.

        Args:
            name: Tuning job ID

        Returns:
            Tuning job information
        """
        return google.genai.get_tuning_job(name=name)

    def list_tuning_jobs(self) -> List[Any]:
        """Lists all tuning jobs.

        Returns:
            List of tuning jobs
        """
        return list(google.genai.list_tuning_jobs())

    def list_tuned_models(self) -> List[Any]:
        """Lists all tuned models.

        Returns:
            List of tuned models
        """
        return list(google.genai.list_tuned_models())
