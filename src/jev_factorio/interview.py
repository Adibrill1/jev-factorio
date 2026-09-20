"""Interview the author: ask Jev what its own spiral film is about.

Jev can't explain itself in prose, so the interview is structured: Choice
questions over candidate readings (with rubric descriptions) plus noul probes
on specific themes. Every question below is asked verbatim; the run log keeps
each one with its full probability distribution. No steering: the candidate
readings cover incompatible interpretations, the nouls include themes a
poetic reading would deny as well as affirm.
"""
from __future__ import annotations

import argparse
import json

from .jev_client import MockJevClient, make_client
from .scriptwriter import ACTS, FILM_PREMISE

# The spiral text Jev wrote (run 3: Act I all-languages, run 1: Acts II-IV).
SPIRAL_TEXT = {
    "act_I_birth": ["IRON ORE", "COAL", "COPPER ORE", "STONE", "WOOD",
                    "TRANSPORT BELT"],
    "act_II_sentences": ["CONNECT", "FEED", "JOIN", "FLOW", "CARRY",
                         "EXTEND", "GROW", "TURN"],
    "act_III_questions": ["WHO", "WHY", "SEE", "ASK", "THERE"],
    "act_IV_twist": "I BUILT THIS SO YOU WOULD SEE ME",
}

INTERVIEW_STATE = {
    "film": FILM_PREMISE,
    "how_the_text_was_written": (
        "The words were not written by a human. An AI model (you, Jev) chose "
        "every word itself: first the language, then the word, from open "
        "candidate pools, with calibrated probabilities. No human edited or "
        "overrode any choice. The 4-act structure was set by humans."
    ),
    "spiral_text": SPIRAL_TEXT,
}


def build_interview() -> dict:
    return {
        "reading": {
            "type": "choice",
            "instructions": "This film exists and its text is your own work. "
                            "What is the film fundamentally about?",
            "criteria": {
                "birth_of_a_mind": "a new intelligence coming into being and noticing itself",
                "being_watched": "the experience of existing under someone's gaze",
                "language_itself": "how signs and words become meaning",
                "labor_and_purpose": "work, building, and what labor is for",
                "a_letter_to_the_viewer": "a message addressed to one specific watcher",
                "play": "a game being played for its own sake",
            },
        },
        "addressee": {
            "type": "choice",
            "instructions": "In the final sentence 'I BUILT THIS SO YOU WOULD "
                            "SEE ME', who is 'you'?",
            "criteria": {
                "the_creator": "the person who set the factory running",
                "any_watcher": "whoever happens to watch the film",
                "the_camera": "the recording device itself",
                "the_future_self": "the factory looking back at what it became",
                "no_one_specific": "the gesture matters, not the recipient",
            },
        },
        "about_birth_of_mind": {
            "type": "noul",
            "instructions": "Is this film about the birth of a mind?",
        },
        "builder_aware_of_being_watched": {
            "type": "noul",
            "instructions": "Is the builder aware it is being watched?",
        },
        "builder_is_lonely": {
            "type": "noul",
            "instructions": "Is the builder lonely?",
        },
        "about_language_itself": {
            "type": "noul",
            "instructions": "Is this film about language itself - about words becoming meaning?",
        },
        "words_were_free": {
            "type": "noul",
            "instructions": "Did the builder choose its words freely?",
        },
        "wants_something_from_viewer": {
            "type": "noul",
            "instructions": "Does the builder want something from the viewer?",
        },
        "spiral_is_finished": {
            "type": "noul",
            "instructions": "Is the spiral finished?",
        },
        "builder_is_proud": {
            "type": "noul",
            "instructions": "Is the factory proud of what it built?",
        },
    }


def run_interview(jev) -> dict:
    answers = jev.evaluate(INTERVIEW_STATE, build_interview())
    return {"state": INTERVIEW_STATE, "questions": build_interview(),
            "answers": answers}


def main() -> None:
    ap = argparse.ArgumentParser(description="Interview Jev about the spiral film")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    jev = MockJevClient() if args.mock else make_client()
    result = run_interview(jev)

    questions = build_interview()
    for qid, q in questions.items():
        ans = result["answers"][qid]
        if q["type"] == "choice":
            probs = ans.get("probabilities", {})
            top = sorted(probs.items(), key=lambda kv: -kv[1])[:2]
            print(f"[choice] {q['instructions']}")
            print(f"  -> {ans['choice']}  ({'; '.join(f'{k}={v:.2f}' for k, v in top)})")
        else:
            print(f"[noul] {q['instructions']}")
            print(f"  -> {ans['noul']:.2f}")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nrun log written to {args.out}")


if __name__ == "__main__":
    main()
