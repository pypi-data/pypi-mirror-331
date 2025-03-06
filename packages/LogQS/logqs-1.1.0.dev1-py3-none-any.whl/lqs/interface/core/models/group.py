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
)
from lqs.interface.core.models import Log


class Group(CommonModel, LockModel):
    name: str
    note: Optional[str]
    context: Optional[dict]
    default_workflow_id: Optional[UUID] = Field(
        ...,
        description="The ID of the workflow to be executed during state transitions of associated processes. DEPRECATED: this field is no longer populated with a non-null value.",
        deprecated=True,
    )

    def list_logs(self, **kwargs) -> List["Log"]:
        return self._app.list.logs(group_id=self.id, **kwargs).data


class GroupDataResponse(DataResponseModel[Group]):
    pass


class GroupListResponse(PaginationModel[Group]):
    pass


class GroupCreateRequest(LockCreateRequest):
    name: str
    note: Optional[str] = None
    context: Optional[dict] = None
    default_workflow_id: Optional[UUID] = Field(
        None,
        deprecated=True,
    )


class GroupUpdateRequest(LockUpdateRequest):
    name: str = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    default_workflow_id: Optional[UUID] = optional_deprecated_field
