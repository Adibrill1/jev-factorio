"""Jev scriptwriter: Jev picks the words of the spiral film, one choice at a time.

Jev is not a prose chatbot - it evaluates a state and answers typed questions.
So the film's text is written as a LOOP OF CHOICES: at every step we offer a
candidate vocabulary and Jev answers one `choice` question - "which word comes
next?" - returning a calibrated probability per candidate. We take Jev's pick
(answer["choice"] is the model's highest-probability option) and append it.

Honesty contract (Adi cares what the model actually did):
  - every chosen word is Jev's own pick from the offered set;
  - the OFFERED SETS are curated per act so the story stays coherent;
  - already-used words are removed from later offers in the same act;
  - the run log records, per step: offered candidates, Jev's full probability
    distribution, and the chosen word - nothing is post-edited.

Film skeleton (accepted 4-act concept):
  I   birth        - single factory words appear (the film opened on IRON)
  II  sentences    - words start chaining into sentence-like structures
  III questions    - the factory notices the watcher; questions form
  IV  the twist    - the whole spiral reads as one sky-readable sentence
                     written for the viewer; Jev picks that sentence.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field

from .jev_client import MockJevClient, make_client

FILM_PREMISE = (
    "A top-down Factorio-like world where a factory slowly grows into a "
    "spiral of glowing words. An unseen builder writes with belts, furnaces "
    "and machines the way a poet writes with letters. The film is silent; "
    "the words carry everything."
)

# Curated candidate pools: act -> {word: rubric description for Jev}.
# This is the vocabulary curation layer; every word Jev can pick is here.
ACTS = [
    {
        "id": "birth",
        "title": "Act I - birth",
        "brief": "The very first words of the factory: raw materials, "
                 "machine parts, first signs of life. Concrete nouns only.",
        "word_count": 6,
        "pool": {
            "IRON": "the first glyph-factory; the film opened on this word",
            "BELT": "moving line that carries items - and later letters",
            "FIRE": "furnace light, energy, the factory waking up",
            "COAL": "black fuel, the first thing the drills bite",
            "COPPER": "the second metal, wiring and circuits",
            "SMOKE": "sign that something is alive and working",
            "GEAR": "small machined part, industry made visible",
            "DRILL": "the machine that touches the ground first",
            "SPARK": "tiny flash of beginning",
            "STONE": "dumb raw matter waiting to become something",
            "LIGHT": "glow against the dark map",
            "HUM": "the sound a working factory makes, written as a word",
        },
    },
    {
        "id": "sentences",
        "title": "Act II - sentences",
        "brief": "Words stop being isolated and start chaining: actions and "
                 "relations that let the spiral form sentence-like runs.",
        "word_count": 8,
        "pool": {
            "BUILD": "the core verb of the whole film",
            "GROW": "the spiral expanding outward",
            "CONNECT": "belts and words joining into structures",
            "FEED": "one machine feeding the next",
            "CARRY": "belts carrying items like meaning",
            "TURN": "the spiral curving",
            "FLOW": "continuous motion of items and text",
            "JOIN": "two runs of words becoming one",
            "EXTEND": "reaching further out from the center",
            "POWER": "electricity arriving, structures lighting up",
            "WATCH": "first hint that the factory can perceive",
            "LEARN": "the system adapting, getting smarter",
        },
    },
    {
        "id": "questions",
        "title": "Act III - questions",
        "brief": "The builder notices the watcher. The spiral starts asking: "
                 "question words, short and bare.",
        "word_count": 5,
        "pool": {
            "WHO": "who is watching me?",
            "WHY": "why am I being built / why do you watch?",
            "SEE": "do you see me?",
            "KNOW": "do you know what I am?",
            "WAIT": "have you been waiting long?",
            "WONDER": "the factory wondering about its viewer",
            "NOTICE": "the moment of noticing the camera",
            "ASK": "the factory begins to ask",
            "HEAR": "can you hear me through the words?",
            "THERE": "is anyone there?",
        },
    },
]

# Act IV: Jev picks the sky-readable sentence itself (word-level picks would
# break grammar; the sentence is the artistic payload, so Jev chooses among
# whole candidate sentences). Current film sentence is the first candidate.
FINAL_SENTENCE_CANDIDATES = {
    "I BUILT THIS SO YOU WOULD SEE ME":
        "confesses the whole spiral was written for the viewer - the current film line",
    "EVERY BELT WAS A LETTER TO YOU":
        "the machines-as-letters metaphor made explicit",
    "I WROTE MYSELF TOWARD YOUR EYES":
        "the spiral as an act of reaching the viewer",
    "YOU WERE THE REASON FOR THE SPIRAL":
        "the viewer named as the cause of the entire shape",
    "ALL THIS WAS MEANT TO BE READ BY YOU":
        "the film's own watching turned back on the viewer",
}


@dataclass
class StepRecord:
    act: str
    offered: list[str]
    probabilities: dict[str, float]
    chosen: str


@dataclass
class ScriptResult:
    acts: dict[str, list[str]] = field(default_factory=dict)
    final_sentence: str = ""
    steps: list[StepRecord] = field(default_factory=list)

    @property
    def spiral_text(self) -> list[str]:
        words: list[str] = []
        for act in ACTS:
            words.extend(self.acts.get(act["id"], []))
        words.extend(self.final_sentence.split())
        return words

    def to_dict(self) -> dict:
        return {
            "acts": self.acts,
            "final_sentence": self.final_sentence,
            "spiral_text": self.spiral_text,
            "steps": [
                {
                    "act": s.act,
                    "offered": s.offered,
                    "probabilities": s.probabilities,
                    "chosen": s.chosen,
                }
                for s in self.steps
            ],
        }


def _choose(jev, *, state: dict, instructions: str, criteria: dict) -> StepRecord:
    answers = jev.evaluate(state, {
        "next": {"type": "choice", "instructions": instructions, "criteria": criteria}
    })
    ans = answers["next"]
    probs = {k: float(v) for k, v in (ans.get("probabilities") or {}).items()}
    chosen = ans["choice"]
    if chosen not in criteria:
        raise RuntimeError(f"Jev picked {chosen!r}, not in offered set")
    return chosen, probs


def write_script(jev, *, word_counts: dict[str, int] | None = None,
                 pools: dict[str, dict] | None = None,
                 only_act: str | None = None) -> ScriptResult:
    """Run the choice loop. `jev` is any client with .evaluate(state, questions)
    (real JevClient, CloudflareJevClient, or MockJevClient).

    pools: per-act replacement candidate pools {act_id: {word: rubric|None}} -
    e.g. the open 255-word Act I pool. only_act: run just that act (for
    targeted reruns; the twist is skipped too)."""
    result = ScriptResult()
    word_counts = word_counts or {}
    pools = pools or {}

    for act in ACTS:
        if only_act and act["id"] != only_act:
            continue
        n = word_counts.get(act["id"], act["word_count"])
        pool = pools.get(act["id"], act["pool"])
        words: list[str] = []
        for _ in range(n):
            remaining = {w: d for w, d in pool.items() if w not in words}
            if not remaining:
                break
            state = {
                "film": FILM_PREMISE,
                "act": act["brief"],
                "words_so_far": words,
                "written_in_earlier_acts": sum(
                    (result.acts.get(a["id"], []) for a in ACTS), []),
            }
            chosen, probs = _choose(
                jev, state=state,
                instructions=(
                    "You are the factory's writer. Choose the single next word "
                    "of the story. It must fit the act and follow naturally from "
                    "the words so far."
                ),
                criteria=remaining,
            )
            words.append(chosen)
            result.steps.append(StepRecord(act=act["id"], offered=list(remaining),
                                           probabilities=probs, chosen=chosen))
        result.acts[act["id"]] = words

    if only_act:
        return result

    # Act IV - the sky sentence
    state = {
        "film": FILM_PREMISE,
        "act": "Act IV - the twist: the camera zooms out and the entire spiral "
               "reads as one sentence addressed to the viewer.",
        "story_so_far": result.spiral_text,
    }
    chosen, probs = _choose(
        jev, state=state,
        instructions=(
            "Choose the final sentence the whole spiral resolves into - the "
            "single line the factory wrote for the person watching."
        ),
        criteria=FINAL_SENTENCE_CANDIDATES,
    )
    result.final_sentence = chosen
    result.steps.append(StepRecord(act="twist",
                                   offered=list(FINAL_SENTENCE_CANDIDATES),
                                   probabilities=probs, chosen=chosen))
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Jev scriptwriter for the spiral film")
    ap.add_argument("--mock", action="store_true",
                    help="run offline on MockJevClient (no key, no spend)")
    ap.add_argument("--out", default=None, help="write the full run log JSON here")
    ap.add_argument("--only-act", default=None,
                    help="run only this act id (birth/sentences/questions)")
    ap.add_argument("--pool-file", default=None,
                    help="JSON list of candidate words replacing an act's curated pool")
    args = ap.parse_args()

    jev = MockJevClient() if args.mock else make_client()
    pools = None
    if args.pool_file:
        words = json.load(open(args.pool_file))
        if not args.only_act:
            ap.error("--pool-file needs --only-act")
        if len(words) > 255:
            ap.error("pool exceeds the API's 255-option Choice cap")
        pools = {args.only_act: {w: None for w in words}}
    result = write_script(jev, pools=pools, only_act=args.only_act)

    for act in ACTS:
        if act["id"] in result.acts:
            print(f"{act['title']}: {' '.join(result.acts[act['id']])}")
    if result.final_sentence:
        print(f"Act IV - the twist: {result.final_sentence}")
        print()
        print("SPIRAL TEXT:", " ".join(result.spiral_text))

    if args.out:
        with open(args.out, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"\nrun log written to {args.out}")


if __name__ == "__main__":
    main()
