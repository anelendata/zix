import base64
import os

from typing import List

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
from plugins.subscriptions import (
    models as subscriptions_models,
    crud as subscriptions_crud,
    schemas as subscriptions_schemas,
    )


logger = logging.get_logger(logger_name=__name__)


UserEnrichedPrivate = users_schemas.UserEnrichedPrivate
if config.USE_SUBSCRIPTIONS:
    UserPrivate = subscriptions_schemas.UserPrivate
    UserEnrichedPrivate = subscriptions_schemas.UserEnrichedPrivate


@router.get(config.API_PATH + "/admin/users", response_model=List[users_schemas.UserPrivate])
def read_users(
    email: str = None,
    offset : int = 0,
    limit: int = 1000,
    current_user: users_schemas.UserPrivate = Depends(users_crud.get_current_active_admin_user),
    db: Session = Depends(get_db),
    ):
    if email:
        unencoded_email = base64.b64decode(email).decode("utf-8")
        user = crud.get_user_by_email(db, unencoded_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with {unencoded_email} not found")
        return [user]
    users = users_crud.get_users(db, offset=offset, limit=limit)
    return users
