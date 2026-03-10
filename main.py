from __future__ import annotations

import argparse
import json

from sql_agent.config import Settings
from sql_agent.factory import build_orchestrator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Natural language SQL agent")
    parser.add_argument("question", type=str, help="Natural language question")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print result as JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings.from_env()
    orchestrator = build_orchestrator(settings)

    result = orchestrator.run(args.question)
    if args.json:
        print(json.dumps(result.__dict__, indent=2))
        return

    print(f"Question: {result.user_question}")
    print(f"\nSQL:\n{result.sql}")
    print(f"\nRows:\n{result.rows}")
    print(f"\nSummary:\n{result.summary}")


if __name__ == "__main__":
    main()
