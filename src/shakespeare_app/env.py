"""Load environment variables from the project `.env` file.

`python-dotenv`'s default `load_dotenv()` only walks up from the *current working
directory*. When `bard-web` or `bard` is started from another folder, the key
in the repo's `.env` is missed. We always try the repo root next to `src/`
first (where this package lives in development).
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


def load_project_env() -> None:
    """Load ``.env`` from the repository root, then apply default cwd-based search."""
    pkg_dir = Path(__file__).resolve().parent
    repo_root = pkg_dir.parent.parent
    load_dotenv(repo_root / ".env")
    load_dotenv()
