"""Live runner plumbing: overlay + JSONL audit log, offline (mock backend)."""
import json
import subprocess
import sys
from pathlib import Path


def test_live_runner_writes_overlay_and_log(tmp_path):
    overlay = tmp_path / "overlay.txt"
    log = tmp_path / "decisions.jsonl"
    subprocess.run(
        [sys.executable, "-m", "jev_factorio.live", "--backend", "mock",
         "--steps", "3", "--tick-seconds", "0",
         "--overlay-file", str(overlay), "--log-file", str(log)],
        check=True, capture_output=True, text=True)
    text = overlay.read_text()
    assert "Jev plays Factorio - LIVE" in text
    assert "action:" in text and "confidence" in text
    records = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(records) == 3
    for r in records:
        assert {"tick", "goal", "action", "source", "confidence", "outcome",
                "ts"} <= set(r)
