"""Server-side HTML rendering for the dashboard. No external assets."""

import html

_STYLE = """
:root {
  color-scheme: light dark;
  --page: #f9f9f7; --surface: #fcfcfb;
  --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --hairline: #e1e0d9; --ring: rgba(11,11,11,0.10);
  --good: #0ca30c; --good-text: #006300;
  --warning: #fab219; --critical: #d03b3b;
}
@media (prefers-color-scheme: dark) {
  :root {
    --page: #0d0d0d; --surface: #1a1a19;
    --ink: #ffffff; --ink-2: #c3c2b7; --muted: #898781;
    --hairline: #2c2c2a; --ring: rgba(255,255,255,0.10);
    --good-text: #0ca30c;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 24px; background: var(--page); color: var(--ink);
  font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
}
main { max-width: 960px; margin: 0 auto; }
h1 { font-size: 18px; margin: 0; }
h2 { font-size: 13px; color: var(--ink-2); text-transform: uppercase;
     letter-spacing: 0.04em; margin: 28px 0 10px; }
header { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
header .sub { color: var(--muted); font-size: 12px; }
.badges { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.badge {
  display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px;
  border: 1px solid var(--ring); border-radius: 999px;
  background: var(--surface); font-size: 12px; font-weight: 600;
}
.badge .dot { width: 8px; height: 8px; border-radius: 50%; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
         gap: 12px; }
.tile { background: var(--surface); border: 1px solid var(--ring);
        border-radius: 8px; padding: 12px 14px; }
.tile .label { font-size: 11px; color: var(--muted); text-transform: uppercase;
               letter-spacing: 0.04em; }
.tile .value { font-size: 24px; font-weight: 600; margin-top: 2px; }
.tile .note { font-size: 12px; color: var(--ink-2); }
.tablewrap { overflow-x: auto; background: var(--surface);
             border: 1px solid var(--ring); border-radius: 8px; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th { text-align: left; color: var(--muted); font-weight: 600; }
th, td { padding: 7px 12px; border-bottom: 1px solid var(--hairline);
         white-space: nowrap; }
tr:last-child td { border-bottom: none; }
td.num { font-variant-numeric: tabular-nums; text-align: right; }
.empty { color: var(--muted); padding: 14px; }
.runlog { background: var(--surface); border: 1px solid var(--ring);
          border-radius: 8px; padding: 10px 14px; overflow-x: auto;
          font: 12px/1.7 ui-monospace, monospace; color: var(--ink-2);
          white-space: pre; margin: 0; }
.alert { border-left: 3px solid var(--critical); background: var(--surface);
         padding: 10px 14px; border-radius: 0 8px 8px 0; margin-top: 12px; }
footer { color: var(--muted); font-size: 12px; margin-top: 28px; }
"""

_TRADE_COLS = [
    ("timestamp", "Time (CT)"), ("symbol", "Sym"), ("action", "Action"),
    ("price", "Price"), ("shares", "Shares"), ("tier", "Tier"),
    ("stop_price", "Stop"), ("tp_price", "TP"), ("points", "Pts"),
    ("notes", "Notes"),
]
_NUM_COLS = {"price", "shares", "stop_price", "tp_price", "points"}


def _esc(v):
    return html.escape("" if v is None else str(v))


def _badge(label, color):
    return (f'<span class="badge"><span class="dot" '
            f'style="background:{color}"></span>{_esc(label)}</span>')


def _money(v):
    try:
        return f"${float(v):,.2f}"
    except (TypeError, ValueError):
        return "—"


def render(status):
    acct = status["account"]
    out = ['<meta charset="utf-8">',
           '<meta http-equiv="refresh" content="30">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           "<title>vibe-trading</title>",
           f"<style>{_STYLE}</style>", "<main>"]

    out.append('<header><h1>vibe-trading — Box Swing v1.0</h1>'
               f'<span class="sub">account ••••{_esc(str(acct.get("account_number", ""))[-4:])}'
               f' · as of {_esc(status["as_of"])} · read-only</span></header>')

    mode = acct.get("mode") or "shadow"
    badges = [
        _badge("trading allowed", "var(--good)") if status["trading_allowed"]
        else _badge("trading blocked", "var(--critical)"),
        _badge(f"mode: {mode}",
               "var(--good)" if mode == "live" else "var(--warning)"),
    ]
    if not acct.get("first_live_cycle_done", True):
        badges.append(_badge("first-live-cycle validation pending", "var(--warning)"))
    if acct.get("drawdown_stop"):
        badges.append(_badge("drawdown stop", "var(--critical)"))
    out.append(f'<div class="badges">{"".join(badges)}</div>')

    for reason in status["blocked_reasons"] + status["errors"]:
        out.append(f'<div class="alert">⚠ {_esc(reason)}</div>')

    losses = acct.get("consecutive_losses", 0)
    tiles = [
        ("Equity", _money(acct.get("equity")), ""),
        ("Settled cash", _money(acct.get("settled_cash")), ""),
        ("Unsettled cash", _money(acct.get("unsettled_cash")), ""),
        ("Consecutive losses", str(losses), "limit 3"),
        ("Benched symbols",
         str(len(status["benched_symbols"])),
         ", ".join(status["benched_symbols"]) or "none"),
    ]
    out.append("<h2>Account</h2><div class='tiles'>")
    for label, value, note in tiles:
        out.append(f'<div class="tile"><div class="label">{_esc(label)}</div>'
                   f'<div class="value">{_esc(value)}</div>'
                   + (f'<div class="note">{_esc(note)}</div>' if note else "")
                   + "</div>")
    out.append("</div>")

    out.append("<h2>Trade journal</h2>")
    trades = status["trades"]
    if not trades:
        out.append('<div class="tablewrap"><div class="empty">No journaled trades yet.</div></div>')
    else:
        rows = ["<tr>" + "".join(f"<th>{h}</th>" for _, h in _TRADE_COLS) + "</tr>"]
        for t in reversed(trades):
            cells = []
            for key, _ in _TRADE_COLS:
                cls = ' class="num"' if key in _NUM_COLS else ""
                cells.append(f"<td{cls}>{_esc(t.get(key, ''))}</td>")
            rows.append("<tr>" + "".join(cells) + "</tr>")
        out.append(f'<div class="tablewrap"><table>{"".join(rows)}</table></div>')

    out.append("<h2>Run log (last %d lines)</h2>" % len(status["run_log"])
               if status["run_log"] else "<h2>Run log</h2>")
    log_text = "\n".join(status["run_log"]) or "run_log.txt is empty."
    out.append(f'<pre class="runlog">{_esc(log_text)}</pre>')

    out.append("<footer>Read-only view of <code>state/</code>. "
               "This page never places, cancels, or modifies orders. "
               "Auto-refreshes every 30s.</footer></main>")
    return "".join(out)
