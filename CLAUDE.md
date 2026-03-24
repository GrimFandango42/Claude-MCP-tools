# CLAUDE.md

This repository is an **archived collection of MCP servers** (superseded by OpenClaw skills and Desktop Commander as of 2026-02-14) that now serves as a **Claude Code skills collection**.

## Repository Status

The 14 MCP servers in `servers/` are archived reference implementations. Active development happens in other repos. This repo's current purpose is housing Claude Code skills in `.claude/skills/`.

## Installed Skills

### /last30days (v2.9.5)
Deep research engine — searches Reddit, X, YouTube, TikTok, Instagram, Hacker News, Polymarket, Bluesky, Truth Social, and web for the past 30 days. Supports one-shot research, comparisons, watchlist tracking, and briefings.

- **Location**: `.claude/skills/last30days/`
- **Core script**: `scripts/last30days.py`
- **Watchlist/briefing**: `scripts/watchlist.py`, `scripts/briefing.py`, `scripts/store.py`
- **Database**: `~/.local/share/last30days/research.db` (auto-created)
- **Briefing archives**: `~/.local/share/last30days/briefs/`
- **Required env**: `SCRAPECREATORS_API_KEY`
- **Optional env**: `OPENAI_API_KEY`, `XAI_API_KEY`, `OPENROUTER_API_KEY`, `BRAVE_API_KEY`, `APIFY_API_TOKEN`, `AUTH_TOKEN`, `CT0`, `BSKY_HANDLE`, `BSKY_APP_PASSWORD`, `TRUTHSOCIAL_TOKEN`

### /mychart (v1.0.0)
Patient-authorized access to MyChart/Epic health records via FHIR R4. OAuth2+PKCE authentication with multi-organization support.

- **Location**: `.claude/skills/mychart/`
- **Core scripts**: `scripts/mychart.py`, `scripts/auth.py`
- **Database**: `~/.local/share/mychart/mychart.db` (tokens + org configs, auto-created)
- **Optional env**: `EPIC_CLIENT_ID` (not needed for sandbox testing)
- **Modes**: `connect`, `orgs`, `labs`, `meds`, `conditions`, `allergies`, `vitals`, `patient`, `summary`

## Archived MCP Servers (Reference Only)

The `servers/` directory contains 14 MCP servers built with FastMCP over stdio. Key patterns if referencing them:
- All log to stderr (stdout reserved for JSON-RPC)
- Structured JSON logging via `python-json-logger`
- Registered in `claude_desktop_config.json` variants at repo root
- See individual `README.md` files in each server directory for details
