import asyncio
import json
import logging
import os
from typing import Protocol

from openai import AzureOpenAI, RateLimitError

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Raised when the LLM client cannot complete a request."""


class LLMClient(Protocol):
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        ...


class AzureOpenAIClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

        if not self.api_key or not self.endpoint or not self.deployment_name:
            raise LLMClientError(
                "Missing Azure OpenAI configuration. "
                "Required: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, "
                "AZURE_OPENAI_DEPLOYMENT_NAME."
            )

        self.client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.endpoint,
            api_version=self.api_version,
        )

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        backoff_seconds = [1, 2, 4]
        last_error: Exception | None = None

        for attempt, sleep_seconds in enumerate(backoff_seconds, start=1):
            try:
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    max_tokens=600,
                )

                usage = response.usage
                if usage:
                    logger.info(
                        "LLM token usage prompt_tokens=%s completion_tokens=%s",
                        usage.prompt_tokens,
                        usage.completion_tokens,
                    )

                content = response.choices[0].message.content
                if not content:
                    raise LLMClientError("LLM returned empty content.")
                return content
            except RateLimitError as exc:
                last_error = exc
                logger.warning(
                    "Rate limit on attempt %s/3. Retrying in %ss.",
                    attempt,
                    sleep_seconds,
                )
                if attempt < len(backoff_seconds):
                    await asyncio.sleep(sleep_seconds)
            except Exception as exc:  # noqa: BLE001
                raise LLMClientError(f"Unrecoverable LLM failure: {exc}") from exc

        raise LLMClientError(f"Rate-limited after 3 attempts: {last_error}") from last_error


class MockLLMClient:
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        del system_prompt, user_prompt
        return json.dumps(
            {
                "priority_level": "HIGH",
                "confidence_score": 0.87,
                "reasoning": "Mocked decision: urgency and customer tier justify HIGH priority.",
                "requires_human_review": False,
                "review_reason": None,
            }
        )


def get_llm_client() -> LLMClient:
    use_mock = os.getenv("USE_MOCK_LLM", "false").strip().lower() == "true"
    if use_mock:
        logger.info("Using MockLLMClient because USE_MOCK_LLM=true")
        return MockLLMClient()
    return AzureOpenAIClient()
