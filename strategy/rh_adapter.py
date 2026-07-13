#!/usr/bin/env python3
"""Adapt Robinhood MCP responses to box_scan.py payload format.

CLI:
    python3 rh_adapter.py bars < historicals_response.json
        -> {"symbol": ..., "bars": [{date, open, high, low, close, volume}...]}

Input: the raw JSON from mcp__RobinHood__get_equity_historicals (the
"data" object or the full response). Bars are converted, interpolated
bars dropped, and ordering verified ascending. Fails loudly on anything
unexpected — a crash here means "do not trade this symbol this cycle."
"""

import json
import sys


def adapt_bars(response):
    data = response.get("data", response)
    results = data["results"]
    if len(results) != 1:
        raise ValueError(f"expected exactly 1 symbol result, got {len(results)}")
    r = results[0]
    if r.get("interval") != "day":
        raise ValueError(f"expected day interval, got {r.get('interval')}")
    bars = []
    for b in r["bars"]:
        if b.get("interpolated"):
            continue
        bars.append({
            "date": b["begins_at"][:10],
            "open": float(b["open_price"]),
            "high": float(b["high_price"]),
            "low": float(b["low_price"]),
            "close": float(b["close_price"]),
            "volume": int(b["volume"]),
        })
    dates = [b["date"] for b in bars]
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ValueError("bars not strictly ascending by date")
    return {"symbol": r["symbol"], "bars": bars}


def main():
    if len(sys.argv) != 2 or sys.argv[1] != "bars":
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    json.dump(adapt_bars(json.load(sys.stdin)), sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
