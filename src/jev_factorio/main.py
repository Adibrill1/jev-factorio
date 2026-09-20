"""CLI: python -m jev_factorio --backend mock --steps 8"""
from __future__ import annotations

import argparse
import os

from .backends.mock import MockBackend
from .loop import AgentLoop


def make_backend(name: str):
    if name == "mock":
        return MockBackend()
    if name == "play_api":
        from .backends.play_api import PlayApiBackend
        return PlayApiBackend(factorio_user_dir=os.environ.get(
            "FACTORIO_USER_DIR", "~/.factorio"))
    if name == "fle":
        from .backends.fle import FleBackend
        b = FleBackend()
        b.start()
        return b
    raise SystemExit(f"unknown backend: {name}")


def cli() -> None:
    p = argparse.ArgumentParser(prog="jev-factorio")
    p.add_argument("--backend", default=os.environ.get("JEV_BACKEND", "mock"))
    p.add_argument("--steps", type=int, default=8)
    p.add_argument("--tick-seconds", type=float,
                   default=float(os.environ.get("JEV_TICK_SECONDS", "0")))  # 0 in mock
    p.add_argument("--confidence-floor", type=float,
                   default=float(os.environ.get("JEV_CONFIDENCE_FLOOR", "0.45")))
    args = p.parse_args()
    AgentLoop(make_backend(args.backend),
              confidence_floor=args.confidence_floor,
              tick_seconds=args.tick_seconds).run(steps=args.steps)


if __name__ == "__main__":
    cli()
