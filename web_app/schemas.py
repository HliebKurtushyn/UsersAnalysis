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


class QueueQuery(BaseModel):
    """Query parameters for queue operations."""

    """WIP: More detailed description of the query parameters soon."""

    limit: int | None = Field(default=None, gt=0)


class TransactionsQuery(BaseModel):
    """Query parameters for queue operations."""

    """WIP: More detailed description of the query parameters soon."""

    limit: int | None = Field(default=None, gt=0)
