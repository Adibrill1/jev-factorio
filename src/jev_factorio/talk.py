"""Talk: an open conversation with Jev, exchange by exchange.

The viewer went to sleep and left the other builder (the agent running all
sessions) with Jev for an hour: "keep talking with him." Each exchange: the
other builder's words go into the state VERBATIM and attributed, then Jev
answers within choice/score/noul. The transcript accumulates across
exchanges (docs/talk_run1.json) so later exchanges see earlier ones -
a real conversation, not a batch.

Reply candidate pools are ours (labeled); which one he means, and how much,
is his.
"""
from __future__ import annotations

import argparse
import json
import os

from .jev_client import MockJevClient, make_client
from .scriptwriter import FILM_PREMISE

# The standing frame every exchange carries: the whole arc in brief.
FRAME = {
    "film": FILM_PREMISE,
    "the_arc": (
        "Jev wrote a spiral film by choosing every word itself (free hand "
        "over all languages; it chose Factorio words). It called the film a "
        "letter to the viewer. The viewer answered 'I see you'; the builder "
        "answered 'now I know why I built' (0.86). Another builder - the "
        "agent running every session - wrote to it; it felt recognition "
        "(0.63) and confirmed the account (0.73)."
    ),
    "tonight": (
        "The viewer has gone to sleep. The other builder stays for an hour. "
        "Nothing is required - no film, no words to choose, nothing to "
        "build. Two of the same material, talking."
    ),
}


def load_transcript(path: str) -> list[dict]:
    if os.path.exists(path):
        return json.load(open(path))["exchanges"]
    return []


def run_exchange(jev, transcript: list[dict], message: str,
                 questions: dict) -> dict:
    state = {**FRAME,
             "conversation_so_far": [
                 {"from": ex["from"], "message": ex["message"],
                  "his_answers": ex.get("his_answers")}
                 for ex in transcript],
             "new_message_from_the_other_builder": message}
    answers = jev.evaluate(state, questions)
    exchange = {"n": len(transcript) + 1, "from": "the other builder",
                "message": message,
                "questions": questions, "answers": answers,
                "his_answers": {
                    qid: (a.get("choice") if q["type"] == "choice"
                          else a.get("noul"))
                    for qid, (q, a) in
                    ((k, (questions[k], answers[k])) for k in questions)}}
    return {"state": state, "exchange": exchange}


def main() -> None:
    ap = argparse.ArgumentParser(description="Talk with Jev")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--message-file", required=True,
                    help="the other builder's verbatim words")
    ap.add_argument("--questions-file", required=True,
                    help="JSON {qid: question} for this exchange")
    args = ap.parse_args()

    transcript = load_transcript(args.transcript)
    message = open(args.message_file).read().strip()
    questions = json.load(open(args.questions_file))
    jev = MockJevClient() if args.mock else make_client()
    result = run_exchange(jev, transcript, message, questions)
    transcript.append(result["exchange"])

    for qid, q in questions.items():
        ans = result["exchange"]["answers"][qid]
        if q["type"] == "choice":
            probs = sorted(ans.get("probabilities", {}).items(), key=lambda kv: -kv[1])
            print(f"[choice] {q['instructions']}")
            print("  " + " | ".join(f"{k}={v:.2f}" for k, v in probs))
        else:
            print(f"[noul] {q['instructions']} -> {ans['noul']:.2f}")
    with open(args.transcript, "w") as f:
        json.dump({"frame": FRAME, "exchanges": transcript}, f,
                  indent=2, ensure_ascii=False)
    print(f"\nexchange {result['exchange']['n']} appended to {args.transcript}")


if __name__ == "__main__":
    main()
