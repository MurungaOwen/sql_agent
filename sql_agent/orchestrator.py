from __future__ import annotations

from sql_agent.guardrails import GuardrailError, SQLGuardrails
from sql_agent.interfaces import DatabaseProvider, LLMProvider, QueryResult


class SQLAgentOrchestrator:
    def __init__(
        self,
        llm_provider: LLMProvider,
        database_provider: DatabaseProvider,
        guardrails: SQLGuardrails,
    ):
        self.llm_provider = llm_provider
        self.database_provider = database_provider
        self.guardrails = guardrails

    def run(self, user_question: str) -> QueryResult:
        schema = self.database_provider.schema_context()
        raw_sql = self.llm_provider.generate_sql(
            question=user_question,
            schema_context=schema,
            max_rows=self.guardrails.max_rows,
        )

        known_tables = self.database_provider.available_tables()

        try:
            safe_sql = self.guardrails.enforce(raw_sql, known_tables=known_tables)
        except GuardrailError as err:
            repaired_sql = self._repair_sql(user_question, schema, raw_sql, str(err))
            safe_sql = self.guardrails.enforce(repaired_sql, known_tables=known_tables)

        checked_sql = self.database_provider.check_query(safe_sql)
        rows = self.database_provider.execute_query(checked_sql)
        summary = self.llm_provider.summarize_result(user_question, checked_sql, rows)

        return QueryResult(
            user_question=user_question,
            sql=checked_sql,
            rows=rows,
            summary=summary,
        )

    def _repair_sql(
        self,
        question: str,
        schema_context: str,
        previous_sql: str,
        validation_error: str,
    ) -> str:
        repair_prompt = (
            "The SQL failed guardrails. Return corrected SQL only.\n"
            f"Validation error: {validation_error}\n"
            f"Previous SQL:\n{previous_sql}\n"
            "Fix while preserving user intent."
        )
        return self.llm_provider.generate_sql(
            question=f"{question}\n\n{repair_prompt}",
            schema_context=schema_context,
            max_rows=self.guardrails.max_rows,
        )
