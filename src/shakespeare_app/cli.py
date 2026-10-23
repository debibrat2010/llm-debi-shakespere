from __future__ import annotations

import argparse
import sys

from shakespeare_app.env import load_project_env
from shakespeare_app.translate import to_shakespeare


def main() -> None:
    load_project_env()
    parser = argparse.ArgumentParser(
        description="Convert modern English to Shakespearean-style English (OpenAI).",
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="Words or sentences to convert. If omitted, read from stdin.",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Read lines from stdin until EOF (same as piping; useful when no args).",
    )
    args = parser.parse_args()
    raw = " ".join(args.text).strip() if args.text else ""
    if raw:
        text = raw
    elif args.interactive or not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.print_help()
        print("\nError: provide TEXT arguments or pipe input on stdin.", file=sys.stderr)
        sys.exit(2)
        return

    text = text.strip()
    if not text:
        sys.exit(0)

    try:
        out = to_shakespeare(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
        return

    print(out)


if __name__ == "__main__":
    main()
