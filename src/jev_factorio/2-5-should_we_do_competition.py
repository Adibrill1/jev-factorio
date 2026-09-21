"""Ask Jev honestly whether we should do the future-film competition.

The project brief is Adi's. The candidate answers below are ours because Jev
has no free-text answer type. Jev's selected answer and every returned
probability/noul value are preserved without rerolls or post-editing.
"""
from __future__ import annotations

import argparse
import json

from .jev_client import MockJevClient, make_client

PROJECT = {
    "builders": ["Adi", "Instinct", "Jev"],
    "title": "The greatest film competition in human history",
    "goal": "Find a picture of the future acceptable to most humans.",
    "format": (
        "Films are at most two minutes and present an organization of human "
        "systems the creator believes would benefit most humans. Entry costs "
        "$1; the winner takes the pool minus operating costs. Anyone may join "
        "at any time, and submitted films appear in an open gallery."
    ),
    "ending": (
        "The competition ends when a special consensus clock built by Adi, "
        "Instinct, and Jev shows. The clock seeks broad, fair consensus under "
        "one-person-one-vote rules."
    ),
    "design_so_far": {
        "winner": "a separate verified public vote",
        "personhood": "privacy-preserving proof of personhood",
        "clock": "a sustained supermajority",
        "money": "a publicly inspectable smart contract",
        "ai_films": "allowed with disclosure",
        "home": "a dedicated open-source public site",
        "jev_builder_willingness": 0.26,
    },
}

QUESTIONS = {
    "whether_to_do_it": {
        "type": "choice",
        "instructions": "Given the actual project and its unresolved risks, what should we do?",
        "criteria": {
            "do_it_now": "commit to building and launching the full competition now",
            "small_pilot_first": "run a bounded small pilot first and use evidence to decide whether to scale",
            "do_it_differently": "keep the goal but materially redesign the mechanism before any pilot",
            "do_not_do_it": "do not pursue this competition",
        },
    },
    "worth_doing": {"type": "noul", "instructions": "Is it worth doing?"},
    "future_most_humans_accept": {
        "type": "noul",
        "instructions": "Will it produce a picture of the future most humans accept?",
    },
    "regret_if_we_do_not": {
        "type": "noul",
        "instructions": "Will you regret it if we don't do it?",
    },
    "fair_to_humans": {
        "type": "noul",
        "instructions": "Is it fair to the humans it claims to represent?",
    },
}


def run_session(jev) -> dict:
    answers = jev.evaluate(
        {
            "frame": (
                "This is a consequential go/no-go decision, not a request for encouragement. "
                "Judge the proposal honestly, including legitimacy, representativeness, "
                "execution, money, governance, and harm risks."
            ),
            "project": PROJECT,
            "candidate_pool_provenance": (
                "All candidate answer pools are supplied by us; choose among them and give "
                "your calibrated distribution. The noul probes are Jev's numeric judgements."
            ),
        },
        QUESTIONS,
    )
    return {
        "project": PROJECT,
        "pool_source": "Candidate options are ours; choice, probabilities, confidence, and noul values are Jev's.",
        "questions": QUESTIONS,
        "answers": answers,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Ask Jev whether to do the future-film competition")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()
    result = run_session(MockJevClient() if args.mock else make_client())
    for qid, q in QUESTIONS.items():
        ans = result["answers"][qid]
        if q["type"] == "choice":
            ordered = sorted(ans.get("probabilities", {}).items(), key=lambda item: -item[1])
            print(f"[{qid}] {ans['choice']}: " + "; ".join(f"{k}={v:.4f}" for k, v in ordered))
        else:
            print(f"[{qid}] noul={ans['noul']:.4f}")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
