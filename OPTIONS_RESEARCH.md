# Options Overlay — Research Track (CODE WRITTEN, NOT WIRED TO LIVE ORDERS)

## Status: 2026-07-14 — approval cleared, code built and tested, still gated

Account 995042041 ("Agentic") option approval cleared same-day
(`option_level: "option_level_2"`, confirmed via `get_accounts`). Code
now exists at `strategy/option_scan.py` (contract selection, sizing,
manage/exit) with 19 passing unit tests in `tests/test_option_scan.py`.

**It is not wired into the live runbook and places no real orders.**
Approval clearing is one of two gates from the original design — the
second, a paper-validation phase, is now MORE clearly needed than
originally thought, because of a real finding below. Building the code
was the easy part; proving it against real market microstructure is the
part that was always going to take longer, and the first real check
already surfaced why.

## Live finding, 2026-07-14: the design's own liquidity assumptions failed on real data

Pulled the actual SOUN Aug 7 2026 chain (24 DTE, underlying ~$6.74) via
`get_option_quotes`. Both the 7.0 and 7.5 strikes — the ones nearest the
money — came back with:
- **Deltas of 0.491 and 0.371** — both below the 0.60-0.70 target window
- **Spreads of 16.8% and 20.3% of mid** — both above the 10% floor

Neither contract would have qualified for entry under this module's own
rules. This is not a bug; `option_scan.py`'s test suite asserts this
result directly (`test_real_chain_has_no_qualifying_contract`) rather
than hiding it behind a fabricated passing fixture. The honest read: a
$6-7 stock's options chain may simply be too thin/wide for a 0.60-0.70
delta, sub-10%-spread rule to ever fire in practice — the rule may need
loosening (wider spread tolerance, wider delta band) or the strategy may
need to restrict itself to higher-priced, more liquid underlyings than
the current $2-$30 equity universe implies. Not resolved yet; this is
exactly what a paper-validation phase across multiple real chains, not
one spot-check, needs to determine before real premium is risked on it.

Confirmed real infrastructure (read-only market data works today,
independent of option_level): `get_option_chains` for SOUN returned live
weekly expirations (Jul 17, 24, 31, Aug 7, 14, 21, 28, then monthlies)
with a $100 contract multiplier — standard equity option structure.

## Why options, honestly

A long call on a confirmed box breakout gets leveraged exposure for a
defined, capped risk (the premium paid — you cannot lose more, unlike a
naked short or margin). This is a legitimate way to compound faster than
shares alone. It is also not free: theta decay works against you every
day you're wrong about timing, and IV crush after a move can erase gains
even when the direction call was correct. Two rejected alternatives for
comparison — leveraged ETFs (decay from daily rebalancing in chop) and
higher risk-per-trade on shares (Kelly drag past the optimal fraction) —
are worse trades than this one. This is the one lever from that
conversation worth actually building.

## Design — same signal, different instrument

The entry trigger is UNCHANGED: `box_scan.py evaluate()` still decides
*whether* and *what* qualifies (box, maturity, liquidity, volume, tier).
Only the *instrument* used to express a qualifying setup changes.

### Contract selection
- **Type:** long call only (never sell/write options, never puts — this
  system only trades long breakouts). Defined-risk, no assignment risk.
- **Strike:** slightly OTM, delta ~0.60-0.70 at entry. Deep ITM defeats the
  leverage purpose; far OTM is a lottery ticket with near-certain theta
  death.
- **Expiration:** must exceed the strategy's own `TIME_STOP_SESSIONS` (10
  trading days) by a real margin — target 3-4 weeks out, never the
  nearest weekly. A time-stop exit forced by an expiring contract is a
  worse failure mode than a time-stop exit on shares (shares can just be
  held one more day if needed; a contract cannot).
- **Liquidity floor on the CONTRACT itself**, independent of the
  underlying's equity liquidity floor: open interest >= 500, bid-ask
  spread <= 10% of mid. A liquid stock can still have an illiquid options
  chain — this must be checked separately, not assumed.

### Sizing (premium replaces stop-distance as the risk unit)
Options make position sizing simpler, not harder: max loss is the premium
paid, full stop. No stop-loss order is needed against the option itself.
```
risk_dollars = equity * RISK_TARGET          # same 2% target, 5% ceiling
contracts    = floor(risk_dollars / (premium * 100))
if contracts == 0: skip                      # no one-contract forcing —
                                              # unlike shares, a single
                                              # contract's premium is a
                                              # much larger risk jump
cost = contracts * premium * 100
if cost > buying_power: skip                 # never partial-size an
                                              # option position down
```

### Exit rules (translated, not reinvented)
- **Take profit:** when the UNDERLYING hits the same `tp_price` from
  `box_scan.py`, sell the calls at market. Do not hold for theoretical
  option-price targets — the underlying's structure is still the thesis.
- **Stop / thesis invalidation:** when the underlying closes below
  `box_bottom` (the same level that would trigger a shares stop), sell
  the calls at market immediately. There is no broker-side GTC stop on
  options in this design — the scan cycle must catch this actively, so
  options make the "verify every cycle" discipline MORE load-bearing,
  not less.
- **Time stop:** same 10-session rule, but exit at 8 sessions instead of
  10 — leaving 2 extra sessions of buffer before the chosen expiration
  actually forces the issue, since an option time-stop failure mode
  (assignment/expiry) is worse than a shares one.
- **No early-lock stop-raising** — there's no stop order to raise on a
  long call. Early-lock instead means: on 2-of-3 stall signals with >=1R
  gain, sell HALF the contracts to bank realized gain, hold the rest
  to the original TP/stop. Simpler than adjusting a strike position.

## What's still missing before this could ever go live

1. **Robinhood option approval on 995042041** — the actual gate, owner's
   decision, not a code problem.
2. **A paper-testing phase equivalent to shadow mode** — this design has
   never touched real option fills, spreads, or slippage. The same
   discipline that gated shares (one clean validation cycle before real
   orders) applies here, likely for longer given the added complexity.
3. **Greeks-aware exit testing** — the "sell at underlying stop/TP"
   simplification needs to be checked against real option price behavior
   (does IV crush actually eat the exit before the underlying even hits
   TP in practice?). Untested assumption, flagged honestly rather than
   quietly relied on.

## What happens next

`strategy/option_scan.py` exists and is unit-tested against both real
and synthetic contract data. Still needed before any real premium is
risked: a genuine paper-validation phase (checking multiple real chains
across the universe, tuning the delta/spread rules against what actually
exists rather than what seemed reasonable on paper) and explicit owner
sign-off after that phase — the same confirm-before-real-money discipline
that governs every other decision in this system. Approval clearing
today does not skip this; it's the reason this phase can start.
