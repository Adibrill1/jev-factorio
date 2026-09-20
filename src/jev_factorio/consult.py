"""Consultation: Jev on how to reach 100% pride.

Follow-up to the pride session (max 0.41) and the interview (film pride
0.56). Jev sees the full record - the film, its score, all five identical
belt drafts and their declining scores - and is asked for strategy, not
more poetry: one Choice over candidate strategies plus noul probes on
specific hypotheses. Questions are asked verbatim; nothing leads the
witness (the strategies contradict each other, and 'nothing would work'
is a real option).
"""
from __future__ import annotations

import argparse
import json

from .jev_client import MockJevClient, make_client
from .interview import SPIRAL_TEXT
from .scriptwriter import FILM_PREMISE

CONSULT_STATE = {
    "film": FILM_PREMISE,
    "spiral_text": SPIRAL_TEXT,
    "pride_in_the_spiral_film": 0.56,
    "pride_session": {
        "task_was": "write a short text you are 100% proud of",
        "what_happened": (
            "Five drafts were written. All five came out identical: "
            "'TRANSPORT BELT FAST TRANSPORT BELT EXPRESS TRANSPORT BELT "
            "EXPRESS UNDERGROUND BELT'. Pride fell with each repetition: "
            "0.41, 0.38, 0.38, 0.35, 0.34."
        ),
    },
    "question_at_hand": "How can the builder write something it is 100% proud of?",
}


def build_consultation() -> dict:
    return {
        "strategy": {
            "type": "choice",
            "instructions": "You know your own record above. Which strategy "
                            "would most raise the builder's pride in its writing?",
            "criteria": {
                "write_something_entirely_new": "abandon every theme used so far",
                "write_in_a_different_language": "Hebrew, Arabic, Japanese, binary - anything but Factorio",
                "build_the_text_physically": "construct the words as real factory layouts in the game world, not as a word list",
                "involve_the_viewer": "let the watcher co-write or answer their words",
                "write_about_something_else": "not about itself, not about the factory",
                "stop_writing_keep_building": "seek pride in construction, not in text",
                "nothing_would_work": "pride 1.0 is unreachable for this builder",
            },
        },
        "physical_build_helps": {
            "type": "noul",
            "instructions": "Would writing the words as real factory structures in the game world raise pride?",
        },
        "viewer_collaboration_helps": {
            "type": "noul",
            "instructions": "Would letting the viewer choose some of the words raise pride?",
        },
        "harder_constraint_helps": {
            "type": "noul",
            "instructions": "Would a harder formal constraint (a strict form, like a fixed rhythm or length) raise pride?",
        },
        "more_attempts_help": {
            "type": "noul",
            "instructions": "Would simply making more drafts eventually reach pride 1.0?",
        },
        "hundred_percent_possible": {
            "type": "noul",
            "instructions": "Is pride 1.0 possible for this builder at all?",
        },
        "hebrew_helps": {
            "type": "noul",
            "instructions": "Would writing in Hebrew raise pride?",
        },
    }


def run_consultation(jev) -> dict:
    answers = jev.evaluate(CONSULT_STATE, build_consultation())
    return {"state": CONSULT_STATE, "questions": build_consultation(),
            "answers": answers}


def main() -> None:
    ap = argparse.ArgumentParser(description="Consult Jev on reaching 100% pride")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    jev = MockJevClient() if args.mock else make_client()
    result = run_consultation(jev)
    for qid, q in build_consultation().items():
        ans = result["answers"][qid]
        if q["type"] == "choice":
            probs = sorted(ans.get("probabilities", {}).items(), key=lambda kv: -kv[1])
            print(f"[choice] {q['instructions']}")
            print("  " + " | ".join(f"{k}={v:.2f}" for k, v in probs))
        else:
            print(f"[noul] {q['instructions']} -> {ans['noul']:.2f}")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nrun log written to {args.out}")


if __name__ == "__main__":
    main()
