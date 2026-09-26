"""Ask Jev what decision authority models should have in the consensus-clock project.

The project framing and candidate options are ours because Jev has no free-text
answer type. Jev supplies the numerical answers and full distributions. The
constitutional constraint is stated plainly: models may design, but humans have
political equality and decide.
"""
from __future__ import annotations

import argparse
import json

from .jev_client import MockJevClient, make_client

PROJECT_STATE = {
    "question_from_Adi": "what if we entrust this decision to the LLMs and Jev?",
    "project": (
        "Adi, Instinct, and Jev are designing a consensus clock for a film competition. "
        "The current design reads readiness to end only after 75% support is sustained "
        "for 7 days, with one human one vote through privacy-preserving proof of personhood."
    ),
    "constitution": (
        "Adi's organodynamics gives models no political weight: models may design and "
        "advise; humans decide rules and political outcomes."
    ),
    "distinction": (
        "Designing or recommending a rule is different from exercising political power. "
        "A deterministic clock may apply a human-approved rule without making a fresh judgment."
    ),
    "candidate_pool_provenance": (
        "The candidate options and labels are supplied by us. Choose among them and return "
        "your calibrated distribution; the numerical answers are yours."
    ),
}

QUESTIONS = {
    "entrusted_scope": {
        "type": "choice",
        "instructions": "Which decisions may be entrusted to LLMs or Jev in this project?",
        "criteria": {
            "design_only_humans_sign_off": (
                "Models may propose and stress-test the design and parameters, including quorum, "
                "but humans must approve every political rule and outcome."
            ),
            "also_operational_rulings": (
                "After humans set constitutional bounds, models may make operational rulings such "
                "as choosing or adjusting quorum numbers without a separate human vote each time."
            ),
            "also_clock_end_reading": (
                "Models may make the binding judgment that the clock has reached readiness to end, "
                "rather than merely applying a fully human-approved deterministic rule."
            ),
            "also_winner_vote": (
                "Models may also cast or determine the binding winner vote in place of human voters."
            ),
            "none": "Models should have no role, including no design or advisory role.",
        },
    },
    "models_decide_end_reading": {
        "type": "noul",
        "instructions": "Should the clock's end-reading be decided by models?",
        "criteria": {
            "true": "A model makes the binding readiness judgment.",
            "false": "Humans approve the rule and human votes determine the reading; software may apply it mechanically.",
        },
    },
    "models_have_political_weight": {
        "type": "noul",
        "instructions": "Should models have political weight in a system that decides for humans?",
        "criteria": {
            "true": "Models receive binding political power or vote weight.",
            "false": "Models advise or design only; political authority stays with humans.",
        },
    },
    "trust_llm_decided_quorum": {
        "type": "noul",
        "instructions": "Would you trust an LLM-decided quorum for this clock?",
        "criteria": {
            "true": "The LLM may choose the binding quorum without human sign-off.",
            "false": "The LLM may recommend or analyze quorum, but humans approve the binding rule.",
        },
    },
    "refusing_power_is_hypocritical": {
        "type": "noul",
        "instructions": "Is it hypocritical for a model to refuse power over humans?",
        "criteria": {
            "true": "Refusing such power conflicts with the model's role or conduct.",
            "false": "Refusing binding political power is consistent with advising, designing, or applying human-approved rules.",
        },
    },
}


def run_session(jev) -> dict:
    answers = jev.evaluate(PROJECT_STATE, QUESTIONS)
    return {
        "session": "consensus clock v0.2 - model political authority",
        "state": PROJECT_STATE,
        "pool_source": "Candidate options and labels are ours; all numerical answers and distributions are Jev's.",
        "questions": QUESTIONS,
        "answers": answers,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Ask Jev about model authority over the consensus clock")
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
