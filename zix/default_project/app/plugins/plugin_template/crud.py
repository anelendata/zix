import uuid
from typing import Any, Optional, Union

from fastapi import Depends, HTTPException, status, Request

from zix.server import database, logging

import config
from . import models, schemas

# Use this format to import other plugin's models, crud, and schemas
from plugins.users import (
    models as users_models,
    crud as users_crud,
    schemas as users_schemas,
    )

logger = logging.get_logger(logger_name=__name__)


# Write your model create, read, update, delete logic below
# Read this: https://docs.sqlalchemy.org/en/20/orm/quickstart.html#create-objects-and-persist
def update_my_object(
    db: database.Session,
    my_object: schemas.MyObjectPrivate,
    ):
    db.add(my_object)
    db.commit()
    # This will update the object with auto assigned fields like uid when creating.
    db.refresh(my_object)
    return my_object


def create_my_object(
    db: database.Session,
    my_object: schemas.MyObjectPrivate,
    ):
    db_my_object = models.MyObject(
        public_info=my_object.public_info,
        private_info=my_object.private_info,
    )
    my_object = update_my_object(db, db_my_object)
    return my_object


def get_my_object_by_uid(
    db: database.Session,
    uid: Union[str, uuid.UUID],
    ):
    if isinstance(uid, str):
        uid = uuid.UUID(uid)
    my_object = db.query(models.MyObject).filter(models.MyObject.uid==uid).first()
    if not my_object:
        return HTTPException(status_code=404, detail="Object not found")
    return my_object


def delete_my_object(
    db: database.Session,
    uid: Union[str, uuid.UUID],
    ):
    my_object = get_my_object_by_uid(db, uid)
    db.delete(my_object)
    db.commit()
