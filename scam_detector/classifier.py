"""
Naive Bayes scam classifier. The model is trained in job_detector (manage.py train) and copied here as model.pkl;
its "job" class is the scam class.
"""
import math
import pickle
from functools import lru_cache

from scam_detector.constants import MODEL_FILE
from scam_detector.tokenizer import tokenize, build_ngrams


@lru_cache(maxsize=1)
def load_model() -> dict:
    # ~50 MB in memory, loaded once per process on first use
    with open(MODEL_FILE, 'rb') as f:
        return pickle.load(f)


def scam_probability(text: str) -> float:
    """
    :param text: message text
    :return: probability (0-1) that the message is a scam
    """
    model = load_model()
    jv, nv = model['job_vocab'], model['not_vocab']
    jc, nc = model['job_token_count'], model['not_token_count']
    V = model['vocab_size']
    a = model.get('alpha', 1.0)

    lp_scam = math.log(model['total_job'] / model['total_docs'])
    lp_not = math.log(model['total_not'] / model['total_docs'])
    for t in build_ngrams(tokenize(text)):
        if t not in jv and t not in nv:
            # unseen tokens carry no evidence
            continue
        lp_scam += math.log((jv.get(t, 0) + a) / (jc + a * V))
        lp_not += math.log((nv.get(t, 0) + a) / (nc + a * V))

    # numerically stable softmax
    mx = max(lp_scam, lp_not)
    e_scam, e_not = math.exp(lp_scam - mx), math.exp(lp_not - mx)
    return e_scam / (e_scam + e_not)
