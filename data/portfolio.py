"""Simulated paper-trading portfolio for the Kenya Investment Explorer.

Phase 2 of the live-data + trading roadmap: a single local virtual portfolio
(no auth, no multi-user support) that lets the user "buy" and "sell" shares
against the prices in data/companies.json, tracked in data/portfolio.json.

This is NOT real brokered trading — no order is ever sent anywhere, no real
money moves. See data/fetch_prices.py for where the prices this trades
against come from.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PORTFOLIO_PATH = Path(__file__).parent / "portfolio.json"
STARTING_CASH = 1_000_000.0  # KES — arbitrary virtual starting balance


def _default_portfolio() -> dict:
    return {"startingCash": STARTING_CASH, "cash": STARTING_CASH, "holdings": [], "trades": []}


def load_portfolio() -> dict:
    if not PORTFOLIO_PATH.exists():
        portfolio = _default_portfolio()
        save_portfolio(portfolio)
        return portfolio
    return json.loads(PORTFOLIO_PATH.read_text())


def save_portfolio(portfolio: dict) -> None:
    PORTFOLIO_PATH.write_text(json.dumps(portfolio, indent=2))


def reset_portfolio() -> dict:
    portfolio = _default_portfolio()
    save_portfolio(portfolio)
    return portfolio


def _find_holding(portfolio: dict, company: str) -> dict | None:
    for h in portfolio["holdings"]:
        if h["company"] == company:
            return h
    return None


@dataclass
class TradeResult:
    ok: bool
    message: str


def buy(portfolio: dict, company: str, shares: float, price: float) -> TradeResult:
    if shares <= 0:
        return TradeResult(False, "Shares must be greater than zero.")
    cost = shares * price
    if cost > portfolio["cash"]:
        return TradeResult(False, f"Insufficient cash: need KES {cost:,.2f}, have KES {portfolio['cash']:,.2f}.")

    holding = _find_holding(portfolio, company)
    if holding is None:
        portfolio["holdings"].append({"company": company, "shares": shares, "avgCost": price})
    else:
        total_shares = holding["shares"] + shares
        holding["avgCost"] = (holding["avgCost"] * holding["shares"] + cost) / total_shares
        holding["shares"] = total_shares

    portfolio["cash"] -= cost
    _log_trade(portfolio, company, "BUY", shares, price, cost)
    save_portfolio(portfolio)
    return TradeResult(True, f"Bought {shares:g} share(s) of {company} at KES {price:,.2f} for KES {cost:,.2f}.")


def sell(portfolio: dict, company: str, shares: float, price: float) -> TradeResult:
    if shares <= 0:
        return TradeResult(False, "Shares must be greater than zero.")
    holding = _find_holding(portfolio, company)
    if holding is None or shares > holding["shares"]:
        held = holding["shares"] if holding else 0
        return TradeResult(False, f"You only hold {held:g} share(s) of {company}.")

    proceeds = shares * price
    holding["shares"] -= shares
    if holding["shares"] <= 0:
        portfolio["holdings"].remove(holding)

    portfolio["cash"] += proceeds
    _log_trade(portfolio, company, "SELL", shares, price, proceeds)
    save_portfolio(portfolio)
    return TradeResult(True, f"Sold {shares:g} share(s) of {company} at KES {price:,.2f} for KES {proceeds:,.2f}.")


def _log_trade(portfolio: dict, company: str, action: str, shares: float, price: float, total: float) -> None:
    portfolio["trades"].append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "company": company,
            "action": action,
            "shares": shares,
            "price": price,
            "total": total,
            "cashAfter": portfolio["cash"],
        }
    )


def holdings_market_value(portfolio: dict, price_by_company: dict[str, float]) -> float:
    return sum(h["shares"] * price_by_company.get(h["company"], h["avgCost"]) for h in portfolio["holdings"])
