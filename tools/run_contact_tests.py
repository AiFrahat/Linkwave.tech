#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run local integration tests for the secure contact form.
Creates an isolated copy of the site with a test form endpoint, starts the mock
server, runs the Playwright suite, then stops the server. No external calls, no email.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PORT = 8796
TEST_CONFIG = (
    "window.LINKWAVE_CONFIG = {\n"
    "  phone: null,\n  email: 'info@linkwave.tech',\n  address: null,\n"
    "  whatsapp: '201276668018',\n  formEndpoint: '/__form',\n  formCooldownMs: 200\n};\n"
)


def main() -> int:
    temp = Path(tempfile.mkdtemp(prefix="linkwave-contact-test-"))
    site = temp / "site"
    shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules"))
    (site / "js" / "site-config.js").write_text(TEST_CONFIG, encoding="utf-8")
    server = subprocess.Popen(
        [sys.executable, str(TOOLS / "mock_form_server.py"),
         "--dir", str(site), "--port", str(PORT)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen("http://127.0.0.1:%d/__stats" % PORT, timeout=1)
                break
            except Exception:
                time.sleep(0.25)
        env = os.environ.copy()
        env["BASE_URL"] = "http://127.0.0.1:%d/" % PORT
        env["SITE_ROOT"] = str(site)
        env["OUT_DIR"] = os.environ.get("OUT_DIR", str(temp / "results"))
        result = subprocess.run(
            ["node", str(TOOLS / "test_contact_form.cjs")],
            cwd=str(ROOT), env=env,
        )
        return result.returncode
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
        shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
