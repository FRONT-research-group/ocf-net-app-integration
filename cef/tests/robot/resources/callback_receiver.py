#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)

        text = raw.decode(errors="replace")

        try:
            payload = json.loads(text)

            # Current NEF callback may contain JSON encoded as a JSON string.
            if isinstance(payload, str):
                payload = json.loads(payload)

            rendered = json.dumps(payload, sort_keys=True)

        except Exception:
            rendered = text

        print("\n=== CALLBACK RECEIVED ===", flush=True)
        print("Path:", self.path, flush=True)
        print(rendered, flush=True)
        print("=========================\n", flush=True)

        self.send_response(204)
        self.end_headers()

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)


print("Listening on 0.0.0.0:8001", flush=True)

ThreadingHTTPServer(
    ("0.0.0.0", 8001),
    Handler
).serve_forever()
