from jev_factorio.backends.mock import MockBackend
from jev_factorio.jev_client import MockJevClient
from jev_factorio.loop import AgentLoop, fallback_policy
from jev_factorio.questions import build_questions
from jev_factorio.state import GameSnapshot


def test_candidates_exclude_impossible_actions():
    s = GameSnapshot(inventory={}, nearby_resources={})
    q = build_questions(s)
    assert set(q["next_action"]["criteria"]) == {"idle"}


def test_mock_loop_runs_end_to_end():
    loop = AgentLoop(MockBackend(), jev=MockJevClient(), tick_seconds=0)
    rec = loop.step()
    assert rec["action"] and rec["outcome"]


def test_fallback_places_drill_plan():
    s = GameSnapshot(inventory={"burner-mining-drill": 1},
                     nearby_resources={"coal": 12.0})
    assert fallback_policy(s) == "walk_to_coal"
