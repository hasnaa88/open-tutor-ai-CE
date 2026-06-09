"""LLM service for coordinating completions."""

from ai.llm.schemas import LLMRequest, LLMResponse
from ai.llm.transports.base import LLMTransport


class LLMService:
    """Service for LLM operations."""

    def __init__(self, transport: LLMTransport):
        self.transport = transport

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Get completion from LLM."""
        return await self.transport.complete(request)
