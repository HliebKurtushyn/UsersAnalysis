from pydantic import BaseModel, ConfigDict, Field


class QueueRequest(BaseModel):
    """Request body for queue operations."""

    model_config = ConfigDict(extra="forbid")

    value: str = Field(min_length=1, max_length=100)


class PushTransactionRequest(BaseModel):
    """Request body for pushing transactions."""

    model_config = ConfigDict(extra="forbid")

    value: str = Field(min_length=1, max_length=100)


class QueueQuery(BaseModel):
    """Query parameters for queue operations."""

    limit: int | None = Field(default=None, gt=0)


class TransactionsQuery(BaseModel):
    """Query parameters for queue operations."""

    limit: int | None = Field(default=None, gt=0)
