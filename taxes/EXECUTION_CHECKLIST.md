# RideServ 2025 — Execution Checklist (start July 21, 2026)

Work top to bottom. Each step says exactly what to do and what unblocks.
Companion workpapers are in `taxes/workpapers/`.

---

## TODAY (Tue Jul 21) — three phone-call/text-sized tasks

### 1. Send W-9 requests to Steve Mikola and Caleb Sims
You cannot file their 1099s without their TINs — this is the critical path
for the Aug 1 penalty deadline, so it goes first.

- Text/email both: *"I need a completed W-9 from you this week so I can file
  your 1099 for last year — here's the blank form:
  https://www.irs.gov/pub/irs-pdf/fw9.pdf. A photo of the filled-out form
  is fine."*
- Log what you collect in `workpapers/1099_recipients.csv`.
- If a recipient refuses or ghosts you: file the 1099 anyway with the
  address you have and "refused" noted for the TIN — a filed-without-TIN
  1099 beats an unfiled one, and documented refusal shifts backup-withholding
  responsibility. Note the refusal in the CSV.

### 2. Find out whether the Form 7004 extension was filed
This decides your whole penalty posture.

- Check: email/portal of whoever prepared 2024's return, your IRS online
  business account (irs.gov → Business tax account), or paper records.
- If nothing turns up, call the IRS Business & Specialty line:
  **800-829-4933** (7am–7pm local, Mon–Fri; call at 7:00am sharp to avoid
  hold times). Have EIN, entity name, and address ready. Ask: "Was a Form
  7004 extension processed for tax year 2025, and has a 2025 Form 1065 been
  filed?"
- Record the answer in the memo. Extension filed → deadline Sept 15.
  No extension → every week of delay adds penalty; the CPA (step 3) needs
  to know on day one.

### 3. Book the CPA appointment
Not "research CPAs" — book a specific appointment this week.

- Search: CPA + "small business" + Springfield IL; or Illinois CPA Society
  referral (icpas.org). Say the magic words: *"Multi-member LLC, 2025
  Form 1065 possibly late, need entity-classification review and K-1
  question resolved before filing."* Late-return work gets you scheduled
  faster than "tax planning."
- Bring/send: `2025_TAX_PLAN.md` (this repo), the three 1099 PDFs, and the
  operating agreement. The #1 question for them is §2 of the plan:
  **is Carolyn a partner (1065 + $0 K-1) or not (Schedule C)?**
- Separately: one call to an elder-law/benefits attorney about Carolyn's
  SSI exposure from the cash gifts. Ask the CPA for a referral if needed.

---

## THIS WEEK (by Fri Jul 31) — the hard deadline

### 4. E-file the two late 1099s (once W-9s arrive)
Deadline logic: the penalty tier roughly triples after **Aug 1**. Aug 1 is a
Saturday — treat **Friday July 31** as the deadline.

Option A — IRS IRIS (free, direct): irs.gov/iris. Needs an IRIS Transmitter
Control Code (TCC), which can take time to issue — **apply today** if going
this route, and fall back to Option B if the TCC doesn't arrive by Jul 29.

Option B — commercial e-file (fast, ~$3–5/form): tax1099.com (the same
service DJD used to 1099 you), track1099.com, or efile4biz.com. Account →
enter payer (RideServ LLC, EIN, address) → enter recipient from W-9 → file.
Both federal and IL in one pass (confirm IL is included; Illinois
participates in the combined federal/state program).

What to file:
- **1099-NEC — Steve Mikola** — Box 1: $8,276.96 *(use the full-year figure
  if the missing-month reconciliation finishes in time; otherwise file the
  known amount now and file a CORRECTED 1099 later — filed-then-corrected
  stops the late clock, waiting does not).*
- **1099-MISC — Caleb Sims** — Box 1 (Rents): $3,450.55 *(skip only if his
  W-9 shows an S-corp or C-corp; individuals/LLCs get the form).*
- **David/Mclaughlin**: hold until the full-year total is confirmed (step 6);
  if over $600 to an unincorporated payee, file the same way.
- Recipient copies: the e-file services mail or e-deliver them for you —
  select that option.

### 5. Download every missing statement (one login session each)
- **Cash App**: profile → Documents → Monthly statements → Jan, Feb, Mar,
  Apr, Jul 2025.
- **Mercury**: dashboard → Statements → Oct 2025.
- **Stripe**: Dashboard → Settings → Documents (1099-K already in hand) and
  Dashboard → Capital → your financing → request/download the **payment
  schedule showing the fee (interest) portion** of the $6,470.60 repaid.
- **eBay**: Seller Hub → Payments → Reports → generate the 2025 **financial
  statement / transaction report** (shows selling fees to deduct against
  the $2,899.41 gross).

---

## NEXT (Aug 1–15) — reconciliation, in this order

### 6. Rebuild income with the new statements
Update `workpapers/gross_receipts_build.csv` as statements land:
- Add Jan–Apr + Jul Cash App income rows (Sonya/Chelsia/Tammy full-year
  totals replace the 7-month figures).
- Add eBay $2,899.41 (already known).
- Resolve the $842.00 Stripe gap (books $35,485.78 vs 1099-K $36,327.78 —
  check late-Dec transactions paying out in Jan 2026).
- Confirm David/Mclaughlin full-year total → decides his 1099 (step 4).

### 7. DJD ↔ Sonya overlap workpaper
Fill `workpapers/djd_sonya_reconciliation.csv`: map DJD's $15,542.20 to the
specific Cash App/Mercury deposits already counted. Goal: prove no
double-count and no untracked channel. This is the CP2000 insurance.

### 8. Kill the $13,175.51 "Contract labor" bucket
Against transaction-level Mercury data: every dollar is either (a) already
inside Steve Mikola/Windol Jenkins itemized totals → delete, (b) a real,
newly identified payee → itemize, and 1099 them if over $600, or (c)
untraceable → not deductible. The bucket itself never goes on a return.

### 9. Resolve "Wages" $1,118.80
Who received it? Owner → reclass to draw (not deductible). Non-owner with
no payroll filings → CPA decides (likely late W-2/941s or reclass to
contract labor + 1099). Do not deduct as wages without payroll filings.

### 10. Mileage method comparison (biggest refund lever)
Pull 2025 mileage from every platform (Uber/Lyft/DoorDash driver tax
summaries include miles). Compute: miles × $0.70 vs. actual costs
(fuel $5,507.86 + insurance $902.34 + repairs + depreciation × business-%).
Take the larger; keep the platform reports as the log. Enter both numbers
in the plan memo before the CPA meeting.

---

## SEPTEMBER — filing

- **Sept 15**: extended 1065 deadline (if extension exists) AND Chase's
  2026 Q3 estimated payment (1040-ES + IL-1040-ES).
- CPA files: 1065 + K-1s + IL-1065 (or Schedule C route per §2 decision),
  with the SEP-IRA contribution decision made before filing (deductible up
  to ~20% of net SE earnings; deadline = extended filing date).
- If NO extension exists: file the moment the books close — every month is
  another ~$245/partner in penalty — and have the CPA request first-time
  abatement / Rev. Proc. 84-35 relief with the filing.

## Standing fixes (do once, benefits forever)

- Open a RideServ-only bank account; stop routing Hayes Management and
  personal spending through Mercury ••7670 and Cash App.
- Going forward, collect a W-9 from every new vendor/landlord **before**
  first payment — makes January 1099 season a 10-minute task.
- Wheel N Deal: record eBay sales monthly (the missed $2,899.41 shows the
  gap in the current process).
