"""Watchlist and price-alert tracking for the Kenya Investment Explorer.

Single local watchlist (no auth, no multi-user support), tracked in
data/watchlist.json — mirrors the pattern used by data/portfolio.py.
"""

from __future__ import annotations

import json
from pathlib import Path

WATCHLIST_PATH = Path(__file__).parent / "watchlist.json"


def _default_watchlist() -> dict:
    return {"watching": [], "alerts": []}


def load_watchlist() -> dict:
    if not WATCHLIST_PATH.exists():
        wl = _default_watchlist()
        save_watchlist(wl)
        return wl
    return json.loads(WATCHLIST_PATH.read_text())


def save_watchlist(wl: dict) -> None:
    WATCHLIST_PATH.write_text(json.dumps(wl, indent=2))


def add_company(wl: dict, company: str) -> None:
    if company not in wl["watching"]:
        wl["watching"].append(company)
        save_watchlist(wl)


def remove_company(wl: dict, company: str) -> None:
    if company in wl["watching"]:
        wl["watching"].remove(company)
    wl["alerts"] = [a for a in wl["alerts"] if a["company"] != company]
    save_watchlist(wl)


def set_alert(wl: dict, company: str, target_price: float, direction: str) -> None:
    wl["alerts"] = [a for a in wl["alerts"] if a["company"] != company]
    wl["alerts"].append({"company": company, "target": target_price, "direction": direction})
    save_watchlist(wl)


def remove_alert(wl: dict, company: str) -> None:
    wl["alerts"] = [a for a in wl["alerts"] if a["company"] != company]
    save_watchlist(wl)


def check_alerts(wl: dict, price_by_company: dict[str, float]) -> list[dict]:
    triggered = []
    for a in wl["alerts"]:
        price = price_by_company.get(a["company"])
        if price is None:
            continue
        if a["direction"] == "above" and price >= a["target"]:
            triggered.append({**a, "current": price})
        elif a["direction"] == "below" and price <= a["target"]:
            triggered.append({**a, "current": price})
    return triggered
