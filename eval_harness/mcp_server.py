from importlib.metadata import version
from typing import Literal

from fastmcp import FastMCP

from eval_harness.models import ContractError
from eval_harness.sync import run_sync
from eval_harness.validate.contract_spec import render_eval_harness_guide

MCP_INSTRUCTIONS = """\
Eval-harness pulls Langfuse eval runs into Notion or Excel for human grading.

Read the eval-harness-guide resource before instrumenting Langfuse evals or calling pull_eval_run_for_grading.
"""

mcp = FastMCP(
    "eval-harness",
    version=version("eval-harness"),
    instructions=MCP_INSTRUCTIONS,
)


@mcp.resource(
    "eval-harness://docs/guide",
    name="eval-harness-guide",
    description=(
        "Langfuse instrumentation contract and pull_eval_run_for_grading usage. "
        "Read before implementing evals or pulling results."
    ),
    mime_type="text/markdown",
)
def eval_harness_guide() -> str:
    return render_eval_harness_guide()


@mcp.tool
def pull_eval_run_for_grading(
    target: Literal["notion", "excel"],
    run: str = "latest",
    dataset_name: str | None = None,
    run_name: str | None = None,
) -> dict:
    """Pull a Langfuse dataset run into Notion or Excel for human grading.

    Prerequisite: eval traces must match the eval-harness-guide resource (dataset run,
    trace.input/output, trace-level judge_verdict score). Creates a fresh grading table.

    Args:
        target: Output destination — "notion" or "excel".
        dataset_name: Langfuse dataset name (pass with run_name; preferred over run="latest").
        run_name: Langfuse run name (pass with dataset_name).
        run: Default "latest" selects the newest run project-wide; prefer explicit names.
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
    except (ValueError, RuntimeError) as exc:
        return {"error": str(exc)}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
