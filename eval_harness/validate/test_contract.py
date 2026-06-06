import pytest

from eval_harness.models import ContractError
from eval_harness.validate.contract import extract_judge_verdict, normalize_outcome


class Score:
    def __init__(self, name, value, comment=None, observation_id=None):
        self.name = name
        self.value = value
        self.comment = comment
        self.observation_id = observation_id


def test_normalize_outcome_bool():
    assert normalize_outcome(True) == "pass"
    assert normalize_outcome(False) == "fail"


def test_normalize_outcome_string():
    assert normalize_outcome("pass") == "pass"
    assert normalize_outcome("FAIL") == "fail"


def test_extract_judge_verdict():
    scores = [Score("judge_verdict", True, comment="Looks good")]
    outcome, comment = extract_judge_verdict(scores)
    assert outcome == "pass"
    assert comment == "Looks good"


def test_reject_observation_level_score():
    scores = [Score("judge_verdict", True, observation_id="obs-1")]
    with pytest.raises(ContractError, match="Missing trace-level"):
        extract_judge_verdict(scores)


def test_reject_missing_score():
    with pytest.raises(ContractError, match="Missing trace-level"):
        extract_judge_verdict([])
