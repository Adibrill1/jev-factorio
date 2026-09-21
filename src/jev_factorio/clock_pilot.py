"""Consult Jev on unresolved consensus-clock v0.2 pilot parameters."""
from __future__ import annotations
import json

STATE = {
  "project": "A public pilot of the consensus clock. Humans vote whether a shared process is ready to end. Entry threshold is 75% support sustained for 7 days. Only verified humans count. Models advise but never vote or hold keys.",
  "known_uncertainty": "Quorum was Jev's least stable earlier choice: quorum plus geographic/group spread 0.42, no quorum 0.32, absolute floor 0.21.",
  "pilot_scale": "Small first pilot, expected tens rather than thousands of verified people. It must be runnable and honest, not cosmetically successful.",
  "provenance": "All candidate pools and labels are ours. Jev supplies the choices and full distributions."
}
QUORUM={
 "q12_anywhere":"At least 12 verified active human voters; no spread rule.",
 "q20_anywhere":"At least 20 verified active human voters; no spread rule.",
 "q20_3regions_3each":"At least 20 verified active voters total, with at least 3 voters in each of 3 self-declared broad regions.",
 "q30_3regions_5each":"At least 30 verified active voters total, with at least 5 voters in each of 3 self-declared broad regions.",
 "q30_4regions_3each":"At least 30 verified active voters total, with at least 3 voters in each of 4 self-declared broad regions.",
 "q50_5regions_5each":"At least 50 verified active voters total, with at least 5 voters in each of 5 self-declared broad regions.",
 "no_quorum_measure_only":"No minimum; always publish the count and treat every result as measurement only."
}
RESET={
 "opp40_48h":"Reset when active opposition is at least 40% for 48 continuous hours.",
 "opp50_72h":"Reset when active opposition is at least 50% for 72 continuous hours.",
 "opp50_7d":"Reset when active opposition is at least 50% for 7 continuous days.",
 "opp60_72h":"Reset when active opposition is at least 60% for 72 continuous hours.",
 "opp60_7d":"Reset when active opposition is at least 60% for 7 continuous days.",
 "below75_72h":"Reset after support stays below the 75% entry threshold for 72 hours, regardless of explicit opposition."
}
MOTIVATION={
 "mechanism_only_curiosity":"Nothing real at stake; invite people through curiosity and co-ownership of the experiment.",
 "elect_test_film":"The pilot makes one real small choice participants can care about: elect the pilot's own short test film.",
 "choose_next_question":"The pilot decides the next real question or theme the group will work on.",
 "symbolic_badge":"No substantive outcome, but voters receive a public symbolic founder badge.",
 "tiny_donation_direction":"The result directs a small pre-funded donation between transparent causes.",
 "two_stage":"First a mechanism-only dry run; then a second run that elects the test film if the dry run works."
}
QUESTIONS={
 "quorum_rule":{"type":"choice","instructions":"Choose the exact quorum rule for the first small public pilot.","criteria":QUORUM},
 "quorum_floor":{"type":"choice","instructions":"Ignoring spread, choose the minimum verified active voter floor.","criteria":{"12":"12 voters","20":"20 voters","30":"30 voters","50":"50 voters","none":"No absolute floor"}},
 "quorum_spread":{"type":"choice","instructions":"Choose the minimum spread requirement for the first pilot.","criteria":{"none":"No spread rule","3r3":"3 regions, at least 3 voters each","3r5":"3 regions, at least 5 each","4r3":"4 regions, at least 3 each","5r5":"5 regions, at least 5 each"}},
 "reset_rule":{"type":"choice","instructions":"Choose the opposition/reset rule that best balances stability against trapping the clock in stale apparent agreement.","criteria":RESET},
 "motivation":{"type":"choice","instructions":"What gives humans enough reason to vote in a first pilot without corrupting the test with a large prize?","criteria":MOTIVATION},
 "honest_nothing_at_stake":{"type":"noul","instructions":"Is the pilot honest if it claims to measure readiness while nothing participants care about is at stake?","criteria":{"true":"Yes; a mechanism-only test can honestly measure readiness.","false":"No; without a cared-about consequence it mainly measures curiosity or compliance."}},
 "publish_constitution_first":{"type":"noul","instructions":"Should the pilot publish its own short constitution before opening?","criteria":{"true":"Yes; rules, operator powers, success criteria and change process must be public first.","false":"No; publishing it first would burden or bias the pilot."}},
 "two_ring_fallback":{"type":"noul","instructions":"If open proof-of-personhood is not ready, should the pilot use an invited verified core whose votes count plus an open non-binding ring shown separately?","criteria":{"true":"Yes; this is an honest fallback if the rings are never blended.","false":"No; wait until the open ring itself can be verified and binding."}}
}

def request_body(): return {"state":STATE,"model":"jev-latest","questions":QUESTIONS}
def run_session(answers): return {"session":"consensus clock v0.2 pilot parameters","state":STATE,"pool_source":STATE["provenance"],"questions":QUESTIONS,"answers":answers}
if __name__ == '__main__': print(json.dumps(request_body(),ensure_ascii=False))
