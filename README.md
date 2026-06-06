# Eval Harness

MCP server for coding agents (Cursor, Claude Code). Pulls Langfuse eval runs into Notion or Excel for human grading. Does not run evals or modify project code.

## Agent workflow

1. **Read `eval-harness-guide`** — before implementing Langfuse eval instrumentation or pulling results.
2. Implement evals in the project (multi-stage pipelines OK).
3. `**pull_eval_run_for_grading**` — after a dataset run completes.

Eval projects only need the Langfuse SDK. They do not install this repo.

## MCP setup

One-time harness setup:

```bash
git clone <this-repo> ~/evaluation-harness   # or your path
cd ~/evaluation-harness
uv sync
cp .env.example .env                         # fill in credentials
```

Register the server globally in Cursor or Claude Code. Replace the path with your clone location.

**Cursor** — Settings → MCP → add server:

```json
{
  "mcpServers": {
    "eval-harness": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/you/evaluation-harness",
        "eval-harness-mcp"
      ]
    }
  }
}
```

**Claude Code** — add the same block to your MCP config (`~/.claude.json` or project MCP settings, depending on your setup).

Credentials load from the harness `.env` (recommended). You can also pass `env` in the MCP block if you prefer.

### Environment variables


| Variable                  | Required                        | Description                                 |
| ------------------------- | ------------------------------- | ------------------------------------------- |
| `LANGFUSE_PUBLIC_KEY`     | For `pull_eval_run_for_grading` | Langfuse API public key                     |
| `LANGFUSE_SECRET_KEY`     | For `pull_eval_run_for_grading` | Langfuse API secret key                     |
| `LANGFUSE_HOST`           | No                              | Default `https://cloud.langfuse.com`        |
| `NOTION_API_KEY`          | For Notion target               | Notion integration token                    |
| `NOTION_PARENT_PAGE_ID`   | For Notion target               | Page ID where grading tables are created    |
| `EVAL_HARNESS_OUTPUT_DIR` | No                              | Excel output directory (default `./output`) |


Eval traces must land in the **same Langfuse project** these keys can access.

**Notion one-time setup:** create an integration → copy token to `NOTION_API_KEY` → share the parent page with the integration → copy page ID to `NOTION_PARENT_PAGE_ID`.

### Agent rule (recommended)

Add to your Cursor/Claude Code rules:

> Before implementing Langfuse eval instrumentation, read the eval-harness MCP resource `eval-harness-guide`. After evals complete, call `pull_eval_run_for_grading` with explicit `dataset_name` and `run_name`.

## MCP surface


| Kind     | Name                        | Purpose                                                  |
| -------- | --------------------------- | -------------------------------------------------------- |
| Resource | `eval-harness-guide`        | Langfuse setup + how to call `pull_eval_run_for_grading` |
| Tool     | `pull_eval_run_for_grading` | Pull a dataset run into Notion or Excel                  |


Prefer explicit `dataset_name` + `run_name`. `run="latest"` selects the newest dataset run **project-wide** across all datasets.

## Grading sheet output

Each pull creates a **fresh** table.


| Column         | Source                  | Populated by eval-harness |
| -------------- | ----------------------- | ------------------------- |
| Input          | `trace.input`           | Yes                       |
| Model response | `trace.output`          | Yes                       |
| Model critique | `judge_verdict` comment | Yes                       |
| Model outcome  | `judge_verdict` value   | Yes                       |
| Human Critique | —                       | No                        |
| Human Outcome  | —                       | No                        |
| Agreement      | formula                 | Formula                   |


Notion also adds a **Case** column (trace ID). Match %: Excel writes `AVERAGE(Agreement)` in B1; in Notion, enable **Calculate → Average** on Agreement.

Chat inputs render as `[role]\ncontent` transcripts; other JSON is pretty-printed. Text truncates at 32k chars (Notion rich text chunks at 2k).

