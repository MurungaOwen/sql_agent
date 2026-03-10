from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from sql_agent.interfaces import LLMProvider


class OpenAICompatibleLLMProvider(LLMProvider):
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.0,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        kwargs = {"model": model_name, "temperature": temperature}
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["base_url"] = base_url
        self.model = ChatOpenAI(**kwargs)

    def generate_sql(self, question: str, schema_context: str, max_rows: int) -> str:
        system = SystemMessage(
            content=(
                "You translate user questions into SQL. "
                "Rules: return SQL only, no markdown, no explanation. "
                "Use only listed tables/columns. "
                "Only read queries (SELECT/CTE). "
                f"Prefer LIMIT {max_rows} when no explicit limit is requested."
            )
        )
        human = HumanMessage(
            content=(
                "Schema context:\n"
                f"{schema_context}\n\n"
                "User question:\n"
                f"{question}"
            )
        )
        response = self.model.invoke([system, human])
        return self._extract_text(response.content)

    def summarize_result(self, question: str, sql: str, rows: str) -> str:
        system = SystemMessage(
            content="Summarize SQL results for business users in 2-4 concise sentences."
        )
        human = HumanMessage(
            content=(
                f"Question: {question}\n"
                f"SQL: {sql}\n"
                f"Rows:\n{rows}\n"
                "Give a factual summary. If result is empty, say so clearly."
            )
        )
        response = self.model.invoke([system, human])
        return self._extract_text(response.content)

    def _extract_text(self, content: str | list[dict]) -> str:
        if isinstance(content, str):
            return content.strip()

        parts: list[str] = []
        for item in content:
            if item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "\n".join(p for p in parts if p).strip()


class OpenAILLMProvider(OpenAICompatibleLLMProvider):
    def __init__(self, model_name: str, temperature: float = 0.0):
        super().__init__(model_name=model_name, temperature=temperature)


class HuggingFaceLLMProvider(OpenAICompatibleLLMProvider):
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.0,
        api_key: str | None = None,
        base_url: str = "https://router.huggingface.co/v1",
    ):
        hf_key = api_key or os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        if not hf_key:
            raise ValueError(
                "HUGGINGFACE_API_KEY (or HF_TOKEN) is required for MODEL_PROVIDER=huggingface"
            )
        super().__init__(
            model_name=model_name,
            temperature=temperature,
            api_key=hf_key,
            base_url=base_url,
        )
