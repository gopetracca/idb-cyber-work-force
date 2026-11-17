# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Working repository for containing and investigating an active attack on the IDB Azure tenant. Scripts are run by the operator during the incident, and every action must be traceable so it can be explained to management afterwards. The repo was bootstrapped empty; update this file as it grows.

## Environment

- Python is managed with **uv** (Python 3.13 pinned in `.python-version`). Prefer Python over PowerShell; use PowerShell only when Python is impractical.
- `uv sync` — create/refresh the environment
- `uv add <pkg>` — add a dependency (updates `pyproject.toml` and `uv.lock`)
- `uv run scripts/<script>.py` — run a script

## Layout

- `scripts/` — operational scripts. `scripts/evidence_log.py` is the shared logging helper.
- `evidence/logs/` — append-only JSONL action logs (`actions-YYYYMMDD.jsonl`, UTC).
- `evidence/artifacts/` — collected data (exports, query results), timestamp-prefixed, each with its SHA-256 recorded in the log.

## Rules for scripts

- Every script must log each meaningful step with `log_action()` (from `evidence_log`), setting `read_only=False` for anything that changes state. Save collected data with `save_artifact()` rather than ad-hoc files.
- Scripts that change Azure/Entra configuration must default to a dry run and require an explicit flag (e.g. `--apply`) to act. Treat the tenant as production: never apply changes without explicit operator confirmation in the current conversation.
- Never write secrets, tokens, or personal data into logs or artifacts; evidence may contain sensitive data, so do not share or commit it without authorization.
- Information security incidents are escalated to Fernando Puerto Mendoza (fernandopu@iadb.org).
