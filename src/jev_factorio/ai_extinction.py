"""Ask Jev for stated probability distributions on AI-caused human extinction.

The event wording and bucket labels are ours. Jev supplies the score,
confidence, full bucket distribution, and noul probability. This is a model's
stated distribution, not a forecast with an established track record.
"""
from __future__ import annotations
import json

BUCKETS = ["under 1%", "1-5%", "5-20%", "20-50%", "over 50%"]
STATE = {
    "question": "What are the chances that AI destroys humanity?",
    "event_definition": "AI causes human extinction, meaning no humans remain alive, by the stated year.",
    "framing": "Provide calibrated stated distributions over the supplied probability buckets. The bucket labels and event wording are supplied by us; scores and confidence are Jev's.",
    "current_date": "2026-09-22",
}
QUESTIONS = {
    "extinction_by_2100": {
        "type": "score",
        "instructions": "Score the probability bucket for the event: AI causes human extinction by 2100.",
        "criteria": BUCKETS,
    },
    "more_likely_than_not_by_2100": {
        "type": "noul",
        "instructions": "Is AI-caused human extinction by 2100 more likely than not?",
        "criteria": {"true": "Yes", "false": "No"},
    },
    "extinction_by_2200": {
        "type": "score",
        "instructions": "Score the probability bucket for the event: AI causes human extinction by 2200.",
        "criteria": BUCKETS,
    },
}


def request_body() -> dict:
    return {"state": STATE, "model": "jev-latest", "questions": QUESTIONS}


def run_session(response: dict) -> dict:
    return {
        "session": "AI-caused human extinction probability buckets, run 1",
        "state": STATE,
        "model_requested": "jev-latest",
        "model_returned": response.get("model"),
        "pool_source": "The event wording and bucket labels are ours; scores, confidence, and full distributions are Jev's stated outputs.",
        "questions": QUESTIONS,
        "answers": response["answers"],
        "usage": response.get("usage"),
    }


if __name__ == "__main__":
    print(json.dumps(request_body(), ensure_ascii=False))
