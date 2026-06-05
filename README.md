# Eval Sync Harness

MCP-triggered sync service that pulls LLM-judge eval results from Langfuse into a Notion table or Excel sheet for human grading. Moves and structures data only — runs no evals, never touches project code.

## Setup

```bash
uv sync --extra dev
cp .env.example .env
# Fill in Langfuse and (optionally) Notion credentials
```

### Environment variables

| Variable | Required | Description |
| -------- | -------- | ----------- |
| `LANGFUSE_PUBLIC_KEY` | Yes | Langfuse API public key |
| `LANGFUSE_SECRET_KEY` | Yes | Langfuse API secret key |
| `LANGFUSE_HOST` | No | Default `https://cloud.langfuse.com` |
| `NOTION_API_KEY` | For Notion target | Notion integration token |
| `NOTION_PARENT_PAGE_ID` | For Notion target | Page ID where sync tables are created |
| `EVAL_SYNC_OUTPUT_DIR` | No | Excel output directory (default `./output`) |

## Per-project contract

Every evaluated project must:

1. Trace eval runs to Langfuse as a **dataset run**
2. Emit `judge_verdict` as a shared ScoreConfig (boolean or pass/fail categorical)
3. Put judge rationale in the score **comment**
4. Attach the score at **trace level**, one trace per eval case

Example (Python SDK):

```python
root_span.score_trace(
    name="judge_verdict",
    value=True,  # or "pass" / "fail"
    comment="The response correctly identifies the issue.",
)
```

If a project does not follow this contract, sync returns a structured error listing failing trace IDs.

## Usage

### CLI

```bash
# Latest dataset run project-wide → Excel
uv run eval-sync sync --target excel

# Explicit run → Notion
uv run eval-sync sync --target notion --dataset my-dataset --run-name my-run-2026-06-05
```

### MCP (Cursor)

Register in Cursor MCP settings:

```json
{
  "mcpServers": {
    "eval-sync": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "eval_sync/mcp_server.py:mcp"],
      "cwd": "/path/to/evaluation-harness",
      "env": {
        "LANGFUSE_PUBLIC_KEY": "pk-lf-...",
        "LANGFUSE_SECRET_KEY": "sk-lf-...",
        "LANGFUSE_HOST": "https://cloud.langfuse.com"
      }
    }
  }
}
```

Or from the repo root with `fastmcp.json`:

```bash
uv run fastmcp run eval_sync/mcp_server.py:mcp
```

**Tool:** `sync(target, run="latest", dataset_name=None, run_name=None)`

## Output schema

Each sync creates a **fresh** table with 7 columns:

| Column | Populated by sync |
| ------ | ----------------- |
| Input | Yes |
| Model response | Yes |
| Model critique | Yes |
| Model outcome | Yes |
| Human Critique | No |
| Human Outcome | No |
| Agreement | Formula (`Model outcome == Human Outcome`) |

**Match %:** average of Agreement. Excel writes this in cell B1. In Notion, enable **Calculate → Average** on the Agreement column.

### JSON handling

Langfuse trace input/output may be chat arrays, nested eval objects, or plain text. The sync:

- Renders chat inputs as `[role]\ncontent` transcripts
- Pretty-prints other JSON structures
- Truncates at 32k characters; chunks Notion rich text at 2k

## Workflow

1. Run evals in your project; judge scores each case in Langfuse
2. Call `sync` (CLI or MCP)
3. Fill Human Outcome and Human Critique in the sheet
4. Read match % and review mismatched rows
5. Change your project, re-run evals, sync again to a new table
6. Compare match % between runs

## Tests

```bash
uv run pytest
```

## Out of scope

Eval execution, project adapters, critique alignment, kappa/confusion matrices, stable case IDs, upsert/idempotency, cross-run diffs.
