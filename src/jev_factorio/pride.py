"""Pride session: Jev writes short texts and rates its pride in each.

Prompted by the interview answer "Is the factory proud of what it built?" -
0.56. The session is sequential drafting: each draft is composed with the
previous drafts AND their pride scores visible in the state, so the model
iterates with full knowledge of its own record. Composition uses the same
free-hand two-stage mechanics as the scriptwriter (language, then word).
Pride is a plain noul probe: "Is the builder proud of this text?".

Honesty: drafts and scores are reported in order, whatever the maximum is.
No rerolls of a disappointing draft; a draft that scores low stays low.
"""
from __future__ import annotations

import argparse
import json

from .jev_client import MockJevClient, make_client
from .scriptwriter import FILM_PREMISE, StepRecord, _choose

WORDS_PER_DRAFT = 4
DRAFT_COUNT = 5

PRIDE_QUESTION = "Is the builder proud of this text?"


def run_pride_session(jev, sources: dict, drafts: int = DRAFT_COUNT,
                      words_per_draft: int = WORDS_PER_DRAFT) -> dict:
    history: list[dict] = []
    steps: list[StepRecord] = []
    for n in range(1, drafts + 1):
        words: list[str] = []
        for _ in range(words_per_draft):
            state = {
                "film": FILM_PREMISE,
                "task": "The builder wants to write a short text it is 100% "
                        "proud of. Compose one, word by word.",
                "draft_number": n,
                "previous_drafts": history,
                "words_so_far": words,
            }
            lang, lang_probs = _choose(
                jev, state=state,
                instructions="Choose which language or notation this word "
                             "will be written in.",
                criteria={k: s["description"] for k, s in sources.items()})
            steps.append(StepRecord(act=f"draft{n}:language",
                                    offered=list(sources),
                                    probabilities=lang_probs, chosen=lang))
            remaining = {w: None for w in sources[lang]["words"] if w not in words}
            word, word_probs = _choose(
                jev, state={**state, "language": lang},
                instructions=f"Choose the next word of draft {n}, written in "
                             f"{lang}.",
                criteria=remaining)
            steps.append(StepRecord(act=f"draft{n}", offered=list(remaining),
                                    probabilities=word_probs, chosen=word))
            words.append(word)
        answers = jev.evaluate(
            {"film": FILM_PREMISE, "previous_drafts": history,
             "text": " ".join(words)},
            {"pride": {"type": "noul", "instructions": PRIDE_QUESTION}})
        pride = float(answers["pride"]["noul"])
        history.append({"draft": n, "text": " ".join(words), "pride": pride})
    best = max(history, key=lambda d: d["pride"])
    return {"pride_question": PRIDE_QUESTION, "drafts": history,
            "best": best, "steps": [s.__dict__ for s in steps]}


def main() -> None:
    ap = argparse.ArgumentParser(description="Jev pride session")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--stage-file", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    sources = json.load(open(args.stage_file))["sources"]
    jev = MockJevClient() if args.mock else make_client()
    result = run_pride_session(jev, sources)
    for d in result["drafts"]:
        print(f"draft {d['draft']}: {d['text']}  (proud: {d['pride']:.2f})")
    print(f"\nbest: draft {result['best']['draft']} at {result['best']['pride']:.2f}")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"run log written to {args.out}")


if __name__ == "__main__":
    main()
