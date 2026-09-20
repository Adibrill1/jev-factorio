"""Backend protocol: how the agent observes and acts on a running game."""
from __future__ import annotations

from typing import Protocol

from ..state import GameSnapshot


class Backend(Protocol):
    def observe(self) -> GameSnapshot:
        """Read current game state."""
        ...

    def act(self, action: str) -> str:
        """Execute one macro action; return a human-readable outcome line."""
        ...
