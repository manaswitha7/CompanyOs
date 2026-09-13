import os

from dotenv import load_dotenv
from litellm import completion


load_dotenv()


class LLMProvider:
    """
    Provider-agnostic LLM interface for Company OS.
    """

    SUPPORTED_PROVIDERS = {
        "gemini",
        "openai",
        "anthropic",
        "ollama",
    }

    def __init__(self):
        self.provider = os.getenv(
            "LLM_PROVIDER",
            "gemini",
        ).strip().lower()

        self.model = os.getenv(
            "LLM_MODEL",
            "gemini/gemini-2.5-flash",
        ).strip()

        self.api_key = self._get_api_key()

        self._validate_configuration()

    def _get_api_key(self) -> str | None:

        if self.provider == "gemini":
            return os.getenv("GEMINI_API_KEY")

        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")

        if self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")

        if self.provider == "ollama":
            return None

        return None

    def _validate_configuration(self):

        if self.provider not in self.SUPPORTED_PROVIDERS:
            raise RuntimeError(
                f"Unsupported LLM_PROVIDER: "
                f"{self.provider}. "
                f"Supported providers: "
                f"{', '.join(sorted(self.SUPPORTED_PROVIDERS))}"
            )

        if not self.model:
            raise RuntimeError(
                "LLM_MODEL is not configured."
            )

        if (
            self.provider != "ollama"
            and not self.api_key
        ):
            raise RuntimeError(
                f"API key is not configured for "
                f"LLM provider '{self.provider}'."
            )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        kwargs = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": temperature,
        }

        if self.api_key:
            kwargs["api_key"] = self.api_key

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        try:

            response = completion(**kwargs)

        except Exception as exc:

            raise RuntimeError(
                f"LLM generation failed using "
                f"{self.provider}/{self.model}: {exc}"
            ) from exc

        if not response.choices:
            raise RuntimeError(
                "LLM returned no choices."
            )

        content = (
            response.choices[0]
            .message
            .content
        )

        if not content:
            raise RuntimeError(
                "LLM returned an empty response."
            )

        return content.strip()

    def get_info(self) -> dict:

        return {
            "provider": self.provider,
            "model": self.model,
            "api_key_configured": bool(
                self.api_key
            ),
        }
