# RideServ LLC — 2025 Tax Filing Plan & Planning Memo

**Prepared:** July 21, 2026 (rev. 2 — incorporates three third-party tax documents)
**Entity:** RideServ LLC (Illinois LLC, EIN ••5908)
**Scope:** Federal + Illinois 2025 filing, 1099 compliance, and forward planning
**Status:** DRAFT — numbers are preliminary (missing statement months); not filing-ready

> This memo organizes the facts and the plan. It is not a substitute for a CPA
> or attorney — two items below (Carolyn Nesbitt's status, and the late-filing
> posture) specifically require licensed professionals before filing.

---

## 1. Entity reality check: this is NOT a C corp

The request was framed as a "C corp filing." The entity records say otherwise:

- RideServ LLC files **Form 1065 (partnership return)** with Schedule K-1s.
  There is no C-corp election (Form 8832) on file per the entity summary.
- A C corp files Form 1120, pays its own 21% tax, and its owners are taxed
  again on dividends. None of that applies to RideServ for 2025, and you
  cannot retroactively elect C-corp status for 2025 at this point.
- **Do not file an 1120 for 2025.** The 2025 filing is a 1065 — or possibly
  a Schedule C (see §2).

**Should RideServ become a C corp going forward?** Almost certainly no at
this income level (~$25–40k net):

| | Pass-through (current) | C corp |
|---|---|---|
| Federal rate on profit | Owner's individual rate, minus ~20% QBI deduction | Flat 21% at corp level |
| Second layer of tax | None | Dividends taxed again to owner |
| Losses | Flow to owner's 1040 | Trapped in the corp |
| QBI deduction (§199A) | Yes | No |

The strategy "big corps" actually use at this size is not C-corp status — it
is an **S-corp election** to reduce self-employment tax, and that only starts
paying off when net profit is consistently above roughly $40–50k after paying
yourself a reasonable W-2 salary. Revisit at that threshold (see §7).

## 2. The Carolyn Nesbitt problem decides WHICH return you file

This is the structural fork, and it must be resolved before filing:

- **If Carolyn is a real 10% member**, the IRS expects a K-1 issued to her
  every year — even a K-1 showing $0 allocated. A partnership return listing
  a member who receives no K-1 is internally inconsistent and is an audit
  flag. "Non-beneficial owner, no K-1" is not a recognized federal filing
  position for a named member.
- **If Carolyn has no economic interest at all** (no capital, no profit, no
  loss — which is what the operating agreement apparently says), a strong
  argument exists that she is not a partner for tax purposes. Then RideServ
  is a **single-member LLC = disregarded entity**, and the 2025 activity
  belongs on **Chase's Form 1040, Schedule C** — no 1065 at all. That would
  also erase the partnership late-filing penalty exposure in §3.

Either answer is workable; straddling them is not. **A CPA must pick the lane
before anything is filed.**

**On the SSI question — straight answer:** labeling the $3,582.70 to Carolyn
as "personal gifts, excluded from books" keeps it off RideServ's return, but
it does **not** keep it out of SSI rules. SSA counts cash gifts as unearned
income in the month received, which can reduce or suspend SSI benefits, and
unreported gifts can create an SSA overpayment debt. There is no bookkeeping
label that changes this. The existing flag is right: an elder-law/benefits
attorney needs to review **before** filing, and Carolyn may need to report
the gifts to SSA regardless of what RideServ files.

## 3. Where you stand on deadlines (as of July 21, 2026)

| Item | Deadline | Status today |
|---|---|---|
| Form 1065 (2025) | **March 16, 2026** (or **Sept 15, 2026** with Form 7004 extension) | If extension filed: ~8 weeks left. If not: late since March. |
| 1099-NEC (Steve Mikola) | Jan 31, 2026 to IRS & recipient | **Late.** Penalty tier increases Aug 1, 2026 — see below |
| 1099-MISC (rent — Sims; possibly Mclaughlin) | Feb/Mar 2026 | Late; same Aug 1 tier logic |
| IL-1065 + IL K-1-P (Illinois) | April 15, 2026 (auto-extension available) | Confirm status |
| Chase's 1040 (K-1 or Sch C flows here) | April 15, 2026 (Oct 15 if extended) | Confirm status |
| Chase's 2026 Q3 estimated tax (1040-ES) | **Sept 15, 2026** | Upcoming |

**Most time-sensitive item in this memo:** information-return (1099) penalties
step up on **August 1, 2026** — roughly $130/form if filed by July 31 vs.
roughly $330–340/form after (inflation-indexed; verify current amounts).
**File the late 1099-NEC for Steve Mikola and the 1099-MISC for the Sims
rent in the next 10 days**, even with partial-year amounts corrected later
if needed. Late is cheap; later is triple.

**If the 1065 was never filed or extended:** the late-filing penalty is
approximately **$245 per partner per month** (indexed), up to 12 months —
with 2 partners that is ~$490/month accruing since March. Two mitigations:

1. **First-time abatement** — available if the entity has a clean 3-year
   compliance history.
2. **Rev. Proc. 84-35 relief** — small partnerships (≤10 individual partners)
   with timely-filed partner returns often qualify for full penalty relief.
3. And if the CPA concludes this is a **disregarded entity (Schedule C)**,
   the partnership penalty disappears entirely because no 1065 was due.

Do not let penalty fear drive delay — the penalty clock only stops when the
return is filed.

## 4. Income side — corrections before filing

1. **Report Stripe GROSS, not net.** Stripe will have issued a 1099-K for
   gross processing volume (~$35,485.78). The return must show gross receipts
   that reconcile to the 1099-K, with refunds ($ credits) and processing fees
   deducted as separate line items. Netting to $31,323.35 on the income line
   creates a document-matching mismatch — a leading cause of automated IRS
   notices.
2. **Cash App client income** ($22,738.01 Sonya + $500.52 Chelsia + $210.02
   Tammy) is reportable regardless of whether Cash App issues a 1099-K.
   Reconcile against any 1099-K actually received.
3. **Missing months** (Cash App Jan–Apr + Jul; Mercury Oct) must be obtained
   before filing. Filing on known-understated income is not an option —
   Sonya alone averages ~$3,250/month, so the missing months plausibly add
   $15k+ of income.
4. **Correctly excluded** (keep the documentation): Stripe Capital principal
   ($7,700 — financing), Cash App self-transfers (~$23,884), Hayes Management
   pass-throughs, personal items (Syy Starrr, Ikey Ikey, Carolyn).
5. **State Farm payout ($2,084.57):** correct that it's not ordinary income,
   but it must be netted against the casualty repair costs and the vehicle's
   basis. If no repairs were deducted and the payout exceeds the loss, the
   excess can be taxable gain. Trace the repair costs before excluding it.
6. **Hayes Management:** excluding it from RideServ is right, but the ~$5,603
   out / $5,424 in still belongs on a tax return somewhere (Hayes's own
   Schedule E/C). Excluded-from-RideServ ≠ excluded-from-tax.

## 4A. Third-party tax documents received (reviewed July 21, 2026)

Three 2025 information returns were provided and reviewed. All monthly boxes
tie exactly to their stated totals. **The IRS has copies of all three**, so
the return's gross receipts must reconcile to them.

### (a) 1099-NEC FROM DJD Legacy Holdings LLC — $15,542.20 — this is SONYA DROTTAR's LLC

- Payer: DJD Legacy Holdings LLC, Sheridan WY (TIN 99-4422560); recipient
  RideServ LLC (last-4 TIN matches), Box 1 nonemployee compensation
  **$15,542.20**; also reported to Illinois (Box 7).
- **Owner confirms DJD Legacy Holdings = Sonya Drottar's entity.** Her
  payments are already in the books as "Sonya Drottar (Cash App)"
  ($22,738.01 over 7 months), so this NEC is almost certainly an **overlap,
  not new income** — she is running RideServ's services through her LLC and
  1099-ing what the LLC paid.
- **Do NOT add $15,542.20 on top of the Cash App figure** — that would
  double-count. And no matching problem exists in the other direction:
  recorded Sonya income ($22,738.01 partial-year, more once missing months
  arrive) already exceeds the $15,542.20 the IRS will try to match.
- **Still required:** a written reconciliation mapping DJD's $15,542.20 to
  specific Cash App/Mercury deposits. Two reasons: (1) confirm none of
  DJD's payments arrived through a channel that was never counted, and
  (2) if the IRS ever asks why gross receipts ≠ sum of 1099s, the workpaper
  is the answer. Also confirm whether her personal-name Cash App payments
  vs. LLC payments split matters for her books — it doesn't change
  RideServ's income (all of it is reportable), only the mapping.
- Cosmetic: recipient name is misspelled ("RideServeLLC") and the address
  (1123 E. Mason St) differs from the eBay/Stripe address (3309 Robbins Rd
  #577). TIN matches, so no correction is required, but confirm with Sonya
  that the full TIN on file is correct.

### (b) Stripe 1099-K — gross $36,327.78 (979 transactions)

- Compiled books show Stripe gross of $35,485.78 — the 1099-K is **$842.00
  higher**. Box 1a is computed on *transaction dates*, while payouts lag,
  so late-December charges paying out in January 2026 are the likely
  explanation. Reconcile the $842 rather than assuming; the return's gross
  receipts line must be ≥ $36,327.78 for Stripe activity.
- Report the full $36,327.78 as gross receipts and deduct the ~$5,004.43 of
  refunds/fees/credits (to reach the $31,323.35 net) as separate expense
  lines. No withholding (Box 4 = $0).

### (c) eBay 1099-K (Wheel N Deal) — gross $2,899.41 (35 transactions) — ⚠️ NOT IN THE BOOKS

- Payee "RideServ LLC / Wheel N Deal," same EIN. Active Feb–Dec (no Jan/Jul
  sales).
- **Wheel N Deal sales revenue was entirely missing from the income
  compilation** — the books captured its COGS ($2,198.00 + $308.14 + part
  of Walmart) but zero sales. Add $2,899.41 to gross receipts.
- eBay deducts selling fees before payout: pull the eBay financial statement
  so the fees can be deducted (gross on the income line, fees as expense).
- Note: eBay filed this despite being under the federal $20k threshold —
  Illinois has a much lower state 1099-K threshold, so IL has a copy too.

### Revised income floor after documents

| Source | Books (before) | Per documents (after) |
|---|---|---|
| Stripe (gross) | $35,485.78 | **$36,327.78** |
| eBay / Wheel N Deal | $0 | **$2,899.41** |
| DJD Legacy Holdings (1099-NEC) | — | $15,542.20 — **overlaps Sonya Cash App; not added** |
| Cash App clients (7 months) | $23,448.55 | $23,448.55 |
| **Gross receipts floor** | ~$58,934 | **~$62,676** (still understated — missing months) |

IRS document-matching check: the three 1099s total $54,769.39. Reported
gross receipts (~$62,676 floor, higher after missing months) comfortably
exceed that, so no matching mismatch — provided the DJD↔Sonya overlap
workpaper exists to prove the mapping.

Net-income effect of the documents themselves: **+~$2,899 gross from eBay**
(less eBay selling fees once pulled) and the $842 Stripe timing item to
reconcile. The DJD NEC adds no income if the overlap trace confirms; the
preliminary net stays in the ~$25–28k band pending the missing Cash App
months and the $13,175 contract-labor resolution.

## 5. Expense side — the four items that move the number

1. **Generic "Contract labor" $13,175.51 — resolve before anything else.**
   This single item swings net income from ~$24.7k to ~$11.6k. Reconcile it
   transaction-by-transaction against Steve Mikola ($8,276.96) and Windol
   Jenkins ($285.41). Only the non-overlapping remainder is deductible, and
   any newly identified individual over $600 needs a 1099-NEC.
2. **"Wages" $1,118.80:** owner/partner draws are NOT deductible on a 1065
   (or Schedule C). Deductible only if a genuine non-owner employee — in
   which case there must be a W-2, and 941/940 payroll filings. If no payroll
   filings exist, the cleanest true-up is usually reclassifying to draw
   (not deductible) or contract labor (1099, if facts support it). CPA call.
3. **Vehicle strategy — likely the biggest legitimate deduction being left
   on the table.** Currently claiming actual fuel ($5,507.86) + insurance
   ($902.34). For rideshare/delivery, the **standard mileage rate (70¢/mile
   for 2025)** frequently beats actual costs: 20,000 business miles = $14,000.
   Rules: one method per vehicle per year (no mixing), and standard mileage
   already includes fuel, insurance, repairs, and depreciation. Pull mileage
   from the rideshare platform statements (Uber/Lyft/DoorDash report it),
   compute both methods, take the larger. A mileage log is also the audit
   defense for either method — reconstruct it now from platform data, not
   later under exam.
4. **Rent $3,450.55 (Caleb & Jaron Sims):** confirm this is genuinely
   business premises. If it is (or includes) the personal residence, it is
   not deductible as rent — the correct vehicle is the **home-office
   deduction** (exclusive business-use area, actual-cost or simplified $5/sq
   ft method). Misclassified personal rent is a classic exam adjustment.

Smaller cleanups: DoorDash "client meals" at 50% is fine **only** for meals
with actual clients — solo meals while driving are personal and
nondeductible, so split the $743.63 accordingly. Stripe Capital interest is
deductible once the amortization schedule arrives (request it from the Stripe
dashboard — Capital → statements). Entertainment $82.66 correctly excluded.

## 6. Draft picture (ranges, not filing numbers)

| Scenario | Income | Expenses | Net |
|---|---|---|---|
| As compiled (floor income, no $13,175 bucket) | $54,772 | $30,020 | ~$24,752 |
| If $13,175 contract labor is real (not duplicate) | $54,772 | $43,195 | ~$11,577 |
| With missing months recovered (both sides move) | $65–72k (est.) | TBD | **Unknown until reconciled** |

What flows from net income (assuming Schedule C or 100% K-1 to Chase):

- **Self-employment tax:** ~15.3% × 92.35% of net → roughly **$3,500** at
  $24.7k net, or ~$1,635 at $11.6k. Half is deductible on the 1040.
- **Federal income tax:** after the ~20% QBI deduction (§199A) and standard
  deduction, likely modest at these levels.
- **Illinois:** 1065 filers pay 1.5% replacement tax (~$370 at $24.7k) plus
  Chase's 4.95% individual rate on the flow-through; Schedule C skips the
  replacement tax.

## 7. Legitimate reduction playbook (the real "big corp" moves)

In priority order for this fact pattern:

1. **Mileage method optimization** (§5.3) — potentially $5–10k of additional
   deduction if platform miles are high. Biggest single lever.
2. **QBI deduction** — 20% of qualified business income off Chase's taxable
   income, automatic if claimed. Made permanent by 2025 legislation.
3. **SEP-IRA** — Chase can contribute ~20% of net self-employment earnings
   (~$4,500 at $24.7k net) and deduct it, and the contribution deadline is
   the **extended** return due date — so this is still open for 2025 if the
   return is on extension. This is the last remaining way to cut the 2025
   bill after year-end.
4. **Home office** — if a space qualifies (exclusive + regular business use),
   also unlocks additional business-mileage treatment for trips from home.
5. **§179 / bonus depreciation** — 100% bonus depreciation was restored for
   2025; any equipment or trailer purchases can be fully expensed.
6. **S-corp election (future, not 2025)** — when net profit is reliably
   above ~$40–50k, an S election (Form 2553) with a reasonable W-2 salary
   saves SE tax on the excess. Below that, payroll costs eat the savings.
   A C-corp election is not recommended at any foreseeable income level here.
7. **Clean books = kept deductions** — the dedicated RideServ-only bank
   account (already flagged) is the highest-ROI compliance move. Commingling
   is how legitimate deductions get disallowed under exam.

## 8. Robinhood / trading account

The Robinhood "Agentic" account (••2041) is titled as an **individual cash
account**, funded July 2026, with **no 2025 activity**. It is irrelevant to
the 2025 return, and even in 2026 its gains/losses belong to the individual
owner's 1040 — not to RideServ — unless the account is retitled to the LLC.

## 9. Action checklist (ordered)

| # | Action | Owner | Deadline |
|---|---|---|---|
| 1 | File late 1099-NEC (Mikola) + 1099-MISC (Sims rent) via IRS IRIS e-file | Chase/CPA | **Before Aug 1, 2026** |
| 2 | Confirm whether Form 7004 extension was filed for the 1065 | Chase | This week |
| 3 | Engage CPA: partner-vs-disregarded-entity determination (§2) | Chase | This week |
| 4 | Engage benefits attorney re: Carolyn / SSI | Chase | Before filing |
| 5 | Pull missing statements: Cash App Jan–Apr + Jul, Mercury Oct | Chase | ASAP |
| 5a | Workpaper mapping DJD/Sonya 1099-NEC ($15,542.20) to Cash App/Mercury deposits | Chase | Before filing |
| 5b | Add eBay/Wheel N Deal sales ($2,899.41) to books; pull eBay fee statement | Chase | Before filing |
| 5c | Reconcile $842.00 Stripe gap (1099-K $36,327.78 vs books $35,485.78 — likely Dec payout timing) | Chase | Before filing |
| 6 | Reconcile $13,175.51 contract-labor bucket to transactions | Chase/CPA | Before filing |
| 7 | Resolve "wages" $1,118.80 (employee vs. draw) | CPA | Before filing |
| 8 | Pull platform mileage reports; run standard-vs-actual comparison | Chase | Before filing |
| 9 | Get Stripe Capital amortization schedule (interest split) | Chase | Before filing |
| 10 | Trace State Farm payout vs. repair costs | Chase | Before filing |
| 11 | Confirm Mclaughlin full-year total for 1099 threshold | Chase | Before filing |
| 12 | Decide SEP-IRA contribution amount | Chase/CPA | Extended filing date |
| 13 | File federal return (1065+K-1s or Sch C) + IL return | CPA | **Sept 15 / Oct 15, 2026** |
| 14 | Chase 2026 Q3 estimated payment (1040-ES + IL-1040-ES) | Chase | **Sept 15, 2026** |
| 15 | Open dedicated RideServ-only bank account | Chase | Now (2026 hygiene) |

## 10. Self-critique — gaps and assumptions in this memo

Per standing instructions, the weaknesses of this analysis:

- **Penalty and rate figures are approximate.** 1099 penalty tiers, the
  §6698 per-partner amount, and the 2025 mileage rate should be verified
  against current IRS tables before relying on them.
- **The Schedule C alternative is an argument, not a certainty.** Whether
  Carolyn is a partner for tax purposes depends on the operating agreement's
  actual text and state law — only a CPA/attorney reading it can decide.
- **Income estimates for missing months are extrapolation** from Sonya's
  monthly average; actuals may differ materially.
- **This memo assumes no prior-year returns create carryovers** (NOLs,
  depreciation schedules on vehicles, prior 1099 filings). Prior-year
  returns were not reviewed.
- **Illinois treatment was addressed at summary level only** — PTE-tax
  election, replacement-tax mechanics, and local obligations need CPA review.
- **No documents were independently verified** — all figures come from the
  owner-provided reconciliation, which itself flags missing months and a
  possible $13k duplicate.
