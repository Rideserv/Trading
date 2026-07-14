# Options Overlay — Research Track (NOT LIVE)

## Status: blocked on Robinhood approval, research only

Account 995042041 ("Agentic") has `option_level: ""` — options are not
approved on it. This is a Robinhood suitability decision the owner makes
directly (their own questionnaire), not something granted by this system.
Nothing in this document trades real money. It exists so the design is
ready the day approval clears, instead of being improvised then.

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

Nothing, automatically. This document is picked up and built into
`strategy/option_scan.py` (mirroring `box_scan.py`'s structure) only once
option approval clears AND the owner asks to proceed — the same
confirm-before-real-money discipline that governs every other decision in
this system.
