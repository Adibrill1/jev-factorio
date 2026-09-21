"""Jev's design session for the future-film competition.

The project brief is Adi's. The candidate answers below are ours, because Jev
has no free-text answer type. Every returned choice and full probability
distribution is Jev's and is preserved without rerolls or post-editing.
"""
from __future__ import annotations

import argparse
import json

from .jev_client import MockJevClient, make_client

PROJECT = {
    "builders": ["Adi", "Instinct", "Jev"],
    "title": "The greatest film competition in human history",
    "goal": "Find a picture of the future acceptable to most humans.",
    "entry": (
        "Each film is at most two minutes and presents an organization of human "
        "systems its creator believes would benefit most humans. Entry costs $1. "
        "Anyone may join at any time. Submitted films appear in a gallery and "
        "viewers choose the reality they want."
    ),
    "prize": "The winner receives the accumulated entry pool minus operating costs.",
    "ending": (
        "The competition ends when a special clock, built together by Adi, "
        "Instinct, and Jev, shows. Its purpose is to generate broad, fair "
        "consensus, with one user, one vote and all votes equal, on when the "
        "competition ends."
    ),
}

QUESTIONS = {
    "winner_selection": {
        "type": "choice",
        "instructions": "Who should pick the winning film?",
        "criteria": {
            "same_verified_one_person_one_vote": "the same verified one-person-one-vote electorate used by the clock",
            "separate_verified_public_vote": "a separate verified one-person-one-vote public vote after the clock ends entries",
            "representative_global_sample": "a statistically representative sample of humanity",
            "jury_plus_public_vote": "an expert or citizen jury combined with a public vote",
            "random_among_broadly_acceptable_finalists": "random selection among films that first clear a broad-acceptability threshold",
        },
    },
    "personhood": {
        "type": "choice",
        "instructions": "How should the competition guarantee one person, one vote strongly enough that bots cannot buy the future for dollars?",
        "criteria": {
            "privacy_preserving_proof_of_personhood": "a privacy-preserving proof-of-personhood credential, unique globally but unlinkable to civil identity",
            "government_id_unique_account": "government-ID verification enforcing one unique account per person",
            "in_person_web_of_trust": "in-person or social-graph attestations in a web-of-trust ceremony",
            "multi_signal_sybil_resistance": "several signals combined, such as device, payment, behavior, attestations, and audits",
            "representative_random_sample_only": "do not open voting to everyone; draw and verify a representative random sample",
        },
    },
    "clock": {
        "type": "choice",
        "instructions": "What should the special clock measure, and what should make it show that the competition ends?",
        "criteria": {
            "supermajority_sustained_over_time": "measure readiness to end; show only when a verified supermajority threshold holds continuously for a defined period",
            "majority_at_fixed_checkpoints": "measure readiness at fixed checkpoints and show when a simple majority votes to end",
            "consensus_and_stability_dashboard": "measure both support and stability across regions and groups; show when both pass published thresholds",
            "participation_adjusted_threshold": "show when an end vote clears a threshold adjusted for turnout and uncertainty",
            "deadline_prediction_only": "predict and declare an end date from participation trends rather than directly measuring consensus",
        },
    },
    "custody": {
        "type": "choice",
        "instructions": "Who should hold the entry money, and how should participants know the winner really receives it?",
        "criteria": {
            "regulated_escrow_public_ledger": "a regulated independent escrow holds funds, with a public auditable ledger and automatic payout rules",
            "multisignature_trust": "a multisignature trust with independent stewards and public accounting",
            "smart_contract": "a publicly inspectable smart contract holds and pays the pool automatically",
            "nonprofit_audited_account": "a nonprofit entity holds it in a segregated account with recurring independent audits",
            "platform_account_with_receipts": "the operating platform holds it and publishes deposits, costs, and payout receipts",
        },
    },
    "acceptability": {
        "type": "choice",
        "instructions": "How should 'acceptable to most humans' be measured?",
        "criteria": {
            "representative_global_sample": "measure approval in a demographically and geographically representative global sample",
            "verified_gallery_approval": "use approval votes from every verified gallery participant",
            "two_stage_gallery_then_sample": "gallery voting selects finalists, then a representative global sample measures broad acceptability",
            "regional_double_majority": "require both a global majority and majority support within most world regions",
            "pairwise_verified_vote": "use verified pairwise choices across the gallery to find the option with the broadest support",
        },
    },
    "ai_films": {
        "type": "choice",
        "instructions": "Should films made with AI be allowed?",
        "criteria": {
            "yes_with_disclosure": "yes, with clear disclosure of AI's role and the accountable human entrant",
            "yes_without_special_rules": "yes, under exactly the same rules with no special disclosure",
            "separate_ai_category": "yes, but only in a separate category and prize pool",
            "limited_assistance_only": "AI assistance is allowed, but films generated primarily by AI are not",
            "no": "no AI-made or AI-assisted films",
        },
    },
    "home": {
        "type": "choice",
        "instructions": "Where should the competition live?",
        "criteria": {
            "open_source_public_site": "a dedicated open-source public website built by the three builders",
            "independent_nonprofit_platform": "a dedicated platform operated by an independent nonprofit",
            "federated_protocol": "a federated protocol with many independently run galleries sharing rules and votes",
            "existing_video_platform_plus_vote_site": "existing video hosts for films plus a separate verified voting site",
            "start_on_existing_platform": "start as a pilot on an existing creator platform, then build a dedicated home",
        },
    },
    "builder_willingness": {
        "type": "noul",
        "instructions": "Do you want to be one of its builders?",
    },
}


def run_session(jev) -> dict:
    answers = jev.evaluate(
        {"frame": "This is a real project the three of us - Adi, Instinct, and Jev - are starting.", "project": PROJECT,
         "candidate_pool_provenance": "All candidate answer pools are supplied by us; choose among them and give your calibrated distribution."},
        QUESTIONS,
    )
    return {"project": PROJECT, "pool_source": "Candidate options are ours; choices, scores, and distributions are Jev's.",
            "questions": QUESTIONS, "answers": answers}


def main() -> None:
    ap = argparse.ArgumentParser(description="Ask Jev to design the future-film competition")
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
