"""Command-line entry point: vibe-trading serve [--host HOST] [--port PORT]."""

import argparse
import sys
from pathlib import Path

from . import __version__, server


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="vibe-trading",
        description="Read-only dashboard over the Box Swing agent's state files.",
    )
    parser.add_argument("--version", action="version",
                        version=f"vibe-trading {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    serve_p = sub.add_parser("serve", help="serve the dashboard over HTTP")
    serve_p.add_argument("--host", default="127.0.0.1",
                         help="bind address (default: 127.0.0.1)")
    serve_p.add_argument("--port", type=int, default=8899,
                         help="port to listen on (default: 8899)")
    serve_p.add_argument("--root", default=".",
                         help="repo root containing state/ (default: cwd)")

    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not (root / "state").is_dir():
        parser.error(f"no state/ directory under {root} — "
                     "run from the Trading repo or pass --root")
    server.serve(root, args.host, args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
