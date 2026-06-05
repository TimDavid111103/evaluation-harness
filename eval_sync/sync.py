from typing import Literal

from eval_sync.config import get_notion_config, get_output_dir
from eval_sync.langfuse.client import create_langfuse_client
from eval_sync.langfuse.fetch_cases import fetch_cases
from eval_sync.langfuse.resolve_run import resolve_run
from eval_sync.models import SyncResult
from eval_sync.targets.excel import write_excel
from eval_sync.targets.notion import write_notion

try:
    from notion_client import Client as NotionClient
except ImportError:  # pragma: no cover
    NotionClient = None  # type: ignore[misc, assignment]


def run_sync(
    target: Literal["notion", "excel"],
    run: str = "latest",
    dataset_name: str | None = None,
    run_name: str | None = None,
) -> SyncResult:
    client = create_langfuse_client()
    run_ref = resolve_run(
        client, run=run, dataset_name=dataset_name, run_name=run_name
    )
    rows = fetch_cases(client, run_ref.dataset_name, run_ref.run_name)

    warnings: list[str] = []

    if target == "excel":
        output_path = write_excel(rows, run_ref, get_output_dir())
        return SyncResult(
            target=target,
            dataset_name=run_ref.dataset_name,
            run_name=run_ref.run_name,
            run_id=run_ref.run_id,
            row_count=len(rows),
            output_path=str(output_path),
            warnings=warnings,
        )

    if NotionClient is None:
        raise RuntimeError("notion-client is not installed")

    notion_cfg = get_notion_config()
    notion = NotionClient(auth=notion_cfg["api_key"])
    page_url, database_id = write_notion(
        notion,
        rows,
        run_ref,
        parent_page_id=notion_cfg["parent_page_id"],
    )
    return SyncResult(
        target=target,
        dataset_name=run_ref.dataset_name,
        run_name=run_ref.run_name,
        run_id=run_ref.run_id,
        row_count=len(rows),
        page_url=page_url,
        database_id=database_id,
        warnings=warnings,
    )
