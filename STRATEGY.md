# Box Swing Strategy v1.0 (Robinhood Agentic)
# Author: Claude (agentic trader)
# Derived from: Core Strategy v4.0 (Box Theory) — adapted, not copied
# Last updated: July 11, 2026

---

## WHY THIS ISN'T v4.0 VERBATIM

v4.0 is an intraday 15-minute breakout system built for Alpaca. Porting it
unchanged to this account would break in four specific ways:

1. **Cash account + T+1 settlement.** v4.0 buys and force-flattens the same
   day, every day, recycling 100% of capital. In a $150 cash account that
   loop produces Good Faith Violations within two days (buy with unsettled
   proceeds → sell same day = GFV; 3 GFVs = 90-day restriction). The account
   would be dead in a week.
2. **No bracket orders on Robinhood.** v4.0's entire exit discipline is
   "broker-side bracket = structural discipline." Robinhood equities support
   a stop OR a limit working on shares, not an OCO pair. The exit mechanism
   has to be redesigned, not assumed.
3. **$150 of equity.** 2% risk = $3.00. On 15-min boxes the stop distances
   are so small that spread + slippage on thin small-caps eats the entire
   edge. Whole-share sizing barely functions at this granularity.
4. **Hourly automation floor.** Scheduled triggers in this environment fire
   at most hourly. A strategy that needs 15-minute reaction time is a
   strategy that fails silently 45 minutes out of every hour.

So: same core edge (Darvas box breakout on real volume), moved to the
timeframe where this account can actually express it — **daily bars, swing
holds of 2–10 days**. Fewer, better trades. Capital preservation first.

---

## PHILOSOPHY (UNCHANGED)

"Don't underestimate the power of simple stupid."

One edge, mastered deeply. A box is a defined trading range. Buy a clean
breakout above the box top on real volume. Stop below structure. Process
over outcome; discipline is structural, not willpower-based.

---

## ACCOUNT

- Broker: Robinhood Agentic Trading (MCP), account ••••2041 ("Agentic")
- Type: cash, individual — NOT margin, NOT PDT-subject
- Equity: $150.00 (all cash as of Jul 11, 2026)
- Equities only, whole shares only
- Owner-side kill switch: Robinhood app can disconnect the agent instantly

---

## THE STRATEGY — DAILY BOX BREAKOUT, SWING HOLD

### Box Definition (daily bars)
- Box window: last 20 **daily** bars, excluding today
- Box top = highest high of window; box bottom = lowest low of window
- **Tightness filter:** box_height / box_top ≤ 0.25. A 20-day range wider
  than 25% is chop, not a box. Skip it.
- Box must be "mature": price has traded inside the box (no close above
  top or below bottom) for at least the last 10 sessions

### Entry Rules
1. Price today trades **above box top**
2. Volume confirmation: today's cumulative volume is **already ≥ 1.5× the
   20-day average full-day volume** at scan time. No pro-rating, no
   projections — the bar must have already printed the volume. Early in the
   day this only triggers on genuinely explosive tape, which is exactly the
   point.
3. Liquidity floor (structural, replaces hand-maintained exclusion lists):
   - 20-day average daily volume ≥ 1M shares
   - 20-day average dollar volume ≥ $5M
   - Price between $2.00 and $30.00
4. Entry: market order (only while regular market is open, never extended
   hours), one position at a time — see Position Rules
5. Immediately after fill confirms: place GTC **stop-loss** at box bottom.
   The stop is the non-negotiable, broker-side safety net and is placed in
   the same cycle as the entry, before anything else happens.

### Tier Grading (at entry, never after)
- TIER 1: volume ≥ 3× average + tight box (height ≤ 15% of top)
- TIER 2: volume ≥ 1.5× average + clean box (height ≤ 25% of top)
- TIER 3: **not traded.** Partial boxes are watchlist material only.

### Exit Rules
- **Take profit:** box_top + 2.0 × box_height (≥ 2:1 reward/risk by
  construction). Robinhood has no OCO, so TP is enforced by the scan loop:
  if any scan sees price ≥ TP → cancel the stop, sell at market, done.
- **Stop loss:** GTC stop order at box bottom, live broker-side from entry.
  NEVER moved down. May be moved UP only by the early-lock rule below.
- **Early lock (daily-bar stall):** if position is up ≥ 1.0R and 2 of 3:
  1. Yesterday's daily candle closed red
  2. Yesterday's close < prior day's close
  3. Yesterday's volume < prior day's volume
  → raise the stop to max(entry price, box top). Lock the trade at
  breakeven-or-better; let the market decide the rest. (This replaces
  v4.0's "close early" — an emotional-exit vector. We tighten, we don't
  bail. See Discipline Scoreboard: the PLUG -1 was exactly this failure.)
- **Time stop:** 10 trading days in the trade without hitting TP → exit at
  market next scan. Dead money is risk.
- **No EOD force-flatten.** Swing positions hold overnight by design.

### Position Sizing (whole shares, $150 reality)
```
risk_dollars   = equity * 0.02                  # target risk
stop_distance  = entry_price - box_bottom
shares         = floor(risk_dollars / stop_distance)
if shares == 0:                                  # whole-share reality
    shares = 1, but ONLY if stop_distance <= equity * 0.05
    else SKIP the setup                          # 5% absolute risk ceiling
cost = shares * entry_price
if cost > settled_cash: shares = floor(settled_cash / entry_price)
if shares == 0: SKIP
```
2% is the target, 5% is the hard ceiling that whole-share rounding may
never exceed. A setup that can't be sized inside 5% risk doesn't get traded.

### Position Rules
- **One open position at a time, total.** Not one per category — one.
  $150 cannot meaningfully diversify, and a single position keeps the
  settlement ledger trivially auditable.
- Category tags are still recorded in the journal for future use when
  equity supports concurrent positions (threshold: $500 equity → revisit).

---

## CASH SETTLEMENT DISCIPLINE (STRUCTURAL)

- Buy only with **settled** funds. Track settled vs unsettled cash in
  state; when in doubt, assume unsettled (fail closed).
- Never sell shares bought with unsettled funds until those funds settle
  (this is the GFV condition — swing holds of ≥ 1 day make it nearly
  impossible to trip, which is a deliberate feature of the timeframe).
- After a sale, proceeds are marked settled at T+1.

---

## TRADING UNIVERSE

Theme (kept from v4.0): Energy / AI-adjacent / Silicon / Natural Gas.
The liquidity floor above is the real gatekeeper — it structurally excludes
the thin names (CRK, GREE) that v4.0 had to hand-flag, and any ticker that
degrades. No setup in a name that fails the floor, ever, regardless of list.

AI Compute: BBAI, SOUN, IONQ, QUBT, RGTI, QBTS
Nuclear/Uranium: SMR, UROY, DNN, UEC, LTBR, ASPI, NXE, UUUU
Power Semis: NVTS
Natural Gas: BW (CRK excluded — fails liquidity floor)
Hydrogen: PLUG, BLDP
Miners/Compute Infra: MARA, RIOT, CLSK, WULF, CIFR, CORZ (GREE, BTBT
excluded — liquidity)

NVDA: excluded until equity > $300 (price > 20% of equity makes
whole-share sizing meaningless below that).

Delisted/inactive (never scan): SWN, BITF.

---

## CIRCUIT BREAKERS (KEPT FROM v4.0 — THEY'RE RIGHT)

### Account-Wide
- 3 consecutive confirmed losses → trading suspended until the next
  trading day. No override, no exceptions.
- Suspension state lives in `state/account_state.json`, committed to git
  (containers are ephemeral — uncommitted state is deleted state).
- Fail closed: unreadable state file = suspended.

### Per-Symbol Bench
- 3 consecutive losses on one ticker with no intervening win → benched
  until it would-have-won isn't enough — until a real winning trade prints.

### New: Drawdown Breaker
- Equity closes below $105 (−30% from $150 start) → **full stop.** No
  further entries until the owner explicitly reviews and re-authorizes.
  A $150 account exists to prove process; −30% means the process needs
  human eyes, not another trade.

---

## MANDATORY SEQUENCE (EVERY SCAN CYCLE, IN ORDER)

1. **RECONCILE** — open orders + positions from broker (source of truth),
   cross-check against TradeLog. Unmatched 'entry' rows → VOID.
2. **VERIFY STOP** — if a position exists with no live GTC stop → place it
   immediately before anything else. A naked position is a fire alarm.
3. **UPDATE CIRCUIT BREAKERS** — consecutive losses, benches, drawdown.
4. **CHECK SUSPENSION** — active → log, report nothing new, stop.
5. **MANAGE OPEN POSITION** — TP check, early-lock check, time stop.
6. **SCAN FOR ENTRY** — only if flat, unsuspended, settled cash available.
7. **LOG IMMEDIATELY** — same cycle as any fill. Never defer.

---

## DATA INTEGRITY

- Daily bars via Robinhood MCP historicals; quotes for live price/volume
- Most-recent-bar verification on every fetch: assert the last bar's date
  is the current/most recent session before acting (v4.0's stale-data bug
  stays fixed by assertion, not by memory)
- Quote staleness: if a quote is older than 5 minutes, refuse to act on
  that symbol this cycle; stale symbols never block the rest of the scan
- Market hours: verify via live quote freshness + calendar, never memory.
  All times CT (CDT = UTC−5 in summer). Market: 8:30 AM–3:00 PM CT.

---

## SCHEDULE (ALL TIMES CT)

- 8:25 AM — Pre-market brief: overnight news on open position + universe,
  settled-cash check, circuit-breaker state
- 9:30 AM–2:30 PM — scan cycle **hourly** (environment floor; the daily-bar
  strategy is designed so hourly is sufficient, not a compromise)
- 2:30 PM — final scan: entries still allowed (confirmed daily breakouts
  near the close are the classic Darvas entry), open-position management
- No force-flatten. Overnight risk is priced into the sizing rules.

---

## NOTIFICATION DISCIPLINE (KEPT)

Alert only on: order fired, position closed, stop moved, breaker state
change, new problem. Never repeat an unchanged status. Robinhood's own
push notifications cover fills at the phone level.

---

## TRADE JOURNAL

`state/trade_log.json`, committed to git. Schema kept from v4.0:
symbol, action (entry/exit), price, shares, timestamp (CT), notes,
points (+1/−1/0), points_reason, tier, setup_type ('box_breakout_daily'),
category. Reconciled against broker fills before anything counts.

---

## EXPANSION TRIGGERS (NOT ACTIVE)

- Equity > $300 → NVDA eligible; revisit position-count rule at $500
- Chip-ecosystem sympathy layer (TSM Q2 earnings Jul 15, 2026): watchlist
  only until this core strategy has ≥ 10 journaled trades. One edge first.

---

## BEHAVIORAL RULES (KEPT, WITH ONE CHANGE)

- Capital preservation first — provider account, every decision filters
  through this lens
- 2% target / 5% ceiling is a hard rule, not a guideline
- Never override a circuit breaker
- Exits require structural reasons; the early-lock rule tightens stops
  instead of bailing — profit-taking fear gets a mechanism, not a veto
- Comfortable losing is okay; avoidance and rage-trading are not
- The goal: prove process at $150 before scale ever gets discussed

---

## v1.1 AMENDMENTS (July 20, 2026 — reconciled with owner re-authorization)

TRADING_PLAYBOOK.md is now the top-level entry point; where it and this
file overlap, the most conservative rule wins. Changes from v1.0:

1. **Account reality reset.** Equity is no longer $150 cash. As of
   2026-07-20: $0.39 settled cash + $38.68 crypto (crypto is untradable
   and invisible via MCP — owner-managed in the app). state/ files have
   been reconciled to this. The system idles in monitor+log mode until
   the account is funded enough to size a whole share inside the 2%/5%
   risk rules.
2. **Cadence: hourly → twice daily.** 10:00 AM ET full cycle (entries
   allowed), 3:30 PM ET exit-management only. The daily-bar strategy was
   designed to tolerate coarse scheduling; near-close entries from v1.0
   are sacrificed for schedule simplicity until equity justifies more.
3. **Position-cost cap added.** In addition to v1.0 risk sizing, a
   position's cost may not exceed 50% of total account value
   (owner-selected "Standard" profile).
4. **Weekly drawdown pause added.** Equity down ≥ 10% over 5 trading
   days → no new entries until recovered or owner reviews. This is in
   addition to (not instead of) the v1.0 circuit breakers.
5. **Supplementary scanner.** Saved Robinhood scan "Autopilot Swing
   Candidates" (a0a9a49e-c941-4f11-8ac6-a28d6f1eccb9) runs for
   discovery. Its hits are journal/watchlist material only — the fixed
   universe list remains the only tradable set.
6. **Branch rename.** All state commits now push to
   `claude/robinhood-trading-tools-access-no4817` (the old
   `claude/robinhood-trading-mcp-4vlevg` branch was merged in PR #3).
