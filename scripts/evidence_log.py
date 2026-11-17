"""Append-only action log for incident-response work.

Every script should call `log_action()` for each meaningful step so the full
timeline can later be explained to management. Entries are JSON Lines in
evidence/logs/actions-YYYYMMDD.jsonl (UTC).

Usage:
    from evidence_log import log_action, save_artifact
    log_action("query", "Listed sign-ins for user X", target="entra", read_only=True)
    save_artifact("signins.json", json_text, description="Sign-in export")
"""

from __future__ import annotations

import getpass
import hashlib
import json
import socket
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "evidence" / "logs"
ARTIFACT_DIR = ROOT / "evidence" / "artifacts"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def log_action(
    action: str,
    description: str,
    *,
    target: str = "",
    read_only: bool = True,
    **details: object,
) -> dict:
    """Record one action. Set read_only=False for anything that changes state."""
    now = _now()
    entry = {
        "timestamp_utc": now.isoformat(),
        "operator": getpass.getuser(),
        "host": socket.gethostname(),
        "action": action,
        "description": description,
        "target": target,
        "read_only": read_only,
        "details": details,
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"actions-{now:%Y%m%d}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def save_artifact(name: str, content: str | bytes, *, description: str = "") -> Path:
    """Store collected evidence with a UTC timestamp prefix and log its SHA-256."""
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data = content.encode("utf-8") if isinstance(content, str) else content
    path = ARTIFACT_DIR / f"{_now():%Y%m%dT%H%M%SZ}_{name}"
    path.write_bytes(data)
    log_action(
        "artifact_saved",
        description or f"Saved {path.name}",
        target=str(path.relative_to(ROOT)),
        sha256=hashlib.sha256(data).hexdigest(),
        bytes=len(data),
    )
    return path
