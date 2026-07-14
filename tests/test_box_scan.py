"""Unit tests for box_scan.py — synthetic data, no network."""

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "strategy"))

import box_scan  # noqa: E402


def make_bars(n=21, base=10.0, height=1.0, volume=2_000_000,
              start_day=1):
    """n daily bars oscillating inside a box [base, base+height].

    The box top is printed early (bar 3) so the maturity rule passes.
    Last bar is 'today' (partial).
    """
    bars = []
    for i in range(n):
        day = start_day + i
        date = f"2026-06-{day:02d}" if day <= 30 else f"2026-07-{day - 30:02d}"
        if i == 3:
            high, low = base + height, base + height * 0.4  # sets box top
        else:
            high, low = base + height * 0.7, base + height * 0.1
        close = (high + low) / 2
        bars.append({"date": date, "open": low, "high": high, "low": base if i == 5 else low,
                     "close": close, "volume": volume})
    return bars


def eval_payload(**overrides):
    payload = {
        "symbol": "TEST",
        "equity": 150.0,
        "buying_power": 150.0,
        "price": 11.20,          # above box top of 11.0
        "quote_age_seconds": 10,
        "bars": make_bars(),
    }
    payload["bars"][-1]["volume"] = 6_000_000  # 3x avg -> volume confirmed
    payload.update(overrides)
    return payload


class TestEvaluate(unittest.TestCase):
    def test_clean_breakout_enters(self):
        result = box_scan.evaluate(eval_payload())
        self.assertEqual(result["action"], "enter")
        self.assertEqual(result["box_top"], 11.0)
        self.assertEqual(result["box_bottom"], 10.0)
        self.assertEqual(result["stop_price"], 10.0)
        self.assertEqual(result["tp_price"], 13.0)  # 11 + 2*1

    def test_sizing_respects_risk_target(self):
        result = box_scan.evaluate(eval_payload())
        # equity 150 * 2% = $3 risk; stop distance 1.20 -> floor = 2 shares
        self.assertEqual(result["shares"], 2)
        self.assertAlmostEqual(result["risk_dollars"], 2.4)

    def test_one_share_fallback_within_ceiling(self):
        # Stop distance $4 > $3 target but <= 5% ceiling ($7.50) -> 1 share
        p = eval_payload(price=14.0)
        p["bars"] = make_bars(base=10.0, height=3.5)  # box 10-13.5, but too wide?
        # height/top = 3.5/13.5 = 26% -> too wide; use tighter absolute prices
        p["bars"] = make_bars(base=20.0, height=4.0)  # 4/24 = 16.7% ok
        p["bars"][-1]["volume"] = 6_000_000
        p["price"] = 24.5  # stop distance 4.5 <= 7.5 ceiling
        result = box_scan.evaluate(p)
        self.assertEqual(result["action"], "enter")
        self.assertEqual(result["shares"], 1)

    def test_skip_when_risk_exceeds_ceiling(self):
        p = eval_payload(equity=60.0, buying_power=60.0)
        # stop distance 1.20 > 5% of 60 = $3.. wait 1.2 < 3 -> shares=1 ok.
        # force it: tiny equity
        p = eval_payload(equity=20.0, buying_power=20.0)
        # 2% = $0.40 -> 0 shares; distance 1.20 > 5% of 20 = $1.00 -> skip
        result = box_scan.evaluate(p)
        self.assertEqual(result["action"], "skip")
        self.assertIn("one share risks", result["reason"])

    def test_no_breakout_skips(self):
        result = box_scan.evaluate(eval_payload(price=10.8))
        self.assertEqual(result["action"], "skip")
        self.assertIn("no breakout", result["reason"])

    def test_insufficient_volume_skips(self):
        p = eval_payload()
        p["bars"][-1]["volume"] = 2_500_000  # 1.25x < 1.5x
        result = box_scan.evaluate(p)
        self.assertEqual(result["action"], "skip")
        self.assertIn("volume", result["reason"])

    def test_thin_liquidity_skips(self):
        p = eval_payload()
        for b in p["bars"]:
            b["volume"] = 300_000  # below 1M floor
        p["bars"][-1]["volume"] = 900_000
        result = box_scan.evaluate(p)
        self.assertEqual(result["action"], "skip")
        self.assertIn("liquidity", result["reason"])

    def test_wide_box_skips(self):
        p = eval_payload()
        p["bars"] = make_bars(base=10.0, height=4.0)  # 4/14 = 28.6% > 25%
        p["bars"][-1]["volume"] = 6_000_000
        p["price"] = 14.2
        result = box_scan.evaluate(p)
        self.assertEqual(result["action"], "skip")
        self.assertIn("too wide", result["reason"])

    def test_immature_box_skips(self):
        p = eval_payload()
        # Move the box-top print to 3 sessions before today
        bars = make_bars()
        bars[3], bars[-4] = copy.deepcopy(bars[-4]), copy.deepcopy(bars[3])
        dates = sorted(b["date"] for b in bars)
        for b, d in zip(bars, dates):
            b["date"] = d
        p["bars"] = bars
        p["bars"][-1]["volume"] = 6_000_000
        result = box_scan.evaluate(p)
        self.assertEqual(result["action"], "skip")
        self.assertIn("not mature", result["reason"])

    def test_stale_quote_refuses(self):
        result = box_scan.evaluate(eval_payload(quote_age_seconds=600))
        self.assertEqual(result["action"], "skip")
        self.assertIn("STALE", result["reason"])

    def test_descending_bars_rejected(self):
        p = eval_payload()
        p["bars"] = list(reversed(p["bars"]))
        result = box_scan.evaluate(p)
        self.assertEqual(result["action"], "skip")
        self.assertIn("ascending", result["reason"])

    def test_tier1_grading(self):
        p = eval_payload()
        p["bars"] = make_bars(base=10.0, height=1.4)  # 1.4/11.4 = 12.3% <= 15%
        p["bars"][-1]["volume"] = 7_000_000  # 3.5x
        p["price"] = 11.6
        result = box_scan.evaluate(p)
        self.assertEqual(result["action"], "enter")
        self.assertEqual(result["tier"], 1)

    def test_price_band(self):
        result = box_scan.evaluate(eval_payload(price=31.0))
        self.assertEqual(result["action"], "skip")
        # (also fails breakout band check first — either reason acceptable)
        self.assertIn("action", result)


def manage_payload(**overrides):
    bars = make_bars(n=8, base=10.0, height=1.0, start_day=1)
    payload = {
        "symbol": "TEST",
        "price": 11.5,
        "quote_age_seconds": 10,
        "today": "2026-06-09",
        "position": {
            "entry_price": 11.2, "shares": 2, "entry_date": "2026-06-02",
            "box_top": 11.0, "box_bottom": 10.0,
            "stop_price": 10.0, "tp_price": 13.0,
        },
        "bars": bars,
    }
    payload.update(overrides)
    return payload


class TestManage(unittest.TestCase):
    def test_take_profit(self):
        result = box_scan.manage(manage_payload(price=13.05))
        self.assertEqual(result["action"], "take_profit")

    def test_time_stop(self):
        bars = make_bars(n=15, base=10.0, height=1.0, start_day=1)
        result = box_scan.manage(manage_payload(
            bars=bars, today="2026-06-15", price=11.3))
        self.assertEqual(result["action"], "time_exit")

    def test_early_lock_raises_stop(self):
        p = manage_payload(price=12.5)  # up 1.3/1.2 = 1.08R
        # Make the last two completed bars show stall: red candle, lower
        # close, lower volume.
        p["bars"][-2] = {"date": "2026-06-07", "open": 12.6, "high": 12.7,
                         "low": 12.3, "close": 12.4, "volume": 1_500_000}
        p["bars"][-1] = {"date": "2026-06-08", "open": 12.4, "high": 12.5,
                         "low": 12.1, "close": 12.2, "volume": 1_000_000}
        p["today"] = "2026-06-09"
        result = box_scan.manage(p)
        self.assertEqual(result["action"], "raise_stop")
        self.assertEqual(result["new_stop"], 11.2)  # max(entry, box_top)

    def test_hold_when_nothing_triggers(self):
        result = box_scan.manage(manage_payload(price=11.4))
        self.assertEqual(result["action"], "hold")

    def test_stale_quote_holds(self):
        result = box_scan.manage(manage_payload(price=13.5,
                                                quote_age_seconds=999))
        self.assertEqual(result["action"], "hold")
        self.assertIn("STALE", result["reason"])


if __name__ == "__main__":
    unittest.main()
