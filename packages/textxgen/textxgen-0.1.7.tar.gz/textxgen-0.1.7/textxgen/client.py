import requests
from typing import Iterator, Dict, Any
from .exceptions import APIError, InvalidInputError
import json
import logging

# Enable this line to see debug logs
# logging.basicConfig(level=logging.DEBUG)

# Disable debug logs by setting the logging level to WARNING or higher
logging.basicConfig(level=logging.WARNING)  # Change this to WARNING or ERROR


class APIClient:
    """
    Handles API requests to the proxy server.
    """

    def __init__(self):
        # Hardcode the proxy server URL (without the extra `/chat`)
        self.proxy_url = "https://vercel-proxy-alpha-coral.vercel.app"

    def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: dict = None,
        stream: bool = False,
    ) -> Any:
        """
        Makes an API request to the proxy server.
        """
        # Construct the full URL correctly
        url = f"{self.proxy_url}{endpoint}"
        try:
            # Debug logs are now suppressed
            response = requests.request(method, url, json=data, stream=stream)
            response.raise_for_status()

            if stream:
                return self._handle_streaming_response(response)
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise APIError(
                f"HTTP Error: {e.response.status_code} - {e.response.text}",
                e.response.status_code,
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"Request Error: {str(e)}")
            raise APIError(
                f"Request Error: {str(e)}", getattr(e.response, "status_code", None)
            )

    def _handle_streaming_response(
        self, response: requests.Response
    ) -> Iterator[Dict[str, Any]]:
        """
        Handles streaming responses from the proxy server.
        """
        buffer = ""
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                # Decode the chunk and add it to the buffer
                buffer += chunk.decode("utf-8")
                # Split the buffer by newlines to process individual SSE events
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.startswith("data: "):
                        # Extract the JSON data from the SSE event
                        json_data = line[len("data: ") :]
                        if json_data.strip() == "[DONE]":
                            # End of stream
                            return
                        try:
                            # Parse the JSON data
                            yield json.loads(json_data)
                        except json.JSONDecodeError as e:
                            logging.error(f"JSON Decode Error: {e}")
                            raise APIError(f"JSON Decode Error: {e}", 500)

    def chat_completion(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> Any:
        """
        Sends a chat completion request to the proxy server.
        """
        if not messages or not isinstance(messages, list):
            raise InvalidInputError("Messages must be a non-empty list.")

        payload = {
            "model": model or "meta-llama/llama-3.1-8b-instruct:free",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        # Use the correct endpoint `/chat`
        return self._make_request("/chat", data=payload, stream=stream)
