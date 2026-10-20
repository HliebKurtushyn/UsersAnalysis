from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QueueRequest(BaseModel):
    """Request body for adding a client to the queue."""

    """WIP: More detailed description of the request body soon."""

    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=100)


class PushTransactionRequest(BaseModel):
    """Request body for adding a transaction."""

    """WIP: More detailed description of the request body soon."""

    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=100)


class StructureOperationRequest(BaseModel):
    """Request body for removing an item from a structure."""

    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1, max_length=100)


class QueueQuery(BaseModel):
    """Query parameters for queue operations."""

    """WIP: More detailed description of the query parameters soon."""

    limit: int | None = Field(default=None, gt=0)


class TransactionsQuery(BaseModel):
    """Query parameters for queue operations."""

    """WIP: More detailed description of the query parameters soon."""

    limit: int | None = Field(default=None, gt=0)


class LogsQuery(BaseModel):
    """Query parameters for operation log filtering."""

    user_id: str | None = Field(default=None, min_length=1, max_length=100)
    operation_type: Literal["enqueue", "dequeue", "push", "pop", "undo"] | None = None
    limit: int = Field(default=50, gt=0)
    offset: int = Field(default=0, ge=0)


class PrepareDataRequest(BaseModel):
    """Request body for rebuilding the cleaned dataset."""

    model_config = ConfigDict(extra="forbid")

    rows: int = Field(gt=0, le=1_000_000)
