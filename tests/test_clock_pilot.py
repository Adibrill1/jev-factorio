from jev_factorio.clock_pilot import request_body, run_session, QUESTIONS

def test_request_shape():
 b=request_body(); assert b['model']=='jev-latest'; assert len(b['questions'])==8
 assert set(b['questions'])==set(QUESTIONS)
def test_answer_preservation():
 a={k:{'type':q['type']} for k,q in QUESTIONS.items()}; assert run_session(a)['answers'] is a
