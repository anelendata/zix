import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional, Union
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_
from starlette.authentication import SimpleUser
from jose import jwt

from zix.server import database, logging

import config
from . import models, schemas

from plugins.users import models as users_models, crud as users_crud


logger = logging.get_logger(logger_name=__name__)


def create_access_token(
        db: database.Session,
        data: dict,
        expires_at: Any = None,
        expires_delta: Optional[timedelta] = None,
        access_token = None,
        id_token = None,
        ):

    if not expires_at:
        if expires_delta:
            expires_at = datetime.utcnow() + expires_delta
        else:
            expires_at = datetime.utcnow() + timedelta(minutes=15)
    if isinstance(expires_at, datetime):
        expire_ts = int(expires_at.timestamp())
    else:
        expire_ts = int(expires_at)

    if not access_token:
        to_encode = data.copy()
        to_encode.update({"exp": expire_ts})
        encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.TOKEN_ENCRYPT_ALGORITHM)
        access_token = encoded_jwt

    user_uid = data["sub"]
    user = users_crud.get_user_by_uid(db, user_uid)

    db_token = models.Token(
        access_token=access_token,
        id_token=id_token,
        expiration=expire_ts,
        user=user,
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token.access_token


def get_token(
        db: database.Session,
        access_token: str,
        ):
    try:
        token = db.query(models.Token).filter(models.Token.access_token == access_token).first()
    except Exception as e:  # Intended for handling a queue pool limit exception
        logger.warning(str(e))
        db.close()
        engine = database.get_engine(
                config.DATABASE_URL,
                config.DB_CONNECT_ARGS,
                config.DB_ENGINE_KWARGS,
                )
        db = database.Session(engine)
        token = db.query(models.Token).filter(models.Token.access_token == access_token).first()

    return token


def get_tokens_by_user(
        db: database.Session,
        user: users_models.User,
        ):
    tokens = db.query(models.Token).filter(models.Token.user == user)
    return tokens


def delete_token(
        db: database.Session,
        access_token: str,
        ):
    token = get_token(db, access_token)
    if not token:
        return
    db.delete(token)
    db.commit()


def get_user_from_token(db, token):
    try:
        token = get_token(db, token)
        if not token:
            return None
        payload = jwt.decode(
                token.access_token,
                config.SECRET_KEY,
                algorithms=[config.TOKEN_ENCRYPT_ALGORITHM],
                )
        user_uid: str = payload.get("sub")
        if user_uid is None or time.time() >= token.expiration:
            return None
        token_data = schemas.TokenData(user_uid=user_uid)
    except JWTError:
        return None
    uid = token_data.user_uid
    return users_crud.get_user_by_uid(db, uid)

