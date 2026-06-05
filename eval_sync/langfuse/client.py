from langfuse import Langfuse

from eval_sync.config import get_langfuse_config


def create_langfuse_client() -> Langfuse:
    cfg = get_langfuse_config()
    return Langfuse(
        public_key=cfg["public_key"],
        secret_key=cfg["secret_key"],
        host=cfg["host"],
    )
