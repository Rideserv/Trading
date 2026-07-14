#!/usr/bin/env python3
"""Circuit breaker + account state for Box Swing v1.0.

Reads/writes state/account_state.json. FAIL CLOSED: any error reading
state means trading is blocked. The agent runs `check` at the top of
every scan cycle and must stop immediately unless it prints
{"trading_allowed": true}.

Cash is NOT tracked internally. An owner trading manually in parallel
(as happened Jul 13-14, 2026) makes any internally-tracked settled/
unsettled ledger drift from reality. Instead, `sync` records the live
`buying_power` figure pulled fresh from get_portfolio every cycle —
Robinhood already computes T+1 settlement correctly, so we just read
its answer rather than re-deriving it ourselves.

CLI:
    python3 circuit_breaker.py check [--today YYYY-MM-DD]
    python3 circuit_breaker.py record-result --outcome win|loss|flat \
        --symbol SYM [--today YYYY-MM-DD]
    python3 circuit_breaker.py sync --equity 150.73 --buying-power 99.83
    python3 circuit_breaker.py set-mode --mode shadow|live
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
    p.add_argument("command", choices=["check", "record-result", "sync",
                                       "set-mode"])
    p.add_argument("--mode", choices=["shadow", "live"])
    p.add_argument("--outcome", choices=["win", "loss", "flat"])
    p.add_argument("--symbol")
    p.add_argument("--equity", type=float)
    p.add_argument("--buying-power", type=float, dest="buying_power")
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
            "buying_power": state.get("buying_power"),
            "buying_power_synced_at": state.get("buying_power_synced_at"),
            "first_live_cycle_done": state.get("first_live_cycle_done", False),
        }, indent=2))
        sys.exit(0 if allowed else 1)

    if args.command == "record-result":
        if not args.outcome or not args.symbol:
            fail_closed("record-result requires --outcome and --symbol")
        record_result(state, args.outcome, args.symbol, args.today)
    elif args.command == "sync":
        if args.equity is None or args.buying_power is None:
            fail_closed("sync requires --equity and --buying-power (live, "
                       "from get_portfolio — never estimated)")
        state["equity"] = args.equity
        state["buying_power"] = args.buying_power
        state["buying_power_synced_at"] = (
            __import__("datetime").datetime.utcnow().isoformat() + "Z")
        save_state(state)
    elif args.command == "set-mode":
        if not args.mode:
            fail_closed("set-mode requires --mode shadow|live")
        state["mode"] = args.mode
        save_state(state)

    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
