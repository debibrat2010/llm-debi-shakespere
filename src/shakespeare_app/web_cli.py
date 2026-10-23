"""Launch the Bard web UI (uvicorn)."""

from __future__ import annotations

import os

from shakespeare_app.env import load_project_env


def main() -> None:
    load_project_env()
    import uvicorn

    host = os.environ.get("BARD_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = int(os.environ.get("BARD_PORT", "8765"))
    reload = os.environ.get("BARD_RELOAD", "").lower() in ("1", "true", "yes")

    uvicorn.run(
        "shakespeare_app.web:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
