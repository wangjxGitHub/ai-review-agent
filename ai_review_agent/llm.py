from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Optional extension point for teams that want LLM-backed rewriting."""

    @abstractmethod
    def rewrite(self, prompt: str) -> str:
        """Return a rewritten proposal from a provider-specific implementation."""


class NoopLLMProvider(LLMProvider):
    """Default provider used when no external model is configured."""

    def rewrite(self, prompt: str) -> str:
        return prompt

