"""Factorio Learning Environment (FLE) backend - the live game interface.

Implemented against FLE v0.4.x (pinned in pyproject; MIT license):
https://github.com/JackHopkins/factorio-learning-environment

Prereqs on the Mac:
  - Docker running via Colima (already installed), FLE cluster up: `fle cluster start`
  - pip install "factorio-learning-environment==0.4.3"

FLE runs the official headless Factorio server in Docker. Cluster instance 0
listens for the Factorio *client* on localhost:34197 and for RCON on
localhost:27000 (fle/cluster/run_envs.py). The paid Factorio app joins
localhost:34197 as a spectator so OBS has real pixels to capture.

This adapter uses only FLE's server lifecycle + tool API (get_entities,
nearest, move_to, harvest_resource, place_entity, insert_item, craft_item,
inspect_inventory) as the observe/act layer; Jev decides *what*, this code
owns *how*.
"""
from __future__ import annotations

import math

from ..state import GameSnapshot

# FLE cluster defaults (fle/cluster/run_envs.py): instance i gets host RCON
# port START_RCON_PORT + i and game port 34197 + i.
RCON_PORT = 27000  # instance 0
GAME_PORT = 34197  # the Factorio app connects here to watch (Multiplayer)

# MVP bootstrap: the player starts with one burner drill, mirroring the first
# rung of FLE's own eval ladder (see docs/ARCHITECTURE.md, section 4).
STARTER_INVENTORY = {"burner-mining-drill": 1}

# Resources we track as candidate mining targets.
_TRACKED_RESOURCES = ("iron-ore", "coal", "copper-ore", "stone")


class FleBackend:
    """Observe/act against a live headless Factorio server through FLE."""

    def __init__(self, address: str = "localhost", tcp_port: int = RCON_PORT,
                 fast: bool = False, speed: float = 1.0,
                 inventory: dict | None = None) -> None:
        self.address = address
        self.tcp_port = tcp_port
        # fast=True makes FLE fast-forward game ticks so actions finish
        # quickly; for the 24/7 livestream we want real-time play instead.
        self.fast = fast
        self.speed = speed
        self.inventory = dict(inventory if inventory is not None
                              else STARTER_INVENTORY)
        self.instance = None
        self.ns = None
        self._Prototype = None
        self._Resource = None

    def start(self) -> None:
        try:
            from fle.env.instance import FactorioInstance
            from fle.env.game_types import Prototype, Resource
        except ImportError as e:
            raise RuntimeError(
                "FLE is not installed. Run: pip install "
                "\"factorio-learning-environment==0.4.3\" (pinned; see "
                "docs/ARCHITECTURE.md), then start the cluster: fle cluster start"
            ) from e
        self._Prototype, self._Resource = Prototype, Resource
        self.instance = FactorioInstance(
            address=self.address, tcp_port=self.tcp_port, fast=self.fast,
            peaceful=True, inventory=self.inventory)
        self.instance.set_speed(self.speed)
        self.ns = self.instance.namespace

    # ---------------------------------------------------------------- observe

    def observe(self) -> GameSnapshot:
        self._require_started()
        pos = self.ns.player_location
        player_xy = (float(pos.x), float(pos.y))

        inv = {str(k): int(v) for k, v in self.ns.inspect_inventory().items()
               if v}

        near: dict[str, float] = {}
        for name in _TRACKED_RESOURCES:
            resource = getattr(self._Resource, _enum_name(name))
            try:
                patch = self.ns.nearest(resource)
            except Exception:
                continue  # not found within FLE's 500-tile search radius
            near[name] = round(math.dist(player_xy, (patch.x, patch.y)), 1)

        drills = self._safe_get_entities(self._Prototype.BurnerMiningDrill)
        furnaces = self._safe_get_entities(self._Prototype.StoneFurnace)
        placed = ([f"burner-mining-drill@{round(e.position.x)},"
                   f"{round(e.position.y)}" for e in drills]
                  + [f"stone-furnace@{round(e.position.x)},"
                     f"{round(e.position.y)}" for e in furnaces])

        alerts: list[str] = []
        for e in drills + furnaces:
            for w in getattr(e, "warnings", []) or []:
                alerts.append(f"{e.name}: {w}")

        return GameSnapshot(
            tick=int(self.instance.get_elapsed_ticks()),
            player_position=player_xy,
            inventory=inv,
            nearby_resources=near,
            placed_entities=placed,
            alerts=alerts,
        )

    # -------------------------------------------------------------------- act

    def act(self, action: str) -> str:
        self._require_started()
        try:
            return self._act(action)
        except Exception as e:
            # Failures must surface to the next observe() via alerts and to
            # the decision log; the loop keeps running.
            return f"error in {action}: {e}"

    def _act(self, action: str) -> str:
        P, R = self._Prototype, self._Resource
        ns = self.ns
        if action == "walk_to_iron":
            target = ns.nearest(R.IronOre)
            ns.move_to(target)
            return f"walked to iron patch at ({target.x:.0f},{target.y:.0f})"
        if action == "walk_to_coal":
            target = ns.nearest(R.Coal)
            ns.move_to(target)
            return f"walked to coal patch at ({target.x:.0f},{target.y:.0f})"
        if action == "mine_iron":
            got = ns.harvest_resource(ns.nearest(R.IronOre), 5)
            return f"mined {got} iron ore"
        if action == "mine_coal":
            got = ns.harvest_resource(ns.nearest(R.Coal), 5)
            return f"mined {got} coal"
        if action == "place_burner_drill":
            target = ns.nearest(R.IronOre)
            ns.move_to(target)
            e = ns.place_entity(P.BurnerMiningDrill, position=target,
                                exact=False)
            return (f"placed burner drill at "
                    f"({e.position.x:.0f},{e.position.y:.0f})")
        if action == "fuel_drill":
            drills = ns.get_entities({P.BurnerMiningDrill})
            if not drills:
                return "no drill placed yet"
            ns.insert_item(P.Coal, drills[0], 5)
            return "inserted 5 coal into burner drill"
        if action == "craft_stone_furnace":
            crafted = ns.craft_item(P.StoneFurnace, 1)
            return f"crafted {crafted} stone furnace"
        return "(idle)"

    # ----------------------------------------------------------------- utils

    def _safe_get_entities(self, prototype) -> list:
        try:
            return list(self.ns.get_entities({prototype}))
        except Exception:
            return []

    def _require_started(self) -> None:
        if self.instance is None or self.ns is None:
            raise RuntimeError("call start() first (fle cluster must be up)")


def _enum_name(resource_name: str) -> str:
    """'iron-ore' -> 'IronOre' (FLE's Resource enum member names)."""
    return "".join(part.capitalize() for part in resource_name.split("-"))
