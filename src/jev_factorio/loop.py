"""The agent loop: observe -> describe options -> Jev decides -> act.

Design notes
------------
* Cadence: macro decisions every `tick_seconds` (default 2s). Jev's 70-500 ms
  latency fits comfortably inside that budget; per-tick (60 UPS) control is
  neither affordable nor needed - Factorio is a planning game.
* Confidence gate: Choice answers carry `confidence` (0-1, from the answer
  distribution). Below the floor we run the scripted fallback instead,
  because Jev always picks a winner even when no option fits.
  See https://docs.typesafe.ai/patterns/confidence-routing.md
* One call per tick fans out goal/action/stuck/urgency questions together.
"""
from __future__ import annotations

import time

from .jev_client import make_client
from .questions import build_questions
from .state import GameSnapshot


def fallback_policy(snapshot: GameSnapshot) -> str:
    """Deterministic policy for low-confidence ticks (and the mock demo)."""
    if not snapshot.placed_entities and snapshot.inventory.get("burner-mining-drill"):
        if "coal" in snapshot.nearby_resources and snapshot.nearby_resources["coal"] > 0:
            return "walk_to_coal"
        return "mine_coal"
    return "idle"


class AgentLoop:
    def __init__(self, backend, jev=None, confidence_floor: float = 0.45,
                 tick_seconds: float = 2.0):
        self.backend = backend
        self.jev = jev or make_client()
        self.confidence_floor = confidence_floor
        self.tick_seconds = tick_seconds

    def step(self) -> dict:
        snapshot = self.backend.observe()
        answers = self.jev.evaluate(snapshot.for_jev(), build_questions(snapshot))

        action_ans = answers["next_action"]
        if action_ans["confidence"] >= self.confidence_floor:
            action = action_ans["choice"]
            source = "jev"
        else:
            action = fallback_policy(snapshot)
            source = "fallback"

        outcome = self.backend.act(action)
        record = {
            "tick": snapshot.tick, "goal": answers["goal"]["choice"],
            "action": action, "source": source,
            "confidence": action_ans["confidence"],
            "stuck_p": answers["is_stuck"]["noul"],
            "urgency": answers["urgency"]["score"], "outcome": outcome,
        }
        print(f"[t={record['tick']:>4}] {source:>8} -> {action:<20} "
              f"(conf {record['confidence']:.2f})  {outcome}")
        return record

    def run(self, steps: int = 10) -> None:
        for _ in range(steps):
            self.step()
            time.sleep(self.tick_seconds)
