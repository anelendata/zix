import os

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import RedirectResponse, HTMLResponse

from zix.server import logging, utils
from zix.server.database import Session, get_db

import config
from . import crud, models, schemas
from fastapi import APIRouter
router = APIRouter()


# Use this format to import other plugin's models, crud, and schemas
from plugins.users import (
    models as users_models,
    crud as users_crud,
    schemas as users_schemas,
    )


logger = logging.get_logger(logger_name=__name__)


@router.post(config.API_PATH + "/my_objects", response_model=schemas.MyObjectPrivate)
def create_my_object(
    my_object: schemas.MyObjectPrivate,
    # One needs to be logged in to access this method
    current_user: users_schemas.UserPrivate = Depends(users_crud.get_current_active_user),
    db: Session = Depends(get_db),
    ):
    my_object = crud.create_my_object(db, my_object)
    return my_object


@router.get(config.API_PATH + "/my_objects/{uid}", response_model=schemas.MyObjectPublic)
def read_my_object(
    uid: str,
    # Without Depends get_current_active_user here, this get method
    db: Session = Depends(get_db),
    ):
    my_object = crud.get_my_object_by_uid(db, uid)
    # Only the public info will be returned, see response_model decoration parameter
    return my_object


@router.put(config.API_PATH + "/my_objects/{uid}", response_model=schemas.MyObjectPrivate)
def update_my_object(
    uid: str,
    my_object: schemas.MyObjectPrivate,
    # One needs to be logged in to access this method
    current_user: users_schemas.UserPrivate = Depends(users_crud.get_current_active_user),
    db: Session = Depends(get_db),
    ):
    my_object = crud.update_my_object(db, my_object)
    return my_object


@router.delete(config.API_PATH + "/my_objects/{uid}")
def delete_my_object(
    uid: str,
    my_object: schemas.MyObjectPrivate,
    # One needs to be logged in as admin to access this method
    current_user: users_schemas.UserPrivate = Depends(users_crud.get_current_active_admin_user),
    db: Session = Depends(get_db),
    ):
    crud.delete_my_object(db, my_object)
    return {
        "status": "success",
        "message": f"Object {uid} has been deleted",
    }
