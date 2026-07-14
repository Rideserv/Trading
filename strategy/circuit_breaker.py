#!/usr/bin/env python3
"""Circuit breaker + settlement state for Box Swing v1.0.

Reads/writes state/account_state.json. FAIL CLOSED: any error reading
state means trading is blocked. The agent runs `check` at the top of
every scan cycle and must stop immediately unless it prints
{"trading_allowed": true}.

CLI:
    python3 circuit_breaker.py check [--today YYYY-MM-DD]
    python3 circuit_breaker.py record-result --outcome win|loss|flat \
        --symbol SYM [--today YYYY-MM-DD]
    python3 circuit_breaker.py set-equity --equity 150.00
    python3 circuit_breaker.py settle-cash --amount 12.34   # T+1 arrival
    python3 circuit_breaker.py spend-cash --amount 12.34    # on a buy fill
    python3 circuit_breaker.py add-unsettled --amount 12.34 # on a sell fill
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent / "state" / "account_state.json"

CONSECUTIVE_LOSS_LIMIT = 3
BENCH_LOSS_LIMIT = 3
DRAWDOWN_STOP_EQUITY = 105.00  # -30% from $150 start: full stop, owner review


def fail_closed(msg):
    print(json.dumps({"trading_allowed": False, "reason": f"FAIL CLOSED: {msg}"}))
    sys.exit(1)


def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except Exception as e:  # unreadable state = suspended, no exceptions
        fail_closed(f"cannot read {STATE_PATH}: {e}")


def save_state(state):
    tmp = STATE_PATH.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    tmp.replace(STATE_PATH)


def check(state, today):
    if state.get("drawdown_stop"):
        return False, ("DRAWDOWN STOP active (equity fell below "
                       f"${DRAWDOWN_STOP_EQUITY:.2f}). Owner must review and "
                       "explicitly re-authorize. No override.")
    suspended_until = state.get("suspended_until")
    if suspended_until:
        if today <= suspended_until:
            return False, f"suspended until {suspended_until} (3 consecutive losses)"
        # Suspension served — reset.
        state["suspended_until"] = None
        state["consecutive_losses"] = 0
        save_state(state)
    if float(state.get("equity", 0)) <= DRAWDOWN_STOP_EQUITY:
        state["drawdown_stop"] = True
        save_state(state)
        return False, ("equity ${:.2f} <= ${:.2f} — DRAWDOWN STOP engaged. "
                       "Owner review required.").format(
                           float(state["equity"]), DRAWDOWN_STOP_EQUITY)
    return True, "clear"


def record_result(state, outcome, symbol, today):
    if outcome == "win":
        state["consecutive_losses"] = 0
        state.setdefault("bench", {}).pop(symbol, None)
    else:  # loss and flat both count against the streak (v4.0 rule kept)
        state["consecutive_losses"] = state.get("consecutive_losses", 0) + 1
        bench = state.setdefault("bench", {})
        bench[symbol] = bench.get(symbol, 0) + 1
    if state["consecutive_losses"] >= CONSECUTIVE_LOSS_LIMIT:
        tomorrow = (date.fromisoformat(today) + timedelta(days=1)).isoformat()
        state["suspended_until"] = tomorrow
    save_state(state)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["check", "record-result", "set-equity",
                                       "settle-cash", "spend-cash",
                                       "add-unsettled", "set-mode"])
    p.add_argument("--mode", choices=["shadow", "live"])
    p.add_argument("--outcome", choices=["win", "loss", "flat"])
    p.add_argument("--symbol")
    p.add_argument("--equity", type=float)
    p.add_argument("--amount", type=float)
    p.add_argument("--today", default=date.today().isoformat())
    args = p.parse_args()

    state = load_state()

    if args.command == "check":
        allowed, reason = check(state, args.today)
        benched = [s for s, n in state.get("bench", {}).items()
                   if n >= BENCH_LOSS_LIMIT]
        print(json.dumps({
            "trading_allowed": allowed,
            "reason": reason,
            "mode": state.get("mode", "shadow"),  # missing mode = shadow
            "benched_symbols": sorted(benched),
            "consecutive_losses": state.get("consecutive_losses", 0),
            "equity": state.get("equity"),
            "settled_cash": state.get("settled_cash"),
            "unsettled_cash": state.get("unsettled_cash", 0),
        }, indent=2))
        sys.exit(0 if allowed else 1)

    if args.command == "record-result":
        if not args.outcome or not args.symbol:
            fail_closed("record-result requires --outcome and --symbol")
        record_result(state, args.outcome, args.symbol, args.today)
    elif args.command == "set-equity":
        state["equity"] = args.equity
        save_state(state)
    elif args.command == "settle-cash":
        state["unsettled_cash"] = max(
            0.0, round(state.get("unsettled_cash", 0) - args.amount, 2))
        state["settled_cash"] = round(
            state.get("settled_cash", 0) + args.amount, 2)
        save_state(state)
    elif args.command == "spend-cash":
        if args.amount > state.get("settled_cash", 0) + 0.005:
            fail_closed("attempted to spend more than settled cash")
        state["settled_cash"] = round(state["settled_cash"] - args.amount, 2)
        save_state(state)
    elif args.command == "add-unsettled":
        state["unsettled_cash"] = round(
            state.get("unsettled_cash", 0) + args.amount, 2)
        save_state(state)
    elif args.command == "set-mode":
        if not args.mode:
            fail_closed("set-mode requires --mode shadow|live")
        state["mode"] = args.mode
        save_state(state)

    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
