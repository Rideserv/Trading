import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from vibe_trading import dashboard, status


def make_root(tmp, account=None, trades=None, run_log="line one\n"):
    root = Path(tmp)
    state = root / "state"
    state.mkdir()
    if account is not None:
        (state / "account_state.json").write_text(json.dumps(account))
    if trades is not None:
        (state / "trade_log.json").write_text(json.dumps(trades))
    (state / "run_log.txt").write_text(run_log)
    return root


CLEAN_ACCOUNT = {
    "account_number": "995042041", "mode": "live",
    "first_live_cycle_done": False, "equity": 150.0,
    "settled_cash": 150.0, "unsettled_cash": 0.0,
    "consecutive_losses": 0, "suspended_until": None,
    "drawdown_stop": False, "bench": {},
}


class TestStatus(unittest.TestCase):
    def test_clean_state_allows_trading(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp, CLEAN_ACCOUNT, [])
            s = status.load_status(root, today="2026-07-14")
        self.assertTrue(s["trading_allowed"])
        self.assertEqual(s["blocked_reasons"], [])
        self.assertEqual(s["run_log"], ["line one"])

    def test_missing_state_fails_closed(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp, account=None, trades=None)
            s = status.load_status(root, today="2026-07-14")
        self.assertFalse(s["trading_allowed"])
        self.assertIn("state unreadable (fail closed)", s["blocked_reasons"])

    def test_breakers_block(self):
        acct = dict(CLEAN_ACCOUNT, consecutive_losses=3,
                    suspended_until="2026-07-15", drawdown_stop=True,
                    bench={"PLUG": {"losses": 3}, "MARA": {"losses": 1}})
        with TemporaryDirectory() as tmp:
            root = make_root(tmp, acct, [])
            s = status.load_status(root, today="2026-07-14")
        self.assertFalse(s["trading_allowed"])
        self.assertEqual(len(s["blocked_reasons"]), 3)
        self.assertEqual(s["benched_symbols"], ["PLUG"])

    def test_expired_suspension_clears(self):
        acct = dict(CLEAN_ACCOUNT, suspended_until="2026-07-13")
        with TemporaryDirectory() as tmp:
            root = make_root(tmp, acct, [])
            s = status.load_status(root, today="2026-07-14")
        self.assertTrue(s["trading_allowed"])


class TestDashboard(unittest.TestCase):
    def test_render_escapes_and_includes_state(self):
        trades = [{"symbol": "<SOUN>", "action": "entry", "price": 5.25,
                   "shares": 1, "tier": 1, "notes": "SHADOW — no order placed"}]
        with TemporaryDirectory() as tmp:
            root = make_root(tmp, CLEAN_ACCOUNT, trades)
            html = dashboard.render(status.load_status(root, today="2026-07-14"))
        self.assertIn("$150.00", html)
        self.assertIn("&lt;SOUN&gt;", html)
        self.assertNotIn("<SOUN>", html)
        self.assertIn("first-live-cycle validation pending", html)

    def test_render_empty_journal(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp, CLEAN_ACCOUNT, [])
            html = dashboard.render(status.load_status(root, today="2026-07-14"))
        self.assertIn("No journaled trades yet.", html)


if __name__ == "__main__":
    unittest.main()
