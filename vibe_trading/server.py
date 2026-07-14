"""HTTP server for the dashboard. Stdlib only, GET-only, read-only."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import dashboard, status


class DashboardHandler(BaseHTTPRequestHandler):
    root = None  # set by serve()

    def _send(self, code, body, content_type):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            payload = status.load_status(self.root)
            self._send(200, dashboard.render(payload), "text/html")
        elif path == "/api/status":
            payload = status.load_status(self.root)
            self._send(200, json.dumps(payload, indent=2), "application/json")
        elif path == "/healthz":
            self._send(200, "ok", "text/plain")
        else:
            self._send(404, "not found", "text/plain")

    def log_message(self, fmt, *args):
        pass  # keep the agent's terminal quiet; run_log.txt is the record


def serve(root, host, port):
    handler = type("BoundHandler", (DashboardHandler,), {"root": root})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"vibe-trading dashboard: http://{host}:{port}/ (state root: {root})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
