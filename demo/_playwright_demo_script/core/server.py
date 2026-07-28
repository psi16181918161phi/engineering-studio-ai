"""WHAT: Boots the demo FastAPI/uvicorn server on a free local port and
waits for its `/api/health` endpoint to report healthy.
WHY: Isolates all subprocess/network I/O behind two small functions so
the rest of the package (and its tests) never spawn a real process
directly — easy to mock (SOLID SRP, matches
`scripts/_sync_submodules/core/syncer.py`'s isolation pattern).
HOW: `free_port()` binds an ephemeral OS-assigned port; `start_server()`
launches `uvicorn engineering_studio.webapp:app` as a subprocess and
polls `/api/health` until it responds 200 or the deadline elapses.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import requests

from ..exceptions.errors import ServerStartError

REPO_ROOT = Path(__file__).resolve().parents[3]


def free_port() -> int:
    """WHAT: Returns an OS-assigned free TCP port on localhost.

    RETURNS:
        int: A currently-unused port number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_server(
    live: bool, *, startup_timeout: float = 15.0
) -> tuple[subprocess.Popen[bytes], str]:
    """WHAT: Starts the demo web server and waits until it is healthy.

    ARGS:
        live (bool): If `False` (default), sets
            `ENGINEERING_STUDIO_FAKE_PIPELINE=1` so the deterministic
            mocked pipeline is used (Mode B, no API key required).
        startup_timeout (float): Max seconds to wait for `/api/health`
            to return HTTP 200 before raising.

    RETURNS:
        tuple[subprocess.Popen[bytes], str]: The running process and its
        base URL.

    RAISES:
        ServerStartError: If the server does not become healthy within
        `startup_timeout` seconds. The spawned process is terminated
        before raising — never leaked on failure.
    """
    port = free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = dict(os.environ)
    if not live:
        env["ENGINEERING_STUDIO_FAKE_PIPELINE"] = "1"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "engineering_studio.webapp:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        env=env,
        cwd=REPO_ROOT,
    )
    deadline = time.time() + startup_timeout
    while time.time() < deadline:
        try:
            if requests.get(f"{base_url}/api/health", timeout=0.5).status_code == 200:
                return process, base_url
        except requests.RequestException:
            pass
        time.sleep(0.2)
    process.terminate()
    raise ServerStartError("demo server did not become healthy in time")
