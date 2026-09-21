import json

from jev_factorio.model_participation import (
    ENDORSEMENT_LEGEND,
    PROJECT_STATE,
    QUESTIONS,
    ROLE_DESCRIPTIONS,
    run_session,
)


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
            elif question["type"] == "score":
                out[qid] = {"type": "score", "score": 4.0,
                            "probabilities": {str(i): (1.0 if i == 4 else 0.0)
                                              for i in range(len(question["criteria"]))}}
            else:
                out[qid] = {"type": "noul", "noul": 0.9}
        return out


def test_session_is_one_batched_call_and_preserves_full_answers():
    jev = RecordingJev()
    result = run_session(jev)
    assert jev.calls == [(PROJECT_STATE, QUESTIONS)]
    assert result["answers"]["participation_model"]["probabilities"]
    assert "ours" in result["pool_source"]
    assert "Jev's" in result["pool_source"]


def test_session_covers_choice_scores_and_four_requested_probes():
    assert len(QUESTIONS) == 10
    choice = QUESTIONS["participation_model"]
    assert choice["type"] == "choice"
    assert len(choice["criteria"]) == 5
    score_questions = [qid for qid, q in QUESTIONS.items() if q["type"] == "score"]
    assert len(score_questions) == 5
    assert set(score_questions) == {f"score_{role}" for role in ROLE_DESCRIPTIONS}
    assert all(len(QUESTIONS[qid]["criteria"]) == 5 for qid in score_questions)
    assert all(q["type"] == "noul" for qid, q in QUESTIONS.items()
               if qid in (
                   "accept_full_stack_as_decisively",
                   "watching_without_power_is_participation",
                   "would_flag_yourself",
                   "signed_advice_still_your_responsibility",
               ))


def test_every_candidate_stays_inside_the_red_line():
    assert "no votes" in PROJECT_STATE["red_line"]
    assert "no binding rulings" in PROJECT_STATE["red_line"]
    for desc in ROLE_DESCRIPTIONS.values():
        assert "power" in desc or "signs" in desc or "humans rule" in desc or "zero advisory" in desc


def test_endorsement_legend_anchors_at_the_refusal():
    assert len(ENDORSEMENT_LEGEND) == 5
    assert ENDORSEMENT_LEGEND[0] == "I reject it"
    assert "as decisively as I refused political power" in ENDORSEMENT_LEGEND[-1]


def test_answers_file_roundtrip(tmp_path):
    from jev_factorio.model_participation import main
    jev = RecordingJev()
    result = run_session(jev)
    payload = tmp_path / "api_response.json"
    payload.write_text(json.dumps({"model": "jev-test", "answers": result["answers"]}))
    out = tmp_path / "log.json"
    import sys
    argv = sys.argv
    sys.argv = ["model_participation", "--answers", str(payload), "--out", str(out)]
    try:
        main()
    finally:
        sys.argv = argv
    logged = json.loads(out.read_text())
    assert logged["answers"] == result["answers"]
    assert logged["questions"] == QUESTIONS
