# Autopilot Journal

Human-readable run journal. Machine state lives in `state/`. Newest
entries at the bottom. Every scheduled run appends here and pushes.

---

## 2026-07-20 21:50 UTC — Baseline (manual setup run, market closed)

- **Account 995042041**: total value $39.07 — $0.39 settled cash,
  $38.68 crypto (untradable via MCP, owner-managed). No equity or
  option positions. No open orders.
- Reconciled `state/account_state.json` from stale $150 to reality.
  The prior-session automation lost broker access 2026-07-13; the $150
  cash it last saw is now the crypto holding.
- Owner re-authorized the system today: full autopilot in this account
  only, Standard risk profile, twice-daily weekday cadence. Details in
  TRADING_PLAYBOOK.md (v1.1); it supersedes trigger-prompt shorthand.
- Created Robinhood saved scanner "Autopilot Swing Candidates"
  (a0a9a49e-c941-4f11-8ac6-a28d6f1eccb9) — discovery only.
- Created two Routines: morning full cycle (0 14 * * 1-5 UTC) and
  afternoon exit check (30 19 * * 1-5 UTC).
- Status: **idle — insufficient cash to size any trade.** System runs
  monitor+log until the account is funded (whole share, $2–$30 price,
  2%/5% risk rules ⇒ roughly $40+ of settled cash needed for the first
  viable entry). `first_live_cycle_done` remains false: the first
  funded cycle validates data end-to-end without placing orders.
