from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class QueryResult:
    user_question: str
    sql: str
    rows: str
    summary: str


class LLMProvider(Protocol):
    def generate_sql(self, question: str, schema_context: str, max_rows: int) -> str:
        ...

    def summarize_result(self, question: str, sql: str, rows: str) -> str:
        ...


class DatabaseProvider(Protocol):
    def schema_context(self) -> str:
        ...

    def available_tables(self) -> set[str]:
        ...

    def check_query(self, sql: str) -> str:
        ...

    def execute_query(self, sql: str) -> str:
        ...
