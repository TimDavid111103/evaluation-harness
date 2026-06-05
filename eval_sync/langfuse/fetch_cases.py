from urllib.parse import quote

from langfuse import Langfuse

from eval_sync.format.json_values import format_input, format_output
from eval_sync.models import ContractError, EvalRow
from eval_sync.validate.contract import extract_judge_verdict


def fetch_cases(client: Langfuse, dataset_name: str, run_name: str) -> list[EvalRow]:
    encoded_dataset = quote(dataset_name, safe="")
    encoded_run = quote(run_name, safe="")
    run = client.api.datasets.get_run(encoded_dataset, encoded_run)

    rows: list[EvalRow] = []
    errors: list[str] = []

    for item in run.dataset_run_items:
        trace_id = item.trace_id
        if not trace_id:
            errors.append(f"Dataset run item {item.id} has no trace_id")
            continue
        try:
            trace = client.api.trace.get(trace_id)
            outcome, comment = extract_judge_verdict(trace.scores or [])
            rows.append(
                EvalRow(
                    input=format_input(trace.input),
                    model_response=format_output(trace.output),
                    model_critique=comment,
                    model_outcome=outcome,
                    trace_id=trace_id,
                )
            )
        except ContractError as exc:
            errors.append(f"Trace {trace_id}: {exc}")

    if errors:
        trace_ids = [
            e.split("Trace ", 1)[1].split(":", 1)[0]
            for e in errors
            if e.startswith("Trace ")
        ]
        raise ContractError(
            "Contract validation failed for one or more traces:\n" + "\n".join(errors),
            trace_ids=trace_ids,
        )

    if not rows:
        raise ContractError("No eval cases found in dataset run")

    return rows
