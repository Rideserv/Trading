# RUNBOOK — Box Swing v1.0 Scan Cycle

This is the exact protocol the agent follows on every scheduled run.
STRATEGY.md defines the rules; this file defines the mechanical sequence.
Run the steps IN ORDER. Never skip. Fail closed on any doubt.

## Universe (scan order)

BBAI SOUN IONQ QUBT RGTI QBTS SMR UROY DNN UEC LTBR ASPI NXE UUUU
NVTS BW PLUG BLDP MARA RIOT CLSK WULF CIFR CORZ

Account: 995042041 (Robinhood "Agentic"). Never touch any other account.

## Step 0 — Preconditions

- `git pull origin claude/robinhood-trading-mcp-4vlevg` first: state files in
  git are the durable memory; containers are ephemeral.
- If Robinhood MCP tools are unavailable or unauthenticated: log one line to
  `state/run_log.txt` ("no broker connection"), commit, stop. Do NOT retry
  auth. Notify the owner ONLY if this is a new problem (wasn't the case on
  the previous run).
- Weekend/holiday: if no fresh quotes print (market closed), log and stop.

## Step 1 — Circuit breaker check (fail closed)

    python3 strategy/circuit_breaker.py check

If `trading_allowed` is false: no scanning, no orders, no exceptions.
Log the reason. Notify owner only if the state CHANGED this run.
Note `benched_symbols` — exclude them from Step 6.

## Step 2 — Reconcile (broker is source of truth)

- `get_equity_orders` + `get_equity_positions` + `get_portfolio` for 995042041.
- Update `state/account_state.json` equity via `set-equity` (use portfolio
  total_value).
- Cross-check `state/trade_log.json`: any 'entry' row without a matching
  broker fill -> add note "VOID", points 0.
- Any position closed since last run (stop filled): log the 'exit' row with
  the real fill price, then `record-result` with win/loss/flat and the symbol.
- T+1 settlement: any sale that happened on a prior trading day ->
  `settle-cash --amount <proceeds>`.

## Step 3 — Verify the stop (fire alarm check)

If a position exists with NO live GTC stop order: place the stop NOW at the
journaled stop price (`place_equity_order`: sell, stop, GTC), before
anything else. A naked position outranks every other step.

## Step 4 — Manage open position (if any)

Fetch daily bars (25+) and a live quote for the held symbol. Build the
manage payload from the journal row and run:

    python3 strategy/box_scan.py manage < payload.json

- `take_profit` / `time_exit`: cancel the GTC stop FIRST (`cancel_equity_order`),
  confirm cancelled, then sell all shares at market. Log the exit row
  immediately. `add-unsettled` the proceeds. `record-result`.
- `raise_stop`: cancel stop, place new GTC stop at `new_stop`. Update the
  journal row's stop_price. Never lower a stop. Ever.
- `hold`: nothing. No notification.

While a position is open, skip Step 6 (one position at a time).

## Step 5 — Settled cash gate

Entries require settled cash >= cost. `spend-cash` enforces this and fails
closed. Never buy with unsettled funds.

## Step 6 — Entry scan (only if flat and Steps 1-5 clear)

For each universe symbol not benched:
1. `get_equity_quotes` — skip symbol if quote stale (> 5 min) or price
   outside $2-$30.
2. Cheap pre-filter: skip if price <= prior 20-day high (no breakout, no
   need for full bars).
3. Otherwise fetch 21+ daily bars (`get_equity_historicals`), ascending,
   today's partial bar last. Build the evaluate payload with CURRENT
   equity and settled_cash from state.
4. `python3 strategy/box_scan.py evaluate < payload.json`
5. On `"action": "enter"`: take the FIRST qualifying setup only
   (Tier 1 beats Tier 2 if the same cycle surfaces both).

## Step 6.5 — Shadow mode gate

`circuit_breaker.py check` reports `mode`. If `mode` is `"shadow"` (or
missing — missing means shadow, fail closed):
- Run every step of this runbook normally EXCEPT no orders are ever sent
  to the broker (no place, no cancel).
- A qualifying entry is logged to `state/trade_log.json` with
  `"notes": "SHADOW — no order placed"`, points 0, plus the full decision
  payload (shares, stop, TP, tier). It does NOT count toward breakers.
- Shadow rows are for verifying data plumbing and decision quality only.

**Go-live protocol:** after the 2:30 PM CT scan on the first shadow day,
review the day: bars parsed clean on every symbol, quotes fresh, no
crashes, decisions sane. If clean, run
`python3 strategy/circuit_breaker.py set-mode --mode live`, commit, and
notify the owner that the system goes live next session. If NOT clean,
stay in shadow, fix, and repeat the next day. Only the agent-after-review
or the owner flips this flag — never flip it mid-day.

## Step 7 — Execute entry (exact order; LIVE mode only)

1. `review_equity_order` then `place_equity_order`: buy `shares` at market,
   account 995042041, regular hours only.
2. Confirm the fill (`get_equity_orders`). No fill within the cycle ->
   cancel, log VOID, done.
3. `spend-cash --amount <fill cost>`.
4. Place GTC stop: sell all shares, stop price = `stop_price` from the
   evaluate output. CONFIRM it's live. If the stop order is rejected,
   sell the position back at market immediately — never hold unprotected
   overnight — and log what happened.
5. Log the entry row to `state/trade_log.json` (symbol, entry price, shares,
   tier, box_top, box_bottom, stop_price, tp_price, category, timestamp CT).
   SAME CYCLE. Never defer.

## Step 8 — Persist and report

- Append one line to `state/run_log.txt`:
  `<UTC timestamp> | <flat|holding SYM> | <action taken or "no setups"> | <breaker state>`
- `git add state/ && git commit -m "scan: <summary>" && git push -u origin
  claude/robinhood-trading-mcp-4vlevg`
- Notify the owner ONLY on: order fired, position closed, stop moved,
  breaker/suspension change, NEW problem. Otherwise stay silent.

## Standing rules

- All order actions: account 995042041 only. Equities only. Whole shares.
  Market/stop/limit as specified — nothing exotic.
- Regular market hours only (8:30 AM - 3:00 PM CT). No extended hours.
- The agent never overrides a breaker, never averages down, never adds to
  a position, never trades a symbol outside the universe list, never
  places an order the runbook didn't specify.
- If anything in the broker state contradicts the journal, STOP after
  reconciling and report — do not trade on a cycle where reality and
  records disagree.
- Scheduled runs use UTC crons assuming CDT (UTC-5). When US daylight
  saving ends (Nov 1, 2026), shift crons +1 hour or trades fire an hour
  early.
