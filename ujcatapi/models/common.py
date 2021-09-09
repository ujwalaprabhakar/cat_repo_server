from typing import Any, Dict

import motor.motor_asyncio
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from ujcatapi import config, dto

_db = None
MONGO_DUPLICATION_ERROR = 11000

BSONDocument = Dict[str, Any]


async def _get_db() -> Database:
    global _db
    if _db is None:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            host=config.MONGODB_URL,
            tz_aware=True,
            maxPoolSize=config.MONGO_MAX_POOL_SIZE,
            retryWrites=False,
        )
        _db = client.get_database()

    return _db


async def get_collection(collection_name: str) -> Collection:
    db = await _get_db()
    return db[collection_name]


def bson_id_to_organization_id(obj_id: ObjectId) -> dto.OrganizationID:
    return dto.OrganizationID(str(obj_id))


def bson_id_to_cat_id(obj_id: ObjectId) -> dto.CatID:
    return dto.CatID(str(obj_id))


def _calculate_db_skip_value(page: dto.Page) -> int:
    return (page.number - 1) * page.size
