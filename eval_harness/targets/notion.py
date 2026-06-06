import time
from datetime import datetime

from notion_client import Client

from eval_harness.format.json_values import split_rich_text
from eval_harness.models import EvalRow, RunRef

AGREEMENT_FORMULA = (
    'if(empty(prop("Human Outcome")), "", '
    'if(prop("Model outcome") == prop("Human Outcome"), 1, 0))'
)

CALLOUT_TEXT = (
    "Match %: after filling Human Outcome, enable Calculate → Average "
    "on the Agreement column in the table below."
)


def _rich_text_property(text: str) -> dict:
    return {"rich_text": split_rich_text(text)}


def _select_property(value: str) -> dict:
    return {"select": {"name": value}}


def write_notion(
    client: Client,
    rows: list[EvalRow],
    run: RunRef,
    parent_page_id: str,
) -> tuple[str, str]:
    date_str = datetime.now().strftime("%Y-%m-%d")
    page_title = f"Eval harness — {run.dataset_name}/{run.run_name} — {date_str}"

    database = client.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": page_title}}],
        properties={
            "Case": {"title": {}},
            "Input": {"rich_text": {}},
            "Model response": {"rich_text": {}},
            "Model critique": {"rich_text": {}},
            "Model outcome": {
                "select": {
                    "options": [
                        {"name": "pass", "color": "green"},
                        {"name": "fail", "color": "red"},
                    ]
                }
            },
            "Human Critique": {"rich_text": {}},
            "Human Outcome": {
                "select": {
                    "options": [
                        {"name": "pass", "color": "green"},
                        {"name": "fail", "color": "red"},
                    ]
                }
            },
            "Agreement": {"formula": {"expression": AGREEMENT_FORMULA}},
        },
    )

    database_id = database["id"]
    page_url = database.get("url") or f"https://notion.so/{database_id.replace('-', '')}"

    client.blocks.children.append(
        block_id=database_id,
        children=[
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": CALLOUT_TEXT}}],
                    "icon": {"type": "emoji", "emoji": "📊"},
                },
            }
        ],
    )

    for index, row in enumerate(rows, start=1):
        client.pages.create(
            parent={"database_id": database_id},
            properties={
                "Case": {"title": [{"text": {"content": row.trace_id or str(index)}}]},
                "Input": _rich_text_property(row.input),
                "Model response": _rich_text_property(row.model_response),
                "Model critique": _rich_text_property(row.model_critique),
                "Model outcome": _select_property(row.model_outcome),
            },
        )
        time.sleep(0.34)

    return page_url, database_id
