"""
prvis-ai EOL MCP server
Wraps endoflife.date API + hardware EOSL data
Exposes as MCP tools for AI agent consumption
"""
import asyncio
import json
import os
from datetime import date, datetime
from typing import Optional
import httpx
from fastapi import FastAPI

app = FastAPI(title="prvis-eol-mcp")
EOL_API = "https://endoflife.date/api"

# Hardware EOSL data — vendor-provided, updated manually
# Format: product -> model -> eosl_date
HARDWARE_EOSL = {
    "cisco": {
        "ASA 5505": "2017-08-25",
        "ASA 5510": "2017-08-25",
        "Catalyst 2960": "2020-01-31",
        "Catalyst 3560": "2020-01-31",
        "ISR 1800": "2016-06-30",
    },
    "hp": {
        "ProLiant DL360 G7": "2018-06-30",
        "ProLiant DL380 G7": "2018-06-30",
        "ProLiant DL360 Gen8": "2022-01-31",
    },
    "dell": {
        "PowerEdge R610": "2016-04-11",
        "PowerEdge R710": "2016-04-11",
        "PowerEdge R720": "2020-01-31",
    },
    "siemens-plc": {
        "S7-300": "2023-10-01",
        "S7-400": "2023-10-01",
        "ET 200S": "2020-07-01",
    },
    "allen-bradley": {
        "SLC 500": "2012-12-31",
        "MicroLogix 1000": "2012-12-31",
        "PLC-5": "2014-12-31",
    },
}

@app.get("/health")
async def health(): return {"status": "ok"}

@app.get("/eol/{product}")
async def get_product_eol(product: str):
    """Get EOL data for a software product from endoflife.date."""
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{EOL_API}/{product}.json")
        if r.status_code != 200:
            return {"error": f"Product not found: {product}"}
        return r.json()

@app.get("/hardware-eosl/{vendor}/{model}")
async def get_hardware_eosl(vendor: str, model: str):
    """Get EOSL date for hardware."""
    vendor_data = HARDWARE_EOSL.get(vendor.lower(), {})
    eosl = vendor_data.get(model)
    if not eosl:
        return {"error": f"Hardware not found: {vendor} {model}"}
    eosl_date = datetime.strptime(eosl, "%Y-%m-%d").date()
    days_remaining = (eosl_date - date.today()).days
    return {
        "vendor": vendor,
        "model": model,
        "eosl_date": eosl,
        "is_eosl": days_remaining < 0,
        "days_remaining": days_remaining,
        "severity": "critical" if days_remaining < 0 else "high" if days_remaining < 90 else "medium" if days_remaining < 365 else "info"
    }

@app.get("/scan")
async def scan_versions(versions: str):
    """
    Scan a list of product:version pairs for EOL status.
    Input: "python:3.8,nodejs:16,ubuntu:20.04"
    """
    results = []
    pairs = versions.split(",")
    async with httpx.AsyncClient(timeout=10) as c:
        for pair in pairs:
            if ":" not in pair:
                continue
            product, version = pair.strip().split(":", 1)
            try:
                r = await c.get(f"{EOL_API}/{product}.json")
                if r.status_code != 200:
                    continue
                cycles = r.json()
                for cycle in cycles:
                    if str(cycle.get("cycle","")).startswith(version.split(".")[0]):
                        eol = cycle.get("eol")
                        is_eol = eol == "true" or eol is True
                        results.append({
                            "product": product,
                            "version": version,
                            "cycle": cycle.get("cycle"),
                            "eol_date": eol if isinstance(eol, str) and eol != "true" else None,
                            "is_eol": is_eol,
                        })
                        break
            except Exception:
                pass
    return results
