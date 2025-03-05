# textxgen/config.py

class Config:
    """
    Configuration class for TextxGen package.
    Stores API key, endpoints, and other configurations.
    """

    # Predefined API key for OpenRouter
    API_KEY = "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"

    # Base URL for OpenRouter API
    BASE_URL = "https://openrouter.ai/api/v1"

    # Supported models (actual model IDs)
    SUPPORTED_MODELS = {
        "llama3": "meta-llama/llama-3.1-8b-instruct:free",
        "phi3": "microsoft/phi-3-mini-128k-instruct:free",
        "deepseek": "deepseek/deepseek-chat:free",
    }

    # Default model
    DEFAULT_MODEL = SUPPORTED_MODELS["llama3"]

    # Headers for API requests
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    @staticmethod
    def get_model_display_names() -> dict:
        """
        Returns a dictionary of model display names (without the `:free` suffix).

        Returns:
            dict: Model display names mapped to their keys.
        """
        return {
            "llama3": "LLaMA 3 (8B Instruct)",
            "phi3": "Phi-3 Mini (128K Instruct)",
            "deepseek": "DeepSeek Chat",
        }