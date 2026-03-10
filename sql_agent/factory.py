from __future__ import annotations

from sql_agent.adapters.database import LangChainSQLToolkitProvider
from sql_agent.adapters.llm import HuggingFaceLLMProvider, OpenAILLMProvider
from sql_agent.config import Settings
from sql_agent.guardrails import SQLGuardrails
from sql_agent.orchestrator import SQLAgentOrchestrator


def build_orchestrator(settings: Settings) -> SQLAgentOrchestrator:
    if settings.model_provider == "openai":
        llm_provider = OpenAILLMProvider(
            model_name=settings.model_name,
            temperature=settings.temperature,
        )
    elif settings.model_provider == "huggingface":
        llm_provider = HuggingFaceLLMProvider(
            model_name=settings.model_name,
            temperature=settings.temperature,
            api_key=settings.huggingface_api_key,
            base_url=settings.huggingface_base_url,
        )
    else:
        raise ValueError(
            f"Unsupported MODEL_PROVIDER '{settings.model_provider}'. "
            "Supported values: openai, huggingface."
        )

    db_provider = LangChainSQLToolkitProvider(
        database_url=settings.database_url,
        llm=llm_provider.model,
    )

    guardrails = SQLGuardrails(
        max_rows=settings.max_rows,
        table_allowlist=set(settings.table_allowlist),
    )

    return SQLAgentOrchestrator(
        llm_provider=llm_provider,
        database_provider=db_provider,
        guardrails=guardrails,
    )
