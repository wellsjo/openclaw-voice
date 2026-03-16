#!/usr/bin/env python3
"""
ensure_tts.py - self-heal and start the local Pocket TTS server.

Goals:
- Keep the skill portable: no machine-specific venv assumptions
- Recover from broken virtualenvs after Python/Homebrew upgrades
- Start the server on localhost:8001 when needed
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = ROOT / ".venv"
VENV_PYTHON = VENV_DIR / "bin" / "python"
LOG_PATH = Path("/tmp/tts.log")
HEALTH_URL = "http://127.0.0.1:8001/health"
MIN_PYTHON = (3, 10)
MAX_PYTHON = (3, 15)
WAIT_SECONDS = 180


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def healthcheck(timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def port_open(host: str = "127.0.0.1", port: int = 8001, timeout: float = 1.0) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        sock.close()


def supported(version: tuple[int, int]) -> bool:
    return MIN_PYTHON <= version < MAX_PYTHON


def python_candidates() -> Iterable[str]:
    override = os.environ.get("TTS_PYTHON")
    if override:
        yield override
    for name in ("python3.11", "python3.12", "python3.13", "python3.14", "python3.10", "python3"):
        yield name


def python_version(executable: str) -> tuple[int, int] | None:
    path = shutil.which(executable) or executable
    try:
        result = subprocess.run(
            [path, "-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"],
            capture_output=True,
            text=True,
            check=True,
        )
        major, minor = result.stdout.strip().split(".")
        version = (int(major), int(minor))
        return version if supported(version) else None
    except Exception:
        return None


def pick_python() -> str:
    for candidate in python_candidates():
        version = python_version(candidate)
        if version is not None:
            return shutil.which(candidate) or candidate
    raise SystemExit(
        "ERROR: No supported Python found. Install python 3.10-3.14 or set TTS_PYTHON to a supported interpreter."
    )


def venv_is_healthy() -> bool:
    if not VENV_PYTHON.exists():
        return False
    try:
        subprocess.run(
            [str(VENV_PYTHON), "-c", "import pocket_tts, fastapi, uvicorn, soundfile"],
            capture_output=True,
            check=True,
        )
        return True
    except Exception:
        return False


def rebuild_venv(verbose: bool = True) -> None:
    python = pick_python()
    if verbose:
        print(f"Rebuilding TTS venv with {python}...")

    if VENV_DIR.exists():
        shutil.rmtree(VENV_DIR)

    subprocess.run([python, "-m", "venv", str(VENV_DIR)], cwd=ROOT, check=True)
    subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT, check=True)
    subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "-r", "requirements.txt"], cwd=ROOT, check=True)


def ensure_runtime(verbose: bool = True) -> None:
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ERROR: ffmpeg is required. Install it first (macOS: brew install ffmpeg).")

    if venv_is_healthy():
        if verbose:
            print("TTS runtime looks healthy.")
        return

    rebuild_venv(verbose=verbose)


def start_server(background: bool = True, verbose: bool = True) -> None:
    if healthcheck():
        if verbose:
            print("TTS server already healthy on localhost:8001.")
        return

    if port_open() and not healthcheck():
        raise SystemExit("ERROR: Port 8001 is in use, but the TTS healthcheck failed. Clear that process or free the port.")

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if background:
        with LOG_PATH.open("ab") as log_file:
            subprocess.Popen(
                [str(VENV_PYTHON), "pocketapi.py"],
                cwd=ROOT,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        if verbose:
            print(f"Starting TTS server in background; log: {LOG_PATH}")
    else:
        if verbose:
            print("Starting TTS server in foreground...")
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), "pocketapi.py"])


def wait_for_health(timeout_seconds: int = WAIT_SECONDS) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if healthcheck(timeout=5.0):
            return
        time.sleep(2)
    raise SystemExit(f"ERROR: TTS server did not become healthy within {timeout_seconds} seconds. Check {LOG_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ensure local Pocket TTS is installed and healthy")
    parser.add_argument("--install-only", action="store_true", help="Repair/install the runtime but do not start the server")
    parser.add_argument("--foreground", action="store_true", help="Start the server in the foreground")
    parser.add_argument("--no-wait", action="store_true", help="Do not wait for health after background start")
    parser.add_argument("--quiet", action="store_true", help="Reduce output")
    args = parser.parse_args()

    verbose = not args.quiet
    ensure_runtime(verbose=verbose)

    if args.install_only:
        return

    if args.foreground:
        start_server(background=False, verbose=verbose)
        return

    start_server(background=True, verbose=verbose)
    if not args.no_wait:
        wait_for_health()
        if verbose:
            print("TTS server is healthy.")


if __name__ == "__main__":
    main()
