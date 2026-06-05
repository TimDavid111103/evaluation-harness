from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RunRef(BaseModel):
    dataset_name: str
    run_name: str
    run_id: str
    created_at: datetime | None = None


class EvalRow(BaseModel):
    input: str
    model_response: str
    model_critique: str
    model_outcome: Literal["pass", "fail"]
    trace_id: str


class SyncResult(BaseModel):
    target: Literal["notion", "excel"]
    dataset_name: str
    run_name: str
    run_id: str
    row_count: int
    output_path: str | None = None
    page_url: str | None = None
    database_id: str | None = None
    warnings: list[str] = Field(default_factory=list)


class ContractError(Exception):
    def __init__(self, message: str, trace_ids: list[str] | None = None):
        super().__init__(message)
        self.trace_ids = trace_ids or []
