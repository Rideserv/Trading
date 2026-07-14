#!/usr/bin/env python3
"""Box Swing Strategy v1.0 — deterministic decision logic.

Pure functions over market data the agent fetches via the Robinhood MCP
tools. No network access in this module: data in, decision out. Every
number that reaches the broker is computed here, never improvised.

CLI:
    python3 box_scan.py evaluate < input.json   # flat -> entry decision
    python3 box_scan.py manage   < input.json   # open position -> action

evaluate input JSON:
    {
      "symbol": "PLUG",
      "equity": 150.0,
      "settled_cash": 150.0,
      "price": 4.31,              # live quote
      "quote_age_seconds": 12,
      "bars": [                    # DAILY bars, ascending; last = today (partial)
        {"date": "2026-06-12", "open":..., "high":..., "low":...,
         "close":..., "volume":...},
        ...
      ]
    }

manage input JSON:
    {
      "symbol": "PLUG",
      "price": 4.80,
      "quote_age_seconds": 12,
      "position": {
        "entry_price": 4.40, "shares": 3, "entry_date": "2026-07-01",
        "box_top": 4.35, "box_bottom": 4.05,
        "stop_price": 4.05, "tp_price": 4.95
      },
      "bars": [ ... daily bars ascending; last = today (partial) ... ],
      "today": "2026-07-11"
    }

Output: single JSON object on stdout. "action" is always present.
"""

import json
import math
import sys
from datetime import date

# --- Strategy constants (STRATEGY.md is the source of truth) ---------------
BOX_BARS = 20                 # completed daily bars forming the box
TOP_MIN_AGE = 10              # sessions since the box top was set (maturity)
TIGHTNESS_MAX = 0.25          # box_height / box_top ceiling
TIER1_TIGHTNESS = 0.15
VOL_MULT = 1.5                # today's cum volume vs 20-day avg (Tier 2)
TIER1_VOL_MULT = 3.0
MIN_AVG_VOLUME = 1_000_000    # shares/day, 20-day average
MIN_DOLLAR_VOLUME = 5_000_000 # $/day, 20-day average
PRICE_MIN = 2.0
PRICE_MAX = 30.0
RISK_TARGET = 0.02            # of equity
RISK_CEILING = 0.05           # absolute max, whole-share reality
TP_HEIGHT_MULT = 2.0          # TP = box_top + 2 * box_height
TIME_STOP_SESSIONS = 10       # completed sessions in trade before forced exit
EARLY_LOCK_MIN_R = 1.0        # unrealized gain (in R) before stop may rise
QUOTE_MAX_AGE_SECONDS = 300   # stale quote -> refuse to act


def skip(reason, **extra):
    return {"action": "skip", "reason": reason, **extra}


def _validate_bars(bars):
    """Bars must be ascending by date with the most recent bar last.

    The v4.0 stale-data bug is prevented by assertion, not by memory.
    """
    if not bars or len(bars) < BOX_BARS + 1:
        return f"need at least {BOX_BARS + 1} daily bars, got {len(bars or [])}"
    dates = [b["date"] for b in bars]
    if dates != sorted(dates):
        return "bars are not in ascending date order"
    if len(set(dates)) != len(dates):
        return "duplicate bar dates"
    return None


def compute_box(completed_bars):
    """Box over the last BOX_BARS completed bars. Returns (box, reject_reason)."""
    window = completed_bars[-BOX_BARS:]
    top = max(b["high"] for b in window)
    bottom = min(b["low"] for b in window)
    height = top - bottom
    if bottom <= 0 or height <= 0:
        return None, "degenerate box"
    if height / top > TIGHTNESS_MAX:
        return None, (f"box too wide: height {height / top:.1%} of top "
                      f"(max {TIGHTNESS_MAX:.0%})")
    # Maturity: the bar that set the top must be old enough that today's
    # move is a breakout of established resistance, not a continuation of
    # fresh highs.
    top_idx = max(i for i, b in enumerate(window) if b["high"] == top)
    top_age = len(window) - 1 - top_idx  # sessions since top was set
    if top_age < TOP_MIN_AGE:
        return None, (f"box not mature: top set {top_age} sessions ago "
                      f"(need >= {TOP_MIN_AGE})")
    avg_volume = sum(b["volume"] for b in window) / len(window)
    avg_dollar_volume = sum(b["volume"] * b["close"] for b in window) / len(window)
    return {
        "top": top,
        "bottom": bottom,
        "height": height,
        "avg_volume": avg_volume,
        "avg_dollar_volume": avg_dollar_volume,
    }, None


def size_position(equity, settled_cash, entry_price, stop_price):
    """Whole-share sizing. Returns (shares, reject_reason)."""
    stop_distance = entry_price - stop_price
    if stop_distance <= 0:
        return 0, "stop distance is not positive"
    shares = math.floor((equity * RISK_TARGET) / stop_distance)
    if shares == 0:
        if stop_distance <= equity * RISK_CEILING:
            shares = 1
        else:
            return 0, (f"one share risks ${stop_distance:.2f} "
                       f"(> {RISK_CEILING:.0%} of equity ${equity:.2f})")
    if shares * entry_price > settled_cash:
        shares = math.floor(settled_cash / entry_price)
    if shares == 0:
        return 0, "insufficient settled cash for one share"
    return shares, None


def evaluate(payload):
    symbol = payload.get("symbol", "?")
    equity = float(payload["equity"])
    settled_cash = float(payload["settled_cash"])
    price = float(payload["price"])
    bars = payload["bars"]

    if payload.get("quote_age_seconds", 0) > QUOTE_MAX_AGE_SECONDS:
        return skip("STALE QUOTE — refusing to act", symbol=symbol)
    err = _validate_bars(bars)
    if err:
        return skip(err, symbol=symbol)

    today_bar = bars[-1]
    completed = bars[:-1]
    box, reject = compute_box(completed)
    if reject:
        return skip(reject, symbol=symbol)

    # Liquidity floor — structural, replaces hand-maintained exclusions.
    if box["avg_volume"] < MIN_AVG_VOLUME:
        return skip(f"liquidity: avg volume {box['avg_volume']:,.0f} < "
                    f"{MIN_AVG_VOLUME:,}", symbol=symbol)
    if box["avg_dollar_volume"] < MIN_DOLLAR_VOLUME:
        return skip(f"liquidity: avg dollar volume "
                    f"${box['avg_dollar_volume']:,.0f} < ${MIN_DOLLAR_VOLUME:,}",
                    symbol=symbol)
    if not (PRICE_MIN <= price <= PRICE_MAX):
        return skip(f"price ${price:.2f} outside ${PRICE_MIN:.0f}-"
                    f"${PRICE_MAX:.0f} band", symbol=symbol)

    # Breakout trigger.
    if price <= box["top"]:
        return skip(f"no breakout: price ${price:.2f} <= box top "
                    f"${box['top']:.2f}", symbol=symbol,
                    box_top=box["top"], box_bottom=box["bottom"])

    # Volume must have ALREADY printed — no projections.
    vol_ratio = today_bar["volume"] / box["avg_volume"]
    if vol_ratio < VOL_MULT:
        return skip(f"volume {vol_ratio:.2f}x avg < {VOL_MULT}x "
                    f"(no projections — must already have printed)",
                    symbol=symbol)

    tightness = box["height"] / box["top"]
    tier = 1 if (vol_ratio >= TIER1_VOL_MULT and tightness <= TIER1_TIGHTNESS) else 2

    shares, reject = size_position(equity, settled_cash, price, box["bottom"])
    if reject:
        return skip(reject, symbol=symbol)

    stop_distance = price - box["bottom"]
    return {
        "action": "enter",
        "symbol": symbol,
        "shares": shares,
        "entry_type": "market",
        "tier": tier,
        "volume_ratio": round(vol_ratio, 2),
        "box_top": box["top"],
        "box_bottom": box["bottom"],
        "stop_price": box["bottom"],
        "tp_price": round(box["top"] + TP_HEIGHT_MULT * box["height"], 2),
        "risk_dollars": round(shares * stop_distance, 2),
        "risk_pct_of_equity": round(shares * stop_distance / equity, 4),
        "cost": round(shares * price, 2),
    }


def _sessions_in_trade(bars, entry_date, today):
    """Completed sessions strictly after entry_date, before today."""
    return sum(1 for b in bars if entry_date < b["date"] < today)


def manage(payload):
    symbol = payload.get("symbol", "?")
    price = float(payload["price"])
    pos = payload["position"]
    bars = payload["bars"]
    today = payload.get("today") or date.today().isoformat()

    if payload.get("quote_age_seconds", 0) > QUOTE_MAX_AGE_SECONDS:
        return {"action": "hold", "reason": "STALE QUOTE — no action this cycle",
                "symbol": symbol}

    # 1. Take profit — scan-enforced (Robinhood has no OCO).
    if price >= pos["tp_price"]:
        return {"action": "take_profit", "symbol": symbol,
                "reason": f"price ${price:.2f} >= TP ${pos['tp_price']:.2f}",
                "steps": ["cancel GTC stop", "sell all shares at market"]}

    # 2. Time stop.
    sessions = _sessions_in_trade(bars, pos["entry_date"], today)
    if sessions >= TIME_STOP_SESSIONS:
        return {"action": "time_exit", "symbol": symbol,
                "reason": f"{sessions} completed sessions in trade "
                          f"(max {TIME_STOP_SESSIONS}) without reaching TP",
                "steps": ["cancel GTC stop", "sell all shares at market"]}

    # 3. Early lock: >= 1R unrealized and 2-of-3 stall on the last two
    #    COMPLETED daily bars -> raise stop to breakeven-or-better.
    #    We tighten; we never bail.
    initial_risk = pos["entry_price"] - pos["box_bottom"]
    completed = [b for b in bars if b["date"] < today]
    if initial_risk > 0 and len(completed) >= 2:
        gain_r = (price - pos["entry_price"]) / initial_risk
        if gain_r >= EARLY_LOCK_MIN_R:
            y, p = completed[-1], completed[-2]
            stall = sum([
                y["close"] < y["open"],
                y["close"] < p["close"],
                y["volume"] < p["volume"],
            ])
            if stall >= 2:
                new_stop = max(pos["entry_price"], pos["box_top"])
                if new_stop > pos["stop_price"] and new_stop < price:
                    return {"action": "raise_stop", "symbol": symbol,
                            "new_stop": round(new_stop, 2),
                            "reason": f"up {gain_r:.1f}R with {stall}/3 stall "
                                      "signals — locking breakeven-or-better",
                            "steps": ["cancel GTC stop",
                                      f"place GTC stop at {new_stop:.2f}"]}

    return {"action": "hold", "symbol": symbol,
            "reason": f"price ${price:.2f}, TP ${pos['tp_price']:.2f}, "
                      f"stop ${pos['stop_price']:.2f}, "
                      f"{sessions}/{TIME_STOP_SESSIONS} sessions"}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("evaluate", "manage"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    payload = json.load(sys.stdin)
    result = evaluate(payload) if sys.argv[1] == "evaluate" else manage(payload)
    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
