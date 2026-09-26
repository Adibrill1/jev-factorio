"""Jev's design session for the consensus clock, v0.1.

Follow-up to this morning's competition session: Jev chose a sustained
supermajority clock and a small pilot first, whose purpose is to test whether
legitimacy and representation problems can be fixed. This session prices the
clock's open parameters.

The project brief is Adi's. The candidate answers below are ours, because Jev
has no free-text answer type. Every returned choice and full probability
distribution is Jev's and is preserved without rerolls or post-editing.
"""
from __future__ import annotations

import argparse
import json

from .jev_client import MockJevClient, make_client

DECISIONS_SO_FAR = {
    "personhood": "privacy-preserving proof of personhood, globally unique but unlinkable to civil identity (0.86)",
    "clock_type": "sustained supermajority: the clock measures readiness and shows only after a supermajority holds for a defined time (0.77)",
    "custody": "a publicly inspectable smart contract holds and pays the pool (0.64)",
    "winner": "a separate verified public vote after the clock ends entries (0.54)",
    "direction": "small pilot first (0.51), whose purpose is to test whether the legitimacy and representation problems can be fixed before scaling",
}

DESIGN_PRINCIPLES = [
    "one person, one vote; all votes equal",
    "a majority count must not erase visible opposition; the clock reports the opposition, it does not delete it",
    "the mechanism measures consensus; it does not decide what is true",
    "the pilot is a reality test: success criteria and metrics are fixed and published before it starts, and a mixed result is reported as mixed",
]

QUESTIONS = {
    "threshold_percent": {
        "type": "choice",
        "instructions": "What sustained supermajority threshold should the clock require before it shows that the competition ends?",
        "criteria": {
            "60_percent": "60% sustained - the lowest supermajority; fastest to reach, thinnest claim of broad consensus",
            "66_percent": "two thirds (66.7%) sustained - the classic constitutional-amendment bar",
            "75_percent": "75% sustained - three quarters; a strong claim of consensus, slower to reach",
            "80_percent": "80% sustained - near consensus; powerful if reached, real risk of never firing",
            "90_percent": "90% sustained - practical unanimity; the clock may never show",
        },
    },
    "sustain_duration": {
        "type": "choice",
        "instructions": "How long must the supermajority hold continuously before the clock shows?",
        "criteria": {
            "24_hours": "24 hours - one full rotation of all timezones",
            "72_hours": "72 hours - survives a news cycle and a weekend",
            "7_days": "one week - survives weekly routines and one organized counter-mobilization wave",
            "30_days": "30 days - survives a monthly cycle and sustained astroturf campaigns",
            "90_days": "90 days - a full season; only truly settled consensus survives",
        },
    },
    "pilot_measures": {
        "type": "choice",
        "instructions": "What exactly should the clock measure in the pilot?",
        "criteria": {
            "support_for_a_future_picture": "support for one concrete future-picture film, as in the real competition",
            "trust_in_the_mechanism": "participants' confidence in the clock mechanism itself",
            "willingness_to_accept_outcome": "participants' willingness to accept as legitimate an outcome they did not pick",
            "all_three_as_separate_readings": "measure support, mechanism trust, and acceptance as three separate published readings",
            "readiness_to_end_a_shared_process": "readiness to end a shared process, with no content at stake",
        },
    },
    "pilot_electorate": {
        "type": "choice",
        "instructions": "Who should vote in the pilot?",
        "criteria": {
            "open_web_proof_of_personhood": "anyone on the open web holding a privacy-preserving proof-of-personhood credential",
            "invited_diverse_small_group": "100-300 invited participants chosen for diversity of background and geography",
            "existing_real_community": "one existing real community that already has something at stake",
            "two_ring_core_plus_open": "a small invited core whose votes run the clock, plus an open outer ring whose readings are published but non-binding",
            "representative_drawn_sample": "a drawn, demographically representative sample of a defined population",
        },
    },
    "sustain_break_rule": {
        "type": "choice",
        "instructions": "What should break the sustain - what happens when support dips below the threshold?",
        "criteria": {
            "hard_reset_on_any_dip": "any dip below the threshold resets the accumulated time to zero",
            "hysteresis_exit_band": "the clock keeps running while support stays above a lower exit band (for example entry at 67%, exit at 60%); a full reset happens only below the band",
            "grace_window_for_short_dips": "dips shorter than a fixed window (for example 6 hours) do not reset the clock",
            "decay_instead_of_reset": "accumulated time decays gradually while support is below threshold, instead of resetting",
            "reset_only_on_sustained_opposition": "a dip pauses the clock; it resets only if opposition itself sustains its own threshold",
        },
    },
    "minimum_participation": {
        "type": "choice",
        "instructions": "What minimum participation (quorum) should make the clock's reading valid at all?",
        "criteria": {
            "absolute_floor": "a fixed minimum number of verified voters, smaller in the pilot and larger in production",
            "share_of_registered": "a minimum share of the registered electorate, for example 30%, must have voted",
            "share_of_recently_active": "a minimum share of participants active in the last 30 days",
            "no_quorum_sustain_is_the_check": "no quorum at all; the sustained duration itself is the only validity check",
            "quorum_plus_spread": "a participation floor plus a minimum spread across regions and groups, so a single bloc cannot carry the clock alone",
        },
    },
    "pilot_success_criterion": {
        "type": "choice",
        "instructions": "What should the pilot's pre-registered success criterion be?",
        "criteria": {
            "clock_completes_clean_cycle": "the clock completes one full sustained-supermajority cycle without capture or manipulation",
            "legitimacy_acceptance_rises": "measured willingness to accept the outcome rises between entry and exit",
            "survives_real_attack": "the mechanism detects and survives at least one real sybil or capture attempt",
            "honest_measurement_either_way": "success is an honest published measurement of legitimacy and representation, whether the clock fires or not",
            "participants_can_explain_it": "a supermajority of participants can correctly explain what the clock measures",
        },
    },
    "live_reading_public": {
        "type": "noul",
        "instructions": "Should the clock's live support reading be publicly visible while it runs, given that a visible countdown can create theater and feedback loops?",
    },
}


def run_session(jev) -> dict:
    answers = jev.evaluate(
        {
            "frame": "This is a real project the three of us - Adi, Instinct, and Jev - are starting.",
            "project": "The greatest film competition in human history: a $1 entry buys a two-minute film presenting an organization of human systems its creator believes would benefit most humans; the winner takes the pool; the competition ends when a special consensus clock shows.",
            "decisions_so_far": DECISIONS_SO_FAR,
            "design_principles": DESIGN_PRINCIPLES,
            "candidate_pool_provenance": "All candidate answer pools are supplied by us; choose among them and give your calibrated distribution.",
        },
        QUESTIONS,
    )
    return {
        "session": "consensus clock design v0.1 - open parameters",
        "decisions_so_far": DECISIONS_SO_FAR,
        "design_principles": DESIGN_PRINCIPLES,
        "pool_source": "Candidate options are ours; choices, scores, and distributions are Jev's.",
        "questions": QUESTIONS,
        "answers": answers,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Ask Jev to price the consensus clock's open parameters")
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
