# Ledger Lens SQL Agent

Natural-language SQL assistant built with LangChain. It exposes:

- A web UI (`/`) for non-technical users
- One API endpoint (`POST /api/ask`) for integrations
- A CLI for quick local testing

The architecture is intentionally decoupled so model provider and database/provider logic can be swapped independently.

## What You Get

- Natura Language -> SQL generation against your live schema
- Read-focused SQL guardrails
- SQL query checking before execution
- Results + human summary in one response
- Provider abstraction (`openai`, `huggingface`)
- Database abstraction (`SQLDatabaseToolkit` wrapped behind `DatabaseProvider`)

## Tech Stack

- Python 3.13+
- FastAPI + Uvicorn
- LangChain + LangChain Community + LangChain OpenAI
- SQLAlchemy (+ psycopg for Postgres)

## Quickstart (5 Minutes)

### 1. Clone and install deps

```bash
git clone https://github.com/MurungaOwen/sql_agent.git
cd sql_agent
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

- Set `DATABASE_URL`
- Pick provider (`MODEL_PROVIDER=openai` or `huggingface`)
- Set matching API key

### 3. Run the web app

```bash
uv run uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`.

### UI Preview

![Ledger Lens UI](web/assets/demo.png)

### 4. Ask a question

Example:

- "Who are the top 10 customers by total transaction amount?"

## API Usage

### Endpoint

- `POST /api/ask`

### Request

```json
{
  "question": "Who are the top transactionists this month?"
}
```

### Response

```json
{
  "question": "Who are the top transactionists this month?",
  "sql": "SELECT ... LIMIT 100;",
  "rows": "[(...)]",
  "summary": "Top customers by amount are ..."
}
```

### cURL

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Show daily transaction count for the last 30 days"}'
```

## CLI Usage

```bash
uv run python main.py "top 5 customers by revenue"
uv run python main.py "monthly sales for 2025" --json
```

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | - | SQLAlchemy database URL |
| `MODEL_PROVIDER` | No | `openai` | `openai` or `huggingface` |
| `MODEL_NAME` | No | `gpt-4o-mini` | Model ID for selected provider |
| `MODEL_TEMPERATURE` | No | `0` | Generation temperature |
| `OPENAI_API_KEY` | If OpenAI | - | OpenAI key |
| `HUGGINGFACE_API_KEY` | If HF | - | Hugging Face token |
| `HUGGINGFACE_BASE_URL` | No | `https://router.huggingface.co/v1` | HF OpenAI-compatible endpoint |
| `MAX_ROWS` | No | `100` | Auto-limit appended if missing |
| `TABLE_ALLOWLIST` | No | empty | Comma-separated allowed tables |

## Provider Setup

### OpenAI

```env
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=your_key
```

### Hugging Face (OpenAI-compatible)

```env
MODEL_PROVIDER=huggingface
MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct
HUGGINGFACE_API_KEY=your_hf_token
HUGGINGFACE_BASE_URL=https://router.huggingface.co/v1
```

Important: If `MODEL_PROVIDER=huggingface`, do not use `gpt-4o-mini` as `MODEL_NAME`.

## Database URL Examples

- SQLite: `sqlite:///example.db`
- Postgres: `postgresql+psycopg://postgres:postgres@localhost:5432/bank`
- MySQL: `mysql+pymysql://user:pass@localhost:3306/dbname`

## Project Structure

```text
app.py                      # FastAPI app + API + UI serving
main.py                     # CLI entrypoint
sql_agent/
  config.py                 # env parsing (.env auto-load)
  interfaces.py             # LLMProvider / DatabaseProvider contracts
  orchestrator.py           # core orchestration flow
  guardrails.py             # read-only + table-scope + limit enforcement
  factory.py                # provider wiring from settings
  adapters/
    llm.py                  # OpenAI and HuggingFace providers
    database.py             # SQLDatabaseToolkit adapter
web/
  index.html
  assets/
    styles.css
    app.js
```

## Request Flow

1. Load schema context from DB tools
2. Generate SQL from question
3. Enforce guardrails
4. Check SQL with toolkit checker
5. Execute SQL
6. Summarize result

If guardrails fail, one repair attempt is performed.

## Guardrails

- Only `SELECT`/`WITH` queries allowed
- Blocks write/DDL keywords (`INSERT`, `UPDATE`, `DELETE`, etc.)
- Optional table allowlist enforcement
- Applies `LIMIT MAX_ROWS` if query has no limit

## Troubleshooting

### `DATABASE_URL (or DB_URL) is required`

- Ensure `.env` exists in project root
- Ensure it contains `DATABASE_URL=...`
- Ensure you run commands from repository root

### `Unsupported MODEL_PROVIDER '...'`

- Use `openai` or `huggingface`

### Hugging Face provider fails

- Set `HUGGINGFACE_API_KEY`
- Use an HF model id (for example `meta-llama/Llama-3.3-70B-Instruct`)
- Keep `HUGGINGFACE_BASE_URL=https://router.huggingface.co/v1` unless intentionally overriding

### Postgres connection errors

- Verify host/port/db/user/password in `DATABASE_URL`
- Ensure Postgres is running and reachable
- Confirm credentials and DB permissions

## Development Notes

- Orchestrator logic is provider-agnostic and database-agnostic by design.
- Add new providers by implementing `LLMProvider` and registering in `sql_agent/factory.py`.
- Add new DB strategies by implementing `DatabaseProvider` and registering in `sql_agent/factory.py`.

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```
