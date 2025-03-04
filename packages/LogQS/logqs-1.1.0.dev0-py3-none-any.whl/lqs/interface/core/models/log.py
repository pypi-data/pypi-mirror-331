from typing import List, Optional
from uuid import UUID

from pydantic import Field

from lqs.interface.core.models.__common__ import (
    CommonModel,
    DataResponseModel,
    LockModel,
    LockCreateRequest,
    LockUpdateRequest,
    PaginationModel,
    optional_field,
    optional_deprecated_field,
    Int64,
)

from lqs.interface.core.models import Topic


class Log(CommonModel, LockModel):
    group_id: UUID = Field(
        ..., description="The ID of the group to which this log belongs."
    )
    name: str = Field(..., description="The name of the log (unique per group).")

    start_time: Optional[Int64] = Field(
        ..., description="The timestamp of the first record of the log."
    )
    end_time: Optional[Int64] = Field(
        ..., description="The timestamp of the last record of the log."
    )
    duration: Optional[Int64] = Field(
        ..., description="The duration of the log in nanoseconds."
    )
    base_timestamp: Optional[Int64] = Field(
        ...,
        description="The time, in nanoseconds, to be added to all timestamps in the log.",
    )
    record_size: int = Field(
        ..., description="The total size of all records in the log in bytes."
    )
    record_count: int = Field(
        ..., description="The total number of records in the log."
    )
    object_size: int = Field(
        ...,
        description="The total size of all objects in the log in bytes. DEPRECATED: this field is no longer populated with a non-zero value.",
        deprecated=True,
    )
    object_count: int = Field(
        ...,
        description="The total number of objects in the log. DEPRECATED: this field is no longer populated with a non-zero value.",
        deprecated=True,
    )

    note: Optional[str] = Field(
        ..., description="A general note about the log for reference."
    )
    context: Optional[dict] = Field(..., description="A JSON context for the log.")
    default_workflow_id: Optional[UUID] = Field(
        ...,
        description="The ID of the workflow to be executed during state transitions of associated processes. DEPRECATED: this field is no longer populated with a non-null value.",
        deprecated=True,
    )

    def list_topics(self, **kwargs) -> List["Topic"]:
        return self._app.list.topic(log_id=self.id, **kwargs).data


Log.model_rebuild()


class LogDataResponse(DataResponseModel[Log]):
    pass


class LogListResponse(PaginationModel[Log]):
    pass


class LogCreateRequest(LockCreateRequest):
    group_id: UUID
    name: str
    note: Optional[str] = None
    base_timestamp: Optional[Int64] = None
    context: Optional[dict] = None
    default_workflow_id: Optional[UUID] = Field(
        None,
        deprecated=True,
    )


class LogUpdateRequest(LockUpdateRequest):
    group_id: UUID = optional_field
    name: str = optional_field
    note: Optional[str] = optional_field
    base_timestamp: Optional[Int64] = optional_field
    context: Optional[dict] = optional_field
    default_workflow_id: Optional[UUID] = optional_deprecated_field
