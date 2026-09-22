"""Live runner for the 24/7 stream: agent loop + OBS overlay + audit log.

Usage (on the Mac, cluster up, key in .env or the environment):

    python -m jev_factorio.live --backend fle

What it writes (defaults under ./stream/):
  - overlay.txt      the latest decision, rewritten every tick; point an OBS
                     Text source ("read from file") at it for the on-screen
                     decision log.
  - decisions.jsonl  one JSON record per decision (state, answers, action,
                     confidence, outcome) - the full audit trail.

Stop with Ctrl+C (or scripts/livestream_stop.sh). The Jev API key is read
from TYPESAFE_API_KEY (environment or a local .env) and is never printed.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

from .backends.mock import MockBackend
from .loop import AgentLoop


def load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader (KEY=VALUE lines); real env vars win."""
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def make_backend(name: str, fast: bool = False, speed: float = 1.0):
    if name == "mock":
        return MockBackend()
    if name == "fle":
        from .backends.fle import FleBackend
        backend = FleBackend(
            address=os.environ.get("FLE_ADDRESS", "localhost"),
            tcp_port=int(os.environ.get("FLE_RCON_PORT", "27000")),
            fast=fast, speed=speed)
        backend.start()
        return backend
    raise SystemExit(f"live runner supports backends: mock | fle (got {name!r})")


def render_overlay(record: dict, started_at: float, steps: int) -> str:
    uptime = int(time.time() - started_at)
    hours, rem = divmod(uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    return "\n".join([
        "Jev plays Factorio - LIVE",
        f"goal: {record['goal']}",
        f"action: {record['action']}  ({record['source']}, "
        f"confidence {record['confidence']:.2f})",
        f"stuck p={record['stuck_p']:.2f} | urgency: {record['urgency']}",
        f"last outcome: {record['outcome']}",
        f"decision #{steps} | game tick {record['tick']} | "
        f"uptime {hours:02d}:{minutes:02d}:{seconds:02d}",
    ])


def cli() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(prog="jev-factorio-live")
    p.add_argument("--backend", default=os.environ.get("JEV_BACKEND", "fle"))
    p.add_argument("--steps", type=int, default=0,
                   help="0 = run until stopped (Ctrl+C)")
    p.add_argument("--tick-seconds", type=float,
                   default=float(os.environ.get("JEV_TICK_SECONDS", "2")))
    p.add_argument("--confidence-floor", type=float,
                   default=float(os.environ.get("JEV_CONFIDENCE_FLOOR", "0.45")))
    p.add_argument("--overlay-file", default="stream/overlay.txt")
    p.add_argument("--log-file", default="stream/decisions.jsonl")
    p.add_argument("--fast", action="store_true",
                   help="FLE fast-forward mode (default off: real-time play)")
    p.add_argument("--speed", type=float, default=1.0, help="game speed")
    args = p.parse_args()

    if args.backend != "mock" and not os.environ.get("TYPESAFE_API_KEY"):
        raise SystemExit(
            "TYPESAFE_API_KEY is not set (environment or .env). "
            "Put the TypeSafe key in .env - never in chat or in git.")

    overlay_path = Path(args.overlay_file)
    log_path = Path(args.log_file)
    overlay_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    backend = make_backend(args.backend, fast=args.fast, speed=args.speed)
    loop = AgentLoop(backend, confidence_floor=args.confidence_floor,
                     tick_seconds=args.tick_seconds)

    started_at = time.time()
    steps = 0
    print(f"live runner up: backend={args.backend} "
          f"tick={args.tick_seconds}s overlay={overlay_path} log={log_path}")
    try:
        while args.steps == 0 or steps < args.steps:
            record = loop.step()
            steps += 1
            record["ts"] = datetime.now().isoformat(timespec="seconds")
            overlay_path.write_text(render_overlay(record, started_at, steps))
            with log_path.open("a") as f:
                f.write(json.dumps(record) + "\n")
            time.sleep(args.tick_seconds)
    except KeyboardInterrupt:
        pass
    print(f"live runner stopped after {steps} decisions "
          f"({int(time.time() - started_at)}s). Overlay and log kept in "
          f"{overlay_path.parent}/")


if __name__ == "__main__":
    cli()
