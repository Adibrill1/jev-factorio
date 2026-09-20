"""Adapter for the Factorio Play API mod (MIT, Factorio 2.0):
https://mods.factorio.com/mod/factorio-agent-api
Source: https://github.com/kovan/factorio-play-api

The mod writes `script-output/agent-gamestate.json` every second and answers
`/agent ...` console commands via `script-output/agent-response.txt`.
Commands are injected through the server RCON console.

SKELETON: wire the paths for your install before use.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from ..state import GameSnapshot


class PlayApiBackend:
    def __init__(self, factorio_user_dir: str, rcon_host: str = "127.0.0.1",
                 rcon_port: int = 27015, rcon_password: str = "") -> None:
        self.out_dir = Path(factorio_user_dir) / "script-output"
        self.rcon_host, self.rcon_port, self.rcon_password = (
            rcon_host, rcon_port, rcon_password)

    def observe(self) -> GameSnapshot:
        raw = json.loads((self.out_dir / "agent-gamestate.json").read_text())
        # TODO: map the mod's JSON schema onto GameSnapshot fields.
        return GameSnapshot(tick=raw.get("tick", 0))

    def act(self, action: str) -> str:
        cmd = self._to_agent_command(action)
        self._rcon(f"/agent {cmd}")
        # The mod answers asynchronously; poll the response file briefly.
        deadline = time.time() + 2.0
        resp_file = self.out_dir / "agent-response.txt"
        while time.time() < deadline:
            if resp_file.exists() and resp_file.stat().st_size:
                return resp_file.read_text()
            time.sleep(0.1)
        return "(no response from game)"

    def _to_agent_command(self, action: str) -> str:
        # TODO: full mapping; MVP examples:
        return {
            "walk_to_iron": "walk direction=east",  # real impl: direction from positions
            "mine_iron": "mine x=0 y=0",
            "place_burner_drill": "build name=burner-mining-drill x=0 y=0",
        }.get(action, "status")

    def _rcon(self, command: str) -> None:
        # TODO: replace with a real Source-RCON client (e.g. the `rcon` pip package).
        subprocess.run(["echo", command], check=False)  # placeholder
