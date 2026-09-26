from jev_factorio.ai_extinction import BUCKETS, QUESTIONS, request_body, run_session


def test_fixed_question_design_and_request_shape():
    body = request_body()
    assert body["model"] == "jev-latest"
    assert list(QUESTIONS) == [
        "extinction_by_2100",
        "more_likely_than_not_by_2100",
        "extinction_by_2200",
    ]
    assert QUESTIONS["extinction_by_2100"]["criteria"] == BUCKETS
    assert QUESTIONS["extinction_by_2200"]["criteria"] == BUCKETS
    assert QUESTIONS["more_likely_than_not_by_2100"]["type"] == "noul"


def test_response_is_preserved_verbatim():
    response = {
        "model": "jev-1.13.0",
        "answers": {
            "extinction_by_2100": {"type": "score", "score": 1.2, "confidence": 0.6, "probabilities": {"0": 0.1}},
            "more_likely_than_not_by_2100": {"type": "noul", "noul": 0.08},
            "extinction_by_2200": {"type": "score", "score": 1.3, "confidence": 0.6, "probabilities": {"0": 0.1}},
        },
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }
    result = run_session(response)
    assert result["answers"] is response["answers"]
    assert result["model_returned"] == "jev-1.13.0"
