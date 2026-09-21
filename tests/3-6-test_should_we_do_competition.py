import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "src/jev_factorio/5-should_we_do_competition.py"
spec = importlib.util.spec_from_file_location("jev_factorio.should_we_do_competition", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
PROJECT, QUESTIONS, run_session = mod.PROJECT, mod.QUESTIONS, mod.run_session


class RecordingJev:
    def __init__(self):
        self.calls = []

    def evaluate(self, state, questions):
        self.calls.append((state, questions))
        out = {}
        for qid, q in questions.items():
            if q["type"] == "choice":
                pick = next(iter(q["criteria"]))
                n = len(q["criteria"])
                out[qid] = {"type": "choice", "choice": pick,
                            "probabilities": {k: 1 / n for k in q["criteria"]}}
            else:
                out[qid] = {"type": "noul", "noul": 0.5}
        return out


def test_session_is_one_honest_batched_call_and_preserves_full_answers():
    jev = RecordingJev()
    result = run_session(jev)
    assert len(jev.calls) == 1
    state, questions = jev.calls[0]
    assert state["project"] == PROJECT
    assert questions == QUESTIONS
    assert "not a request for encouragement" in state["frame"]
    assert len(questions) == 5
    assert [q["type"] for q in questions.values()].count("choice") == 1
    assert [q["type"] for q in questions.values()].count("noul") == 4
    assert result["answers"]["whether_to_do_it"]["probabilities"]
    assert "ours" in result["pool_source"]
    assert "Jev's" in result["pool_source"]


def test_choice_pool_fits_api_cap_and_probes_are_verbatim():
    choice = QUESTIONS["whether_to_do_it"]
    assert 2 <= len(choice["criteria"]) <= 255
    assert set(choice["criteria"]) == {
        "do_it_now", "small_pilot_first", "do_it_differently", "do_not_do_it"
    }
    assert QUESTIONS["worth_doing"]["instructions"] == "Is it worth doing?"
    assert QUESTIONS["future_most_humans_accept"]["instructions"] == "Will it produce a picture of the future most humans accept?"
    assert QUESTIONS["regret_if_we_do_not"]["instructions"] == "Will you regret it if we don't do it?"
    assert QUESTIONS["fair_to_humans"]["instructions"] == "Is it fair to the humans it claims to represent?"
