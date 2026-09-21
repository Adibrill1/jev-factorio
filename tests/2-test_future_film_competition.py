from jev_factorio.future_film_competition import PROJECT, QUESTIONS, run_session


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
    assert state["project"] == PROJECT
    assert questions == QUESTIONS
    assert len(questions) == 8
    assert [q["type"] for q in questions.values()].count("choice") == 7
    assert [q["type"] for q in questions.values()].count("noul") == 1
    assert result["answers"]["winner_selection"]["probabilities"]
    assert "ours" in result["pool_source"]
    assert "Jev's" in result["pool_source"]


def test_choice_pools_fit_api_cap_and_builder_probe_is_verbatim():
    for q in QUESTIONS.values():
        if q["type"] == "choice":
            assert 2 <= len(q["criteria"]) <= 255
    assert QUESTIONS["builder_willingness"]["instructions"] == "Do you want to be one of its builders?"
