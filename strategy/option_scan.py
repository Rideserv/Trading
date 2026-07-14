#!/usr/bin/env python3
"""Options overlay for Box Swing v1.0 — see OPTIONS_RESEARCH.md.

The underlying breakout signal is UNCHANGED — this module only decides
which CONTRACT expresses a setup that box_scan.evaluate() already
qualified, and how to manage/exit it. It does not re-derive the box.

STATUS: shadow-only until a real cycle validates contract selection
against live chains, same discipline as box_scan.py's first-live-cycle
gate. See OPTIONS_RESEARCH.md for why (never touched real option fills).

CLI:
    python3 option_scan.py select-contract < input.json
    python3 option_scan.py manage          < input.json

select-contract input JSON:
    {
      "equity": 150.0, "buying_power": 99.83,
      "box_result": { ... full output of box_scan.evaluate() with
                       action == "enter" ... },
      "underlying_price": 6.74,
      "contracts": [                # from get_option_instruments +
        {                           # get_option_quotes, one per strike
          "instrument_id": "...", "strike": 6.5, "expiration": "2026-08-07",
          "delta": 0.62, "bid": 0.60, "ask": 0.68, "mark": 0.64,
          "open_interest": 640, "days_to_expiration": 24
        }, ...
      ]
    }

manage input JSON:
    {
      "underlying_price": 7.40, "today": "2026-07-24",
      "position": {
        "instrument_id": "...", "contracts": 2, "entry_premium": 0.64,
        "entry_date": "2026-07-14", "box_top": 6.71, "box_bottom": 6.05,
        "tp_price": 7.97, "half_sold": false
      }
    }
"""

import json
import sys
from datetime import date

MIN_DTE = 21                  # calendar days; must clear TIME_STOP_SESSIONS
                              # with real buffer before expiration forces it
MAX_DTE = 45
TARGET_DELTA_LOW = 0.60
TARGET_DELTA_HIGH = 0.70
MIN_OPEN_INTEREST = 500
MAX_SPREAD_PCT_OF_MID = 0.10   # (ask - bid) / mid
OPTION_TIME_STOP_SESSIONS = 8  # tighter than shares' 10 — expiration risk
EARLY_LOCK_MIN_R = 1.0


def reject(reason, **extra):
    return {"action": "skip", "reason": reason, **extra}


def _liquid(contract):
    bid, ask = contract["bid"], contract["ask"]
    if bid <= 0 or ask <= 0:
        return False, "no two-sided market"
    mid = (bid + ask) / 2
    spread_pct = (ask - bid) / mid
    if contract["open_interest"] < MIN_OPEN_INTEREST:
        return False, (f"open interest {contract['open_interest']} < "
                       f"{MIN_OPEN_INTEREST}")
    if spread_pct > MAX_SPREAD_PCT_OF_MID:
        return False, f"spread {spread_pct:.1%} > {MAX_SPREAD_PCT_OF_MID:.0%} of mid"
    return True, None


def select_contract(contracts):
    """Pick the best contract: DTE window, delta window, liquidity floor.

    Returns (contract, reject_reason). Prefers delta closest to the
    midpoint of the target window among all liquid, in-window candidates.
    """
    candidates = []
    for c in contracts:
        if not (MIN_DTE <= c["days_to_expiration"] <= MAX_DTE):
            continue
        if not (TARGET_DELTA_LOW <= c["delta"] <= TARGET_DELTA_HIGH):
            continue
        ok, why = _liquid(c)
        if not ok:
            continue
        candidates.append(c)
    if not candidates:
        return None, (f"no contract in {MIN_DTE}-{MAX_DTE} DTE with delta "
                      f"{TARGET_DELTA_LOW}-{TARGET_DELTA_HIGH} passing "
                      f"liquidity floor (OI>={MIN_OPEN_INTEREST}, "
                      f"spread<={MAX_SPREAD_PCT_OF_MID:.0%})")
    target_delta = (TARGET_DELTA_LOW + TARGET_DELTA_HIGH) / 2
    candidates.sort(key=lambda c: abs(c["delta"] - target_delta))
    return candidates[0], None


def size_contracts(equity, buying_power, premium):
    risk_dollars = equity * 0.02
    contracts = int(risk_dollars // (premium * 100))
    if contracts == 0:
        return 0, (f"one contract costs ${premium * 100:.2f}, exceeds the "
                   f"${risk_dollars:.2f} risk target — no forced minimum "
                   "for options (unlike shares)")
    cost = contracts * premium * 100
    if cost > buying_power:
        contracts = int(buying_power // (premium * 100))
    if contracts == 0:
        return 0, "insufficient buying power for one contract"
    return contracts, None


def select_and_size(payload):
    box = payload["box_result"]
    if box.get("action") != "enter":
        return reject("box_result is not a qualifying entry")
    contract, why = select_contract(payload["contracts"])
    if not contract:
        return reject(why, symbol=box.get("symbol"))
    premium = contract["mark"]
    contracts, why = size_contracts(payload["equity"], payload["buying_power"],
                                    premium)
    if not contracts:
        return reject(why, symbol=box.get("symbol"))
    return {
        "action": "enter_option",
        "symbol": box.get("symbol"),
        "instrument_id": contract["instrument_id"],
        "strike": contract["strike"],
        "expiration": contract["expiration"],
        "delta": contract["delta"],
        "contracts": contracts,
        "premium": premium,
        "cost": round(contracts * premium * 100, 2),
        "tp_price": box["tp_price"],          # underlying price, unchanged
        "box_bottom": box["box_bottom"],       # underlying stop trigger
        "box_top": box["box_top"],
        "tier": box["tier"],
    }


def _sessions_in_trade(entry_date, today):
    return (date.fromisoformat(today) - date.fromisoformat(entry_date)).days


def manage(payload):
    price = float(payload["underlying_price"])
    pos = payload["position"]
    today = payload.get("today") or date.today().isoformat()

    if price <= pos["box_bottom"]:
        return {"action": "close_all",
                "reason": f"underlying ${price:.2f} <= box_bottom "
                          f"${pos['box_bottom']:.2f} — thesis invalidated"}

    if price >= pos["tp_price"]:
        return {"action": "close_all",
                "reason": f"underlying ${price:.2f} >= TP ${pos['tp_price']:.2f}"}

    days_held = _sessions_in_trade(pos["entry_date"], today)
    if days_held >= OPTION_TIME_STOP_SESSIONS:
        return {"action": "close_all",
                "reason": f"{days_held} days held >= "
                          f"{OPTION_TIME_STOP_SESSIONS}-day option time stop "
                          "(tighter than shares — expiration risk)"}

    initial_risk = pos["box_top"] - pos["box_bottom"]
    if initial_risk > 0 and not pos.get("half_sold"):
        gain_r = (price - pos["box_top"]) / initial_risk
        if gain_r >= EARLY_LOCK_MIN_R:
            return {"action": "sell_half",
                    "reason": f"up {gain_r:.1f}R — banking half, holding "
                              "rest to TP/stop (no stop order exists on a "
                              "long call to raise instead)"}

    return {"action": "hold",
            "reason": f"underlying ${price:.2f}, TP ${pos['tp_price']:.2f}, "
                      f"stop-equivalent ${pos['box_bottom']:.2f}, "
                      f"{days_held}/{OPTION_TIME_STOP_SESSIONS} days"}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("select-contract", "manage"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    payload = json.load(sys.stdin)
    result = (select_and_size(payload) if sys.argv[1] == "select-contract"
             else manage(payload))
    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
