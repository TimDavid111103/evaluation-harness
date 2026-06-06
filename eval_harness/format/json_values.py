import json
from typing import Any

MAX_CELL_CHARS = 32_000
NOTION_RICH_TEXT_CHUNK = 2000


def coerce_value(raw: str | dict | list | None) -> str | dict | list | None:
    if raw is None:
        return ""
    if isinstance(raw, str):
        stripped = raw.strip()
        if stripped.startswith(("{", "[")):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return raw
        return raw
    return raw


def _is_chat_transcript(value: list) -> bool:
    if not value:
        return False
    return all(
        isinstance(item, dict) and "role" in item and "content" in item for item in value
    )


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                if "text" in part:
                    parts.append(str(part["text"]))
                elif "type" in part and part.get("type") == "text" and "text" in part:
                    parts.append(str(part["text"]))
                else:
                    parts.append(json.dumps(part, ensure_ascii=False))
            else:
                parts.append(str(part))
        return "\n".join(parts)
    if isinstance(content, dict):
        return json.dumps(content, indent=2, ensure_ascii=False)
    return str(content)


def _format_chat_transcript(messages: list) -> str:
    blocks: list[str] = []
    for message in messages:
        role = str(message.get("role", "unknown"))
        content = _content_to_text(message.get("content"))
        blocks.append(f"[{role}]\n{content}")
    return "\n\n".join(blocks)


def _pretty_json(value: dict | list) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


def truncate(text: str, max_chars: int = MAX_CELL_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    suffix = f"\n… [truncated, {len(text)} chars total]"
    keep = max_chars - len(suffix)
    if keep < 0:
        return text[:max_chars]
    return text[:keep] + suffix


def format_input(raw: str | dict | list | None) -> str:
    value = coerce_value(raw)
    if value == "" or value is None:
        return ""
    if isinstance(value, list) and _is_chat_transcript(value):
        result = _format_chat_transcript(value)
    elif isinstance(value, (dict, list)):
        result = _pretty_json(value)
    else:
        result = str(value)
    return truncate(result)


def format_output(raw: str | dict | list | None) -> str:
    value = coerce_value(raw)
    if value == "" or value is None:
        return ""
    if isinstance(value, (dict, list)):
        result = _pretty_json(value)
    else:
        result = str(value)
        coerced = coerce_value(result)
        if isinstance(coerced, (dict, list)):
            result = _pretty_json(coerced)
    return truncate(result)


def split_rich_text(text: str, chunk_size: int = NOTION_RICH_TEXT_CHUNK) -> list[dict]:
    if not text:
        return [{"type": "text", "text": {"content": ""}}]
    chunks: list[dict] = []
    for i in range(0, len(text), chunk_size):
        chunks.append({"type": "text", "text": {"content": text[i : i + chunk_size]}})
    return chunks
