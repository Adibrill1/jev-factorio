"""Adapter for the Factorio Learning Environment (MIT):
https://github.com/JackHopkins/factorio-learning-environment
Paper: https://arxiv.org/abs/2503.09617
PyPI: `pip install factorio-learning-environment` (needs Docker; runs a
headless Factorio server and exposes a Python REPL tool API).

SKELETON: fill in against `fle` package APIs once the cluster runs locally
(`fle cluster start`). FLE is built for LLM code-synthesis agents; here we
use only its server lifecycle + tool functions as our actuation layer.
"""
from __future__ import annotations

from ..state import GameSnapshot


class FleBackend:
    def __init__(self) -> None:
        self._instance = None  # fle server handle

    def start(self) -> None:
        # TODO: from fle import cluster / FactorioInstance; start headless server.
        raise NotImplementedError("start an FLE cluster first: `fle cluster start`")

    def observe(self) -> GameSnapshot:
        # TODO: use FLE tools: get_entities(), get_player_position(),
        #       inspect_inventory(), nearest(Resource.IronOre), ...
        raise NotImplementedError

    def act(self, action: str) -> str:
        # TODO: map macro actions to FLE tool calls, e.g.
        #   place_entity(Prototype.BurnerMiningDrill, position=nearest(Resource.IronOre))
        raise NotImplementedError
