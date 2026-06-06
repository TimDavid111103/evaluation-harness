import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_langfuse_config() -> dict[str, str]:
    return {
        "public_key": require_env("LANGFUSE_PUBLIC_KEY"),
        "secret_key": require_env("LANGFUSE_SECRET_KEY"),
        "host": os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    }


def get_notion_config() -> dict[str, str]:
    return {
        "api_key": require_env("NOTION_API_KEY"),
        "parent_page_id": require_env("NOTION_PARENT_PAGE_ID"),
    }


def get_output_dir() -> Path:
    path = Path(os.getenv("EVAL_HARNESS_OUTPUT_DIR", "./output"))
    path.mkdir(parents=True, exist_ok=True)
    return path
