"""Load and summarize the agent's state files.

Read-only mirror of what circuit_breaker.py computes: this module NEVER
writes state and NEVER talks to the broker. Fail closed like the rest of
the system — an unreadable state file reports trading_allowed=False.
"""

import json
from datetime import date
from pathlib import Path

CONSECUTIVE_LOSS_LIMIT = 3
RUN_LOG_TAIL = 25


def _read_json(path, fallback):
    try:
        with open(path) as f:
            return json.load(f), None
    except Exception as e:
        return fallback, f"{path.name}: {e}"


def load_status(root, today=None):
    """Build the full dashboard payload from the state directory under root."""
    root = Path(root)
    state_dir = root / "state"
    today = today or date.today().isoformat()
    errors = []

    account, err = _read_json(state_dir / "account_state.json", {})
    if err:
        errors.append(err)
    trades, err = _read_json(state_dir / "trade_log.json", [])
    if err:
        errors.append(err)

    run_log = []
    try:
        lines = (state_dir / "run_log.txt").read_text().splitlines()
        run_log = [ln for ln in lines if ln.strip()][-RUN_LOG_TAIL:]
    except Exception as e:
        errors.append(f"run_log.txt: {e}")

    suspended_until = account.get("suspended_until")
    reasons = []
    if errors:
        reasons.append("state unreadable (fail closed)")
    if account.get("drawdown_stop"):
        reasons.append("drawdown stop — owner review required")
    if suspended_until and suspended_until >= today:
        reasons.append(f"suspended until {suspended_until}")
    if account.get("consecutive_losses", 0) >= CONSECUTIVE_LOSS_LIMIT:
        reasons.append(f"{account['consecutive_losses']} consecutive losses")

    bench = account.get("bench") or {}
    benched = sorted(
        sym for sym, b in bench.items()
        if isinstance(b, dict) and b.get("losses", 0) >= CONSECUTIVE_LOSS_LIMIT
    )

    return {
        "as_of": today,
        "account": account,
        "trading_allowed": not reasons,
        "blocked_reasons": reasons,
        "benched_symbols": benched,
        "trades": trades if isinstance(trades, list) else [],
        "run_log": run_log,
        "errors": errors,
    }
