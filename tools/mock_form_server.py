#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local test double for the Linkwave contact-form server contract.

Serves a copy of the website and implements POST /__form exactly as the documented
serverless contract does for validation/rate limiting; it never sends email.
Test-only: not part of the website, no secrets, no external requests.

Usage: python tools/mock_form_server.py --dir <site-copy> [--port 8796]
"""
from __future__ import annotations

import argparse
import json
import re
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_BODY = 16 * 1024
LIMITS = {"name": 100, "email": 254, "phone": 30, "subject": 150, "message": 3000}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
PHONE_RE = re.compile(r"^[+()0-9\s-]{7,30}$")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

state = {"submissions": 0, "valid": 0, "rejected": 0, "rate": 0, "last": None,
         "rate_window": {}, "requests": 0}


def validate(payload: dict) -> list[dict]:
    errors = []
    for field in ("name", "email", "subject", "message"):
        value = payload.get(field, "")
        if not isinstance(value, str) or not value.strip():
            errors.append({"field": field, "code": "required"})
    for field, limit in LIMITS.items():
        value = payload.get(field, "")
        if isinstance(value, str) and len(value) > limit:
            errors.append({"field": field, "code": "tooLong"})
        if isinstance(value, str) and CONTROL_RE.search(value):
            errors.append({"field": field, "code": "invalid"})
    email = payload.get("email", "")
    if isinstance(email, str) and email.strip() and not EMAIL_RE.match(email.strip()):
        errors.append({"field": "email", "code": "badEmail"})
    phone = payload.get("phone", "")
    if isinstance(phone, str) and phone.strip() and not PHONE_RE.match(phone.strip()):
        errors.append({"field": "phone", "code": "badPhone"})
    if any("\r" in str(payload.get(k, "")) or "\n" in str(payload.get(k, ""))
           for k in ("name", "email", "subject", "phone")):
        errors.append({"field": "subject", "code": "invalid"})
    return errors


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/__stats"):
            self._json(200, state)
            return
        if self.path.startswith("/__reset"):
            state.update({"submissions": 0, "valid": 0, "rejected": 0, "rate": 0,
                          "last": None, "rate_window": {}, "requests": 0})
            self._json(200, {"ok": True})
            return
        return super().do_GET()

    def do_POST(self):
        if self.path != "/__form":
            self._json(404, {"ok": False, "errors": [{"field": "", "code": "notFound"}]})
            return
        state["requests"] += 1
        ip = self.client_address[0]
        now = time.time()
        window = state["rate_window"].get(ip, [])
        window = [t for t in window if now - t < 10]
        if len(window) >= 2:
            state["rate"] += 1
            self._json(429, {"ok": False, "errors": [{"field": "", "code": "rateLimited"}]})
            return
        window.append(now)
        state["rate_window"][ip] = window
        cookie = self.headers.get("Cookie", "")
        if "scenario=error" in cookie:
            state["rejected"] += 1
            self._json(500, {"ok": False})
            return
        if "scenario=abort" in cookie:
            self.connection.close()
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > MAX_BODY:
            state["rejected"] += 1
            self._json(400, {"ok": False, "errors": [{"field": "", "code": "tooLarge"}]})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            state["rejected"] += 1
            self._json(400, {"ok": False, "errors": [{"field": "", "code": "invalidJson"}]})
            return
        if not isinstance(payload, dict):
            state["rejected"] += 1
            self._json(400, {"ok": False, "errors": [{"field": "", "code": "invalidJson"}]})
            return
        if str(payload.get("_gotcha", "")).strip():
            state["rejected"] += 1
            self._json(400, {"ok": False, "errors": [{"field": "", "code": "honeypot"}]})
            return
        errors = validate(payload)
        if errors:
            state["rejected"] += 1
            self._json(400, {"ok": False, "errors": errors})
            return
        state["submissions"] += 1
        state["valid"] += 1
        state["last"] = {k: payload.get(k) for k in ("name", "email", "phone", "subject", "message", "language")}
        # Accepted for delivery only — the mock never sends email.
        self._json(200, {"ok": True, "accepted": True, "id": "mock-%d" % state["submissions"]})

    def log_message(self, *args):
        pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    parser.add_argument("--port", type=int, default=8796)
    args = parser.parse_args()
    handler = lambda *a, **k: Handler(*a, directory=args.dir, **k)
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as httpd:
        print("mock contact server on http://127.0.0.1:%d/ -> %s" % (args.port, args.dir), flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
