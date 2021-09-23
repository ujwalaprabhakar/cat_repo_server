import enum
import json
from datetime import datetime
from typing import Any, Dict, Generic, List, NamedTuple, NewType, Optional, TypeVar

import pymongo
from pydantic import BaseModel, PositiveInt
from pydantic.generics import GenericModel

ResponseT = TypeVar("ResponseT")
UnsetT = NewType("UnsetT", str)

OrganizationID = NewType("OrganizationID", str)
CatID = NewType("CatID", str)

JSON = Dict[str, Any]


class CatSortKey(str, enum.Enum):
    id = "id"
    name = "name"


class SortOrder(int, enum.Enum):
    asc = pymongo.ASCENDING
    desc = pymongo.DESCENDING


class CatSortPredicate(NamedTuple):
    key: CatSortKey
    order: SortOrder


class Page(BaseModel):
    number: PositiveInt
    size: PositiveInt


class PageMetadata(BaseModel):
    has_next_page: bool


class PagedResult(GenericModel, Generic[ResponseT]):
    results: List[ResponseT]
    metadata: PageMetadata


class MembershipType(str, enum.Enum):
    organization = "organization"


class Scope(BaseModel):
    id: OrganizationID  # In the future, this might be Union[OrganizationID, TeamID, etc...]
    type: MembershipType


CatSortPredicates = NewType("CatSortPredicates", List[CatSortPredicate])


def create_unique_cat_sort_predicates_list(
    sort_predicate_list: List[CatSortPredicate],
) -> CatSortPredicates:
    """
    Creates an instance of CatSortPredicates. Includes validation to make sure there are
    no duplicate sort_keys within the list.
    """
    sort_keys = [sort_predicate.key for sort_predicate in sort_predicate_list]
    if len(sort_keys) != len(set(sort_keys)):
        raise ValueError("Duplicate sort_key values provided.")
    return CatSortPredicates(sort_predicate_list)


class ServiceClientResponse(NamedTuple):
    status_code: int
    text: str

    def json(self) -> dict:
        return json.loads(self.text)


class UnsavedCat(BaseModel):
    name: str


class Cat(BaseModel):
    id: CatID
    name: str
    ctime: datetime
    mtime: datetime


class CatSummary(BaseModel):
    id: CatID
    name: str


class PartialUpdateCat(BaseModel):
    url: Optional[str]


class CatFilter(BaseModel):
    cat_id: Optional[CatID] = None
    name: Optional[str] = None
    scope: Optional[Scope] = None


class LinkResponse(BaseModel):
    href: str
    rel: str
    type: str


class StatusViewResponse(BaseModel):
    service: str
    version: str
    links: Optional[List[LinkResponse]]
    feature_flags: JSON


class ListResponse(GenericModel, Generic[ResponseT]):
    results: List[ResponseT]
    metadata: PageMetadata
