from typing import Optional

from pydantic import BaseModel

from lqs.interface.base.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


class ObjectStore(CommonModel):
    name: str
    bucket_name: str
    access_key_id: Optional[str]
    region_name: Optional[str]
    endpoint_url: Optional[str]
    note: Optional[str]
    context: Optional[dict]
    disabled: bool
    default: bool
    read_only: bool
    managed: bool
    key_prefix: Optional[str]


class ObjectStoreDataResponse(DataResponseModel[ObjectStore]):
    pass


class ObjectStoreListResponse(PaginationModel[ObjectStore]):
    pass


class ObjectStoreCreateRequest(BaseModel):
    name: str
    bucket_name: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    note: Optional[str] = None
    context: Optional[dict] = None
    disabled: bool = False
    default: bool = False
    read_only: bool = False
    managed: bool = False
    key_prefix: Optional[str] = None


class ObjectStoreUpdateRequest(BaseModel):
    name: str = optional_field
    bucket_name: str = optional_field
    access_key_id: Optional[str] = optional_field
    secret_access_key: Optional[str] = optional_field
    region_name: Optional[str] = optional_field
    endpoint_url: Optional[str] = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    disabled: bool = optional_field
    default: bool = optional_field
    read_only: bool = optional_field
    managed: bool = optional_field
    key_prefix: Optional[str] = optional_field
