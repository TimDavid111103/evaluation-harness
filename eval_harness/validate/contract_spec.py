from eval_harness.validate.contract import JUDGE_SCORE_NAME


def render_eval_harness_guide() -> str:
    score = JUDGE_SCORE_NAME
    return f"""# Eval harness

## Langfuse setup

Run evals as a **dataset run** — one trace per case, each run item linked via `trace_id`.
Traces must be in the Langfuse project this server's credentials can access.

On each **root trace**, set four fields:

| Langfuse | Sheet column |
| -------- | ------------ |
| `trace.input` | Input |
| `trace.output` | Model response |
| trace-level `{score}` comment | Model critique |
| trace-level `{score}` value | Model outcome |

Requirements:
- Use `score_trace(name="{score}", ...)` on the **root trace** (not span-level scoring)
- Exactly one `{score}` score per trace
- Value: bool, 0/1, or pass/fail strings

```python
root_span.update(input=eval_input, output=final_response)
root_span.score_trace(name="{score}", value=True, comment="Judge rationale.")
```

Pipeline stages may be traced as child spans; only the root trace needs the fields above.

## Pull results

When evals finish, call **`pull_eval_run_for_grading`**:

| Parameter | Required | Notes |
| --------- | -------- | ----- |
| `target` | yes | `"notion"` or `"excel"` |
| `dataset_name` | yes* | Langfuse dataset name |
| `run_name` | yes* | Langfuse run name |
| `run` | no | Default `"latest"` — avoid unless you have one dataset |

*Prefer explicit `dataset_name` + `run_name` over `run="latest"`.
"""
