from __future__ import annotations

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

from sql_agent.interfaces import DatabaseProvider


class LangChainSQLToolkitProvider(DatabaseProvider):
    def __init__(self, database_url: str, llm):
        self.db = SQLDatabase.from_uri(database_url)
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=llm)

        tool_map = {tool.name: tool for tool in self.toolkit.get_tools()}
        self._query_tool = tool_map["sql_db_query"]
        self._schema_tool = tool_map["sql_db_schema"]
        self._list_tool = tool_map["sql_db_list_tables"]
        self._checker_tool = tool_map["sql_db_query_checker"]

    def available_tables(self) -> set[str]:
        raw = self._list_tool.invoke("")
        if isinstance(raw, str):
            return {t.strip() for t in raw.split(",") if t.strip()}
        return set(self.db.get_usable_table_names())

    def schema_context(self) -> str:
        tables = sorted(self.available_tables())
        if not tables:
            return "No usable tables found."
        table_csv = ", ".join(tables)
        schema_details = self._schema_tool.invoke(table_csv)
        return f"Tables: {table_csv}\n\nSchema details:\n{schema_details}"

    def check_query(self, sql: str) -> str:
        checked = self._checker_tool.invoke(sql)
        return checked.strip() if isinstance(checked, str) else sql

    def execute_query(self, sql: str) -> str:
        result = self._query_tool.invoke(sql)
        return result if isinstance(result, str) else str(result)
