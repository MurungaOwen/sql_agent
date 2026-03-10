from __future__ import annotations

import re


class GuardrailError(ValueError):
    pass


class SQLGuardrails:
    _WRITE_KEYWORDS = re.compile(
        r"\b(insert|update|delete|drop|alter|truncate|grant|revoke|create|replace)\b",
        re.IGNORECASE,
    )

    _TABLE_PATTERN = re.compile(r"\b(?:from|join)\s+([a-zA-Z_][\w\.]*)", re.IGNORECASE)

    def __init__(self, max_rows: int, table_allowlist: set[str] | None = None):
        self.max_rows = max_rows
        self.table_allowlist = table_allowlist or set()

    def enforce(self, sql: str, known_tables: set[str]) -> str:
        normalized = self._normalize(sql)

        if not normalized.lower().startswith(("select", "with")):
            raise GuardrailError("Only SELECT/CTE read queries are allowed.")

        if self._WRITE_KEYWORDS.search(normalized):
            raise GuardrailError("Write/DDL SQL keywords are not allowed.")

        referenced = self._extract_referenced_tables(normalized)
        if referenced:
            valid_tables = known_tables
            if self.table_allowlist:
                valid_tables = valid_tables.intersection(self.table_allowlist)

            illegal = {t for t in referenced if t not in valid_tables}
            if illegal:
                raise GuardrailError(
                    f"Query references tables outside allowed scope: {sorted(illegal)}"
                )

        if self.max_rows > 0 and " limit " not in f" {normalized.lower()} ":
            normalized = f"{normalized.rstrip(';')} LIMIT {self.max_rows};"

        return normalized

    def _normalize(self, sql: str) -> str:
        sql = sql.strip()
        if sql.startswith("```"):
            sql = sql.strip("`")
            if sql.lower().startswith("sql"):
                sql = sql[3:]
        return sql.strip()

    def _extract_referenced_tables(self, sql: str) -> set[str]:
        refs = set()
        for match in self._TABLE_PATTERN.findall(sql):
            refs.add(match.split(".")[-1].strip('"'))
        return refs
