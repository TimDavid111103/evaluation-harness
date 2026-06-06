from typing import Any, Literal

from eval_harness.models import ContractError

JUDGE_SCORE_NAME = "judge_verdict"
PASS_STRINGS = frozenset({"pass", "true", "yes", "1"})
FAIL_STRINGS = frozenset({"fail", "false", "no", "0"})


def _score_name(score: Any) -> str | None:
    name = getattr(score, "name", None)
    if name is None and isinstance(score, dict):
        name = score.get("name")
    return name


def _score_value(score: Any) -> Any:
    value = getattr(score, "value", None)
    if value is None and isinstance(score, dict):
        value = score.get("value")
    return value


def _score_comment(score: Any) -> str:
    comment = getattr(score, "comment", None)
    if comment is None and isinstance(score, dict):
        comment = score.get("comment")
    return str(comment) if comment is not None else ""


def _observation_id(score: Any) -> str | None:
    obs_id = getattr(score, "observation_id", None) or getattr(score, "observationId", None)
    if obs_id is None and isinstance(score, dict):
        obs_id = score.get("observation_id") or score.get("observationId")
    return obs_id


def normalize_outcome(value: Any) -> Literal["pass", "fail"]:
    if isinstance(value, bool):
        return "pass" if value else "fail"
    if isinstance(value, (int, float)):
        if value in (1, 1.0):
            return "pass"
        if value in (0, 0.0):
            return "fail"
        raise ContractError(f"judge_verdict numeric value {value!r} is not 0/1")
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in PASS_STRINGS:
            return "pass"
        if normalized in FAIL_STRINGS:
            return "fail"
        raise ContractError(f"judge_verdict string value {value!r} is not pass/fail")
    raise ContractError(f"judge_verdict value type {type(value).__name__} is unsupported")


def extract_judge_verdict(scores: list[Any]) -> tuple[Literal["pass", "fail"], str]:
    trace_level = [
        s for s in scores if _score_name(s) == JUDGE_SCORE_NAME and not _observation_id(s)
    ]
    if len(trace_level) == 0:
        raise ContractError(f"Missing trace-level score named {JUDGE_SCORE_NAME!r}")
    if len(trace_level) > 1:
        raise ContractError(f"Multiple trace-level {JUDGE_SCORE_NAME!r} scores found")
    score = trace_level[0]
    outcome = normalize_outcome(_score_value(score))
    comment = _score_comment(score)
    return outcome, comment
