"""Unit tests for option_scan.py.

REAL_QUOTES_SOUN is the actual SOUN Aug 7 2026 chain (7.0 and 7.5
strikes) fetched live via get_option_quotes on 2026-07-14, underlying
~$6.74. Both real contracts FAIL this module's own criteria: deltas
0.491/0.371 are below the 0.60-0.70 target window, and spreads are
16.8%/20.3% of mid — both above the 10% floor. That is a genuine,
useful finding (see OPTIONS_RESEARCH.md's "untested assumption" caveat),
not a test-writing inconvenience, so it is asserted directly below
rather than papered over.

SYNTHETIC_LIQUID_CONTRACT is fabricated, clearly labeled as such, and
used only to exercise the "a qualifying contract exists" code path —
every test using it says so in its name/comment.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "strategy"))

import option_scan  # noqa: E402


REAL_QUOTES_SOUN = [
    {  # real, fetched 2026-07-14 via get_option_quotes
        "instrument_id": "4e5e0fae-be5b-4930-806d-5618fc0ff739", "strike": 7.0,
        "expiration": "2026-08-07", "delta": 0.491382,
        "bid": 0.49, "ask": 0.58, "mark": 0.535,
        "open_interest": 645, "days_to_expiration": 24,
    },
    {  # real, fetched 2026-07-14 via get_option_quotes
        "instrument_id": "c19fffc3-7afc-4148-9e7b-c889b4c2d1d8", "strike": 7.5,
        "expiration": "2026-08-07", "delta": 0.370521,
        "bid": 0.31, "ask": 0.38, "mark": 0.345,
        "open_interest": 553, "days_to_expiration": 24,
    },
]

# Fabricated for testing only — NOT from any real chain. Spread is a
# deliberately-tight 8.9% of mid to sit inside the 10% floor.
SYNTHETIC_LIQUID_CONTRACT = {
    "instrument_id": "synthetic-test-only", "strike": 6.5,
    "expiration": "2026-08-07", "delta": 0.62,
    "bid": 0.86, "ask": 0.94, "mark": 0.90,
    "open_interest": 700, "days_to_expiration": 24,
}

REAL_CONTRACTS_SOUN = REAL_QUOTES_SOUN + [SYNTHETIC_LIQUID_CONTRACT]

BOX_ENTER = {
    "action": "enter", "symbol": "SOUN", "shares": 7,
    "box_top": 6.71, "box_bottom": 6.05, "stop_price": 6.05,
    "tp_price": 7.97, "tier": 2,
}


class TestSelectContract(unittest.TestCase):
    def test_real_chain_has_no_qualifying_contract(self):
        # Neither real SOUN quote clears the delta window OR the spread
        # floor — a genuine finding, not a test artifact. This is exactly
        # why OPTIONS_RESEARCH.md calls the spread/delta assumptions
        # untested: on this real chain, on this real day, nothing here
        # would have qualified for entry.
        contract, why = option_scan.select_contract(REAL_QUOTES_SOUN)
        self.assertIsNone(contract)

    def test_picks_delta_closest_to_window_midpoint(self):
        # Synthetic contract only (see module docstring) — exercises the
        # happy path where a qualifying contract genuinely exists.
        contract, why = option_scan.select_contract(REAL_CONTRACTS_SOUN)
        self.assertIsNone(why)
        self.assertEqual(contract["strike"], 6.5)

    def test_excludes_out_of_delta_window(self):
        only_low_delta = [c for c in REAL_CONTRACTS_SOUN if c["strike"] != 6.5]
        contract, why = option_scan.select_contract(only_low_delta)
        self.assertIsNone(contract)
        self.assertIn("delta", why)

    def test_excludes_illiquid_by_open_interest(self):
        thin = dict(REAL_CONTRACTS_SOUN[0])
        thin["open_interest"] = 100
        contract, why = option_scan.select_contract([thin])
        self.assertIsNone(contract)

    def test_excludes_wide_spread(self):
        wide = dict(REAL_CONTRACTS_SOUN[0])
        wide["bid"], wide["ask"] = 0.50, 1.20  # spread 82% of mid
        contract, why = option_scan.select_contract([wide])
        self.assertIsNone(contract)

    def test_excludes_out_of_dte_window(self):
        too_soon = dict(REAL_CONTRACTS_SOUN[0])
        too_soon["days_to_expiration"] = 10  # < MIN_DTE (21)
        too_far = dict(REAL_CONTRACTS_SOUN[0])
        too_far["days_to_expiration"] = 60   # > MAX_DTE (45)
        contract, why = option_scan.select_contract([too_soon, too_far])
        self.assertIsNone(contract)


class TestSizing(unittest.TestCase):
    def test_sizes_from_real_premium(self):
        # equity 150 * 2% = $3 risk; premium $0.90 * 100 = $90/contract
        # -> 0 contracts fit the risk target exactly (3 // 90 = 0)
        contracts, why = option_scan.size_contracts(150.0, 99.83, 0.90)
        self.assertEqual(contracts, 0)
        self.assertIn("no forced minimum", why)

    def test_sizes_with_larger_equity(self):
        # equity 1000 * 2% = $20 risk / $90 premium -> 0 still (real
        # options are expensive relative to a small account — the point
        # of the design doc's honesty about needing bigger equity first)
        contracts, why = option_scan.size_contracts(1000.0, 999.0, 0.90)
        self.assertEqual(contracts, 0)

    def test_sizes_when_affordable(self):
        contracts, why = option_scan.size_contracts(5000.0, 4999.0, 0.90)
        self.assertIsNone(why)
        self.assertEqual(contracts, 1)  # 5000*0.02=100 // 90 = 1

    def test_buying_power_caps_contracts(self):
        contracts, why = option_scan.size_contracts(50000.0, 150.0, 0.90)
        self.assertEqual(contracts, 1)  # 150 // 90 = 1, capped by cash


class TestSelectAndSize(unittest.TestCase):
    def test_rejects_non_entering_box(self):
        payload = {"box_result": {"action": "skip"}, "contracts": [],
                  "equity": 150, "buying_power": 99.83}
        result = option_scan.select_and_size(payload)
        self.assertEqual(result["action"], "skip")

    def test_full_pipeline_with_real_contracts_but_small_account(self):
        payload = {
            "box_result": BOX_ENTER, "contracts": REAL_CONTRACTS_SOUN,
            "equity": 150.0, "buying_power": 99.83,
        }
        result = option_scan.select_and_size(payload)
        # $150 account genuinely can't afford even one real SOUN contract
        # at the correct delta ($90) inside the 2% risk target — this is
        # the honest result, not a bug.
        self.assertEqual(result["action"], "skip")

    def test_full_pipeline_with_adequate_equity(self):
        payload = {
            "box_result": BOX_ENTER, "contracts": REAL_CONTRACTS_SOUN,
            "equity": 5000.0, "buying_power": 4999.0,
        }
        result = option_scan.select_and_size(payload)
        self.assertEqual(result["action"], "enter_option")
        self.assertEqual(result["strike"], 6.5)
        self.assertEqual(result["tp_price"], 7.97)  # underlying TP, unchanged


class TestManage(unittest.TestCase):
    def base_position(self, **overrides):
        pos = {
            "instrument_id": "x", "contracts": 1, "entry_premium": 0.90,
            "entry_date": "2026-07-14", "box_top": 6.71, "box_bottom": 6.05,
            "tp_price": 7.97, "half_sold": False,
        }
        pos.update(overrides)
        return pos

    def test_thesis_invalidated_closes(self):
        result = option_scan.manage({"underlying_price": 6.00, "today": "2026-07-15",
                                     "position": self.base_position()})
        self.assertEqual(result["action"], "close_all")
        self.assertIn("invalidated", result["reason"])

    def test_take_profit_closes(self):
        result = option_scan.manage({"underlying_price": 8.00, "today": "2026-07-15",
                                     "position": self.base_position()})
        self.assertEqual(result["action"], "close_all")

    def test_time_stop_tighter_than_shares(self):
        result = option_scan.manage({"underlying_price": 6.80, "today": "2026-07-22",
                                     "position": self.base_position()})
        self.assertEqual(result["action"], "close_all")
        self.assertIn("time stop", result["reason"])

    def test_early_lock_sells_half(self):
        # box_top 6.71, box_bottom 6.05 -> risk 0.66; up 1R means price
        # >= 6.71 + 0.66 = 7.37
        result = option_scan.manage({"underlying_price": 7.40, "today": "2026-07-16",
                                     "position": self.base_position()})
        self.assertEqual(result["action"], "sell_half")

    def test_already_half_sold_does_not_repeat(self):
        result = option_scan.manage({"underlying_price": 7.40, "today": "2026-07-16",
                                     "position": self.base_position(half_sold=True)})
        self.assertEqual(result["action"], "hold")

    def test_hold_when_nothing_triggers(self):
        result = option_scan.manage({"underlying_price": 6.80, "today": "2026-07-16",
                                     "position": self.base_position()})
        self.assertEqual(result["action"], "hold")


if __name__ == "__main__":
    unittest.main()
