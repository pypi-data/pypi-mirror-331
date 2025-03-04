from typing import Optional

from pydantic import BaseModel

from lqs.interface.core.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


class Callback(CommonModel):
    name: str
    note: Optional[str]
    context: Optional[dict]
    managed: bool
    default: bool
    disabled: bool
    uri: Optional[str]
    parameter_schema: Optional[dict]


class CallbackDataResponse(DataResponseModel[Callback]):
    pass


class CallbackListResponse(PaginationModel[Callback]):
    pass


class CallbackCreateRequest(BaseModel):
    name: str
    note: Optional[str] = None
    context: Optional[dict] = None
    managed: bool = False
    default: bool = False
    disabled: bool = False
    uri: Optional[str] = None
    secret: Optional[str] = None
    parameter_schema: Optional[dict] = None


class CallbackUpdateRequest(BaseModel):
    name: str = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    managed: bool = optional_field
    default: bool = optional_field
    disabled: bool = optional_field
    uri: Optional[str] = optional_field
    secret: Optional[str] = optional_field
    parameter_schema: Optional[dict] = optional_field
