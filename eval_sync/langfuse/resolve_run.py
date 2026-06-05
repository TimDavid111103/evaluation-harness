from __future__ import annotations

from datetime import datetime
from urllib.parse import quote

from langfuse import Langfuse

from eval_sync.models import RunRef


def _paginate_datasets(client: Langfuse) -> list:
    datasets = []
    page = 1
    while True:
        response = client.api.datasets.list(page=page, limit=100)
        datasets.extend(response.data)
        if page >= response.meta.total_pages:
            break
        page += 1
    return datasets


def _paginate_runs(client: Langfuse, dataset_name: str) -> list:
    runs = []
    page = 1
    encoded_name = quote(dataset_name, safe="")
    while True:
        response = client.api.datasets.get_runs(encoded_name, page=page, limit=100)
        runs.extend(response.data)
        if page >= response.meta.total_pages:
            break
        page += 1
    return runs


def resolve_latest_run(client: Langfuse) -> RunRef:
    latest: RunRef | None = None
    for dataset in _paginate_datasets(client):
        for run in _paginate_runs(client, dataset.name):
            created_at = run.created_at
            if latest is None or (
                created_at
                and (latest.created_at is None or created_at > latest.created_at)
            ):
                latest = RunRef(
                    dataset_name=run.dataset_name or dataset.name,
                    run_name=run.name,
                    run_id=run.id,
                    created_at=created_at,
                )
    if latest is None:
        raise ValueError("No dataset runs found in Langfuse project")
    return latest


def resolve_explicit_run(
    client: Langfuse, dataset_name: str, run_name: str
) -> RunRef:
    encoded_dataset = quote(dataset_name, safe="")
    encoded_run = quote(run_name, safe="")
    run = client.api.datasets.get_run(encoded_dataset, encoded_run)
    return RunRef(
        dataset_name=run.dataset_name or dataset_name,
        run_name=run.name,
        run_id=run.id,
        created_at=run.created_at,
    )


def resolve_run(
    client: Langfuse,
    run: str = "latest",
    dataset_name: str | None = None,
    run_name: str | None = None,
) -> RunRef:
    if dataset_name and run_name:
        return resolve_explicit_run(client, dataset_name, run_name)
    if run != "latest":
        raise ValueError(
            "Explicit run requires both dataset_name and run_name, or use run='latest'"
        )
    return resolve_latest_run(client)
