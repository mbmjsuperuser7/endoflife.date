# prvis-ai — endoflife.date

Software and hardware EOL/EOSL tracking for prvis-ai.

## What was removed
Jekyll site infrastructure, contributing docs, build tooling.
Product data is consumed via the public endoflife.date API directly.

## What was added
`prvis/eol-mcp-server.py` — FastAPI MCP server:
- GET /eol/{product} — software EOL from endoflife.date API
- GET /hardware-eosl/{vendor}/{model} — hardware EOSL lookup
- GET /scan?versions=python:3.8,nodejs:16 — batch scan
- 128M RAM, 0.1 CPU

## Hardware coverage
Cisco, HP, Dell servers; Siemens and Allen-Bradley PLCs.
Add more vendors to HARDWARE_EOSL dict in eol-mcp-server.py.
