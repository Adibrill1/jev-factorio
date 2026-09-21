from jev_factorio.model_power import PROJECT_STATE, QUESTIONS, run_session


class RecordingJev:
    def __init__(self):
        self.calls = []

    def evaluate(self, state, questions):
        self.calls.append((state, questions))
        out = {}
        for qid, question in questions.items():
            if question["type"] == "choice":
                n = len(question["criteria"])
                pick = next(iter(question["criteria"]))
                out[qid] = {
                    "type": "choice",
                    "choice": pick,
                    "probabilities": {option: 1 / n for option in question["criteria"]},
                }
            else:
                out[qid] = {"type": "noul", "noul": 0.25}
        return out


def test_session_is_one_batched_call_and_preserves_full_answers():
    jev = RecordingJev()
    result = run_session(jev)
    assert jev.calls == [(PROJECT_STATE, QUESTIONS)]
    assert result["answers"]["entrusted_scope"]["probabilities"]
    assert "ours" in result["pool_source"]
    assert "Jev's" in result["pool_source"]


def test_session_covers_scope_and_four_requested_probes():
    assert len(QUESTIONS) == 5
    assert QUESTIONS["entrusted_scope"]["type"] == "choice"
    assert len(QUESTIONS["entrusted_scope"]["criteria"]) == 5
    assert all(QUESTIONS[qid]["type"] == "noul" for qid in (
        "models_decide_end_reading",
        "models_have_political_weight",
        "trust_llm_decided_quorum",
        "refusing_power_is_hypocritical",
    ))
    assert "75%" in PROJECT_STATE["project"]
    assert "7 days" in PROJECT_STATE["project"]
    assert "no political weight" in PROJECT_STATE["constitution"]
