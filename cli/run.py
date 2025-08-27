# cli/run.py
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from agent.customer_support_agent import CustomerSupportAgent


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="support-agent",
        description="Customer Support Agent (terminal runner)",
    )
    parser.add_argument(
        "--email",
        required=True,
        help="User email (used to restrict order data to the owner)",
    )
    parser.add_argument(
        "--message",
        help="Ask a single question and exit. If omitted, starts an interactive REPL.",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set in your environment.", file=sys.stderr)
        return 1

    agent = CustomerSupportAgent()

    # One-shot mode
    if args.message:
        resp = agent(user_email=args.email, message=args.message)
        print(resp["answer"])
        return 0

    # REPL mode
    print("Customer Support Agent (type 'exit' to quit)")
    try:
        while True:
            msg = input("> ").strip()
            if not msg:
                continue
            if msg.lower() in {"exit", "quit", "q"}:
                break
            resp = agent(user_email=args.email, message=msg)
            print(resp["answer"])
    except (KeyboardInterrupt, EOFError):
        print()  # newline for clean exit
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
