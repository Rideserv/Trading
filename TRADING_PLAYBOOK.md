# TRADING_PLAYBOOK — Autopilot Entry Point (v1.1)

This file is the top-level authority for scheduled autopilot runs. If a
trigger prompt conflicts with this file, **this file wins**. Strategy
detail: `STRATEGY.md` (Box Swing v1.0 + v1.1 amendments). Mechanical
sequence: `RUNBOOK.md`.

## Standing authorization (owner, 2026-07-20)

- **Full autopilot**: the agent may place equity orders in Robinhood
  account 995042041 ("Agentic") without per-trade confirmation, inside
  the caps below.
- Accounts ••••3178 (margin) and ••••2276 (Roth IRA): **never touch**.
- Equities (stocks/ETFs) only. No options, no crypto, nothing else
  without new explicit authorization. (Crypto tools are not available
  via MCP anyway — the owner manages the existing crypto holding in the
  Robinhood app.)
- Cadence: twice each weekday.
  - ~10:00 AM ET — full cycle (reconcile, manage exits, entry scan)
  - ~3:30 PM ET — exit management only, no new entries
  - Crons run 14:00 / 19:30 UTC. When US DST ends (Nov 1, 2026), these
    fire an hour early in ET; shift crons +1h then.

## Risk caps — intersection of the owner-approved "Standard" profile and
## Box Swing v1.0 (the most conservative rule always wins)

- **One open position at a time** (v1.0; revisit at $500 equity).
- Position cost ≤ 50% of total account value (Standard profile).
- Risk per trade: 2% of equity target, 5% hard ceiling, via the v1.0
  sizing formula. A setup that can't be sized inside 5% risk is skipped.
- **Exits are structural** per STRATEGY.md — GTC stop at box bottom
  (placed broker-side in the same cycle as entry), take-profit at
  box_top + 2× box height, 10-trading-day time stop, early-lock rule.
  These supersede the generic +5% / −3% / 5-day thresholds written into
  the trigger prompts.
- Pause all new entries if equity is down ≥ 10% over 5 trading days
  (Standard) **or** any v1.0 circuit breaker trips (3 consecutive
  losses; per-symbol bench; −30% drawdown full stop). Fail closed:
  unreadable state = suspended.
- Cash account: buy with settled funds only, track T+1 settlement, never
  risk a Good Faith Violation.
- Universe: the fixed list in RUNBOOK.md only. The saved scanner
  "Autopilot Swing Candidates" (scan_id
  a0a9a49e-c941-4f11-8ac6-a28d6f1eccb9) is **discovery/watchlist
  material only** — its hits are journaled, never traded, unless the
  owner adds them to the universe.
- The go-live validation gate (RUNBOOK Step 6.6,
  `first_live_cycle_done`) still applies before the first real order.

## Current reality (2026-07-20)

- Tradable cash: **$0.39**. Crypto holding ($38.68) is invisible to the
  agent's trading tools. Until buying power supports a whole share
  inside the sizing rules, runs are **monitor + log only** — that is
  expected behavior, not a failure.
- Prior-session automation (branch `claude/robinhood-trading-mcp-4vlevg`,
  merged in PR #3) lost broker access 2026-07-13 and went dark. Its
  hourly triggers may or may not still exist; if a run notices commits
  or orders it didn't make, stop and report to the owner immediately.

## Logging (every run, no exceptions)

- Append a dated entry to `AUTOPILOT_LOG.md` (human-readable journal:
  account value, buying power, positions, actions and why).
- Machine state stays in `state/` (`account_state.json`,
  `trade_log.json`, `run_log.txt`) per RUNBOOK.
- Commit and push to branch `claude/robinhood-trading-tools-access-no4817`.
  Containers are ephemeral: uncommitted state is deleted state.

## Reporting

Alert the owner only on: order placed, position closed, stop moved,
breaker/suspension change, or a new problem. Quiet runs get a one-line
status reply at most. Never re-announce an unchanged situation.
