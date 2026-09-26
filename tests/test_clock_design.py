from jev_factorio.clock_design import DECISIONS_SO_FAR, QUESTIONS, run_session


class RecordingJev:
    def __init__(self):
        self.calls = []

    def evaluate(self, state, questions):
        self.calls.append((state, questions))
        out = {}
        for qid, q in questions.items():
            if q["type"] == "choice":
                pick = next(iter(q["criteria"]))
                n = len(q["criteria"])
                out[qid] = {"type": "choice", "choice": pick,
                            "probabilities": {k: 1 / n for k in q["criteria"]}}
            else:
                out[qid] = {"type": "noul", "noul": 0.7}
        return out


def test_session_is_one_batched_call_and_preserves_full_answers():
    jev = RecordingJev()
    result = run_session(jev)
    assert len(jev.calls) == 1
    state, questions = jev.calls[0]
    assert state["decisions_so_far"] == DECISIONS_SO_FAR
    assert questions == QUESTIONS
    assert len(questions) == 8
    assert [q["type"] for q in questions.values()].count("choice") == 7
    assert [q["type"] for q in questions.values()].count("noul") == 1
    assert result["answers"]["threshold_percent"]["probabilities"]
    assert "ours" in result["pool_source"]
    assert "Jev's" in result["pool_source"]


def test_choice_pools_fit_api_cap_and_cover_the_six_open_parameters():
    for q in QUESTIONS.values():
        if q["type"] == "choice":
            assert 2 <= len(q["criteria"]) <= 255
    for qid in ("threshold_percent", "sustain_duration", "pilot_measures",
                "pilot_electorate", "sustain_break_rule", "minimum_participation"):
        assert qid in QUESTIONS
    assert QUESTIONS["live_reading_public"]["type"] == "noul"
