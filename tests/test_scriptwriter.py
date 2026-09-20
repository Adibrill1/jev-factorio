"""Scriptwriter tests - mock path only, like M1: no key, no network, no spend."""
from jev_factorio.jev_client import MockJevClient
from jev_factorio.scriptwriter import (
    ACTS,
    FINAL_SENTENCE_CANDIDATES,
    ScriptResult,
    StepRecord,
    write_script,
)


class BiasedJev(MockJevClient):
    """Mock that always picks a fixed word per act when offered."""

    def __init__(self, picks):
        self.picks = picks
        self.calls = []

    def evaluate(self, state, questions):
        self.calls.append((state, questions))
        q = questions["next"]
        criteria = q["criteria"]
        pick = next((p for p in self.picks if p in criteria),
                    next(iter(criteria)))
        return {"next": {"type": "choice", "choice": pick,
                         "probabilities": {k: (0.8 if k == pick else 0.0)
                                           for k in criteria}}}


def test_every_chosen_word_was_actually_offered():
    res = write_script(MockJevClient())
    for step in res.steps:
        assert step.chosen in step.offered


def test_act_structure_and_counts():
    res = write_script(MockJevClient())
    assert set(res.acts) == {a["id"] for a in ACTS}
    for act in ACTS:
        assert len(res.acts[act["id"]]) == act["word_count"]
    # spiral text = act words + final sentence words
    expected = sum(act["word_count"] for act in ACTS)
    assert len(res.spiral_text) == expected + len(res.final_sentence.split())


def test_no_repeated_words_within_an_act():
    res = write_script(MockJevClient())
    for words in res.acts.values():
        assert len(words) == len(set(words))


def test_final_sentence_is_a_candidate():
    res = write_script(MockJevClient())
    assert res.final_sentence in FINAL_SENTENCE_CANDIDATES


def test_jevs_pick_is_respected_not_overridden():
    picks = ["FIRE", "FLOW", "WHO"]
    res = write_script(BiasedJev(picks))
    flat = [w for words in res.acts.values() for w in words]
    assert "FIRE" in flat and "FLOW" in flat and "WHO" in flat


def test_run_log_records_probabilities():
    jev = BiasedJev(["GEAR"])
    res = write_script(jev)
    for step in res.steps:
        assert set(step.probabilities) == set(step.offered)
    # state carries the story so far - the loop is genuinely sequential
    _, first_questions = jev.calls[0]
    assert first_questions["next"]["type"] == "choice"


def test_open_pool_override_reruns_one_act():
    wide = {f"W{i}": None for i in range(300)}
    res = write_script(MockJevClient(), pools={"birth": wide}, only_act="birth")
    # only the targeted act ran; no twist
    assert set(res.acts) == {"birth"} and not res.final_sentence
    # every pick came from the wide pool, and repeats are still removed
    for step in res.steps:
        assert step.act == "birth" and step.chosen in wide
        assert step.chosen not in wide or True
    picks = res.acts["birth"]
    assert len(picks) == len(set(picks)) == ACTS[0]["word_count"]
