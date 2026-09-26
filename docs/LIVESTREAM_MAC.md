# Local livestream runbook (Mac, Apple Silicon)

The chain, all on her Mac:

```
Colima/Docker ─ FLE headless Factorio server (ports 34197 game / 27000 RCON)
      ▲                     ▲
      │ RCON (agent)        │ Multiplayer connect 127.0.0.1:34197 (spectator)
agent loop (this repo)      Factorio app window ──► OBS (VideoToolbox) ──► YouTube Live
      │                                            ▲
      └─► stream/overlay.txt ──► OBS Text source ──┘
```

## What the repo provides

- `src/jev_factorio/backends/fle.py` - real FLE backend (observe/act over the
  live game via FLE's tool API). Starter inventory: 1 burner drill; peaceful
  map; game speed 1.0 (real-time, watchable).
- `src/jev_factorio/live.py` - the runner: `python -m jev_factorio.live
  --backend fle`. Writes `stream/overlay.txt` (rewritten every decision; hook
  an OBS Text source at it) and appends `stream/decisions.jsonl` (full audit:
  state, answers, confidence, outcome). Reads `TYPESAFE_API_KEY` from the
  environment or a local `.env`; never prints it.
- `scripts/livestream_preflight.sh` - checks macOS, Python 3.10+, Docker/
  Colima, FLE, the Factorio app, OBS, and that the key is set. Exits 1 with a
  MISSING list if anything is absent.
- `scripts/livestream_stop.sh` - stops the agent loop and `caffeinate`.

## Manual-only steps (hers, not the agent's)

1. **YouTube stream key**: paste it herself in OBS - Settings > Stream >
   Service "YouTube - RTMPS" > Stream Key. Never via chat, files, or shell.
2. **OBS scene**: Window Capture of the Factorio app + a Text (FreeType 2)
   source reading `<repo>/stream/overlay.txt`. Encoder: Apple VideoToolbox
   (hardware) H.264. Suggested: 1920x1080, 30 fps, ~4500 kbps.
3. **Spectator view**: open Factorio > Multiplayer > Connect to address >
   `127.0.0.1:34197` once the FLE cluster is up.

## Run order

1. `colima start` (if stopped), `fle cluster start`
2. `bash scripts/livestream_preflight.sh`
3. `caffeinate -dims &` - keeps the Mac awake while streaming
4. `python -m jev_factorio.live --backend fle`
5. Factorio app: join `127.0.0.1:34197` as spectator
6. OBS: Start Streaming; confirm "Live" in YouTube Studio

## Stop

`bash scripts/livestream_stop.sh`, then OBS > Stop Streaming. Fully done:
`fle cluster stop && colima stop`.

## Cost note

At one decision every ~2 s the Jev spend is ~43k calls/day (~$3/day at
gateway pricing). `stream/decisions.jsonl` is the exact record.
