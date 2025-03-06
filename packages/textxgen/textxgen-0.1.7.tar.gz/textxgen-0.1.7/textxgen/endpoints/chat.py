# textxgen/endpoints/chat.py

from typing import Iterator, Dict, Any
from ..client import APIClient
from ..models import Models
from ..exceptions import InvalidInputError



class ChatEndpoint:
    """
    Handles chat-based interactions with the proxy server.
    """

    def __init__(self):
        self.client = APIClient()  # No need to pass proxy_url
        self.models = Models()

    def chat(
        self,
        messages: list,
        model: str = None,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 100,
        stream: bool = False,
    ) -> Any:
        """
        Sends a chat request to the proxy server.
        """
        if not messages or not isinstance(messages, list):
            raise InvalidInputError("Messages must be a non-empty list.")

        # Prepare the payload
        payload = {
            "model": self.models.get_model(model) if model else Models().list_models()["llama3"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        # Add system prompt if provided
        if system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": system_prompt})

        # Send the request
        return self.client.chat_completion(messages=payload["messages"], model=payload["model"], stream=stream)

    def get_supported_models_display(self) -> dict:
        """
        Returns a dictionary of supported models with display names.

        Returns:
            dict: Supported models with display names.
        """
        return self.models.list_display_models()