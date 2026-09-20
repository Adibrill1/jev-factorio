# Build plan

Ordered milestones. Each ends in something runnable.

## M0 - Offline loop (done in this scaffold)
`--backend mock` runs observe -> Jev(mock) -> gate -> act -> verify with no
key and no game. Unit tests cover the candidate filter and the fallback.
Exit: `python -m jev_factorio --backend mock --steps 8` prints a decision
trace; `pytest` green.

## M1 - Real Jev on the mock world
Get a key: TypeSafe console (waitlist) or Vercel AI Gateway
(`typesafe-ai/jev`). Set `TYPESAFE_API_KEY`. Same loop, real decisions.
Add decision logging to JSONL (state, questions, answers, chosen action).
Exit: mock world bootstraps its drill under real Jev decisions; spend
logged and under a cent.

## M2 - FLE backend online
`pip install factorio-learning-environment==0.4.3`, `fle cluster start`.
Implement `FleBackend.observe/act` against FLE's tool API
(`get_entities`, `inspect_inventory`, `nearest`, `place_entity`, ...).
Exit: one macro action (place burner drill) executed in a real headless
game from a Jev decision.

## M3 - MVP: bootstrap mining end-to-end
Full loop in a real game: walk, mine coal, walk, place drill, fuel drill,
verified WORKING with ore accumulating. Confidence floor tuned from M1
logs; alerts (out-of-fuel, blocked placement) wired into state.
Exit: repeatable run from fresh map to working drill, unattended.

## M4 - Goal tier and plan bookkeeping
Add the goal Choice as a real stack: goal holds until `is_stuck` fires or
the goal's completion predicate passes (checked in code, not by Jev).
Add stone furnace + smelting actions. Exit: agent reaches automated iron
plates.

## M5 - Hardening
429/529 backoff, per-run token budget with hard stop, decision replay
tool (re-run logged states against new question rubrics), fallback
coverage for every action, optional Play-API-mod backend for non-Docker
installs. Exit: 30-minute unattended run, cost report, failure taxonomy.
