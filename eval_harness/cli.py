import json
from typing import Literal, Optional

import typer

from eval_harness.models import ContractError
from eval_harness.sync import run_sync

app = typer.Typer(no_args_is_help=True, help="Sync Langfuse eval runs to Notion or Excel.")


@app.command()
def sync(
    target: Literal["notion", "excel"] = typer.Option(..., help="Output destination"),
    run: str = typer.Option("latest", help="Run selector; use 'latest' or pass --dataset and --run-name"),
    dataset: Optional[str] = typer.Option(None, "--dataset", help="Langfuse dataset name"),
    run_name: Optional[str] = typer.Option(None, "--run-name", help="Langfuse run name"),
) -> None:
    """Pull a Langfuse eval run into Notion or Excel for human grading."""
    try:
        result = run_sync(
            target=target,
            run=run,
            dataset_name=dataset,
            run_name=run_name,
        )
        typer.echo(json.dumps(result.model_dump(mode="json"), indent=2))
    except ContractError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        if exc.trace_ids:
            typer.secho(f"Failing trace IDs: {', '.join(exc.trace_ids)}", err=True)
        raise typer.Exit(code=1) from exc
    except ValueError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


def main() -> None:
    app()


if __name__ == "__main__":
    main()
