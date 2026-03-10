from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str
    model_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    huggingface_api_key: str | None = None
    huggingface_base_url: str = "https://router.huggingface.co/v1"
    max_rows: int = 100
    table_allowlist: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> "Settings":
        _load_dotenv_file(".env")
        database_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
        if not database_url:
            raise ValueError("DATABASE_URL (or DB_URL) is required")

        allowlist = tuple(
            t.strip() for t in os.getenv("TABLE_ALLOWLIST", "").split(",") if t.strip()
        )

        return cls(
            database_url=database_url,
            model_provider=os.getenv("MODEL_PROVIDER", "openai").lower(),
            model_name=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0")),
            huggingface_api_key=(
                os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
            ),
            huggingface_base_url=os.getenv(
                "HUGGINGFACE_BASE_URL", "https://router.huggingface.co/v1"
            ),
            max_rows=int(os.getenv("MAX_ROWS", "100")),
            table_allowlist=allowlist,
        )


def _load_dotenv_file(path: str) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
