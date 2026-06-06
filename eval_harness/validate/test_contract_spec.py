from eval_harness.validate.contract import JUDGE_SCORE_NAME
from eval_harness.validate.contract_spec import render_eval_harness_guide


def test_eval_harness_guide_covers_langfuse_contract():
    md = render_eval_harness_guide()
    assert JUDGE_SCORE_NAME in md
    assert "trace.input" in md
    assert "trace.output" in md
    assert "score_trace" in md
    assert "trace_id" in md
    assert "dataset run" in md.lower()


def test_eval_harness_guide_covers_pull_tool():
    md = render_eval_harness_guide()
    assert "pull_eval_run_for_grading" in md
    assert "dataset_name" in md
    assert "run_name" in md
