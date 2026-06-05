from typing import Literal

from fastmcp import FastMCP

from eval_sync.models import ContractError
from eval_sync.sync import run_sync

mcp = FastMCP("eval-sync-harness")


@mcp.tool
def sync(
    target: Literal["notion", "excel"],
    run: str = "latest",
    dataset_name: str | None = None,
    run_name: str | None = None,
) -> dict:
    """Pull a Langfuse eval run into Notion or Excel for human grading.

    Reads trace-level judge_verdict scores and writes model columns;
    leaves human columns blank. Creates a fresh table each call.
    """
    try:
        result = run_sync(
            target=target,
            run=run,
            dataset_name=dataset_name,
            run_name=run_name,
        )
        return result.model_dump(mode="json")
    except ContractError as exc:
        return {
            "error": str(exc),
            "trace_ids": exc.trace_ids,
        }
    except ValueError as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    mcp.run()
