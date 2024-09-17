import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from zix.server import logging, utils
from zix.server.database import Session, get_db

import config
from . import crud, models, schemas
from fastapi import APIRouter
router = APIRouter()

from plugins.subscriptions import crud as subscriptions_crud, schemas as subscriptions_schemas

logger = logging.get_logger(logger_name=__name__)

UserPublic = schemas.UserPublic
UserPrivate = schemas.UserPrivate
UserEnrichedPrivate = schemas.UserEnrichedPrivate
if config.USE_SUBSCRIPTIONS:
    UserPrivate = subscriptions_schemas.UserPrivate
    UserEnrichedPrivate = subscriptions_schemas.UserEnrichedPrivate

@router.post(config.API_PATH + "/users/", response_model=UserPrivate)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    ):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = crud.create_user_and_account(db, user)
    return new_user


@router.get(config.API_PATH + "/users/", response_model=List[UserPublic])
def read_users(
    email: str,
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.UserPrivate = Depends(crud.get_current_active_user),
    db: Session = Depends(get_db),
    ):
    if email:
        unencoded_email = base64.b64decode(email).decode("utf-8")
        user = crud.get_user_by_email(db, unencoded_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with {unencoded_email} not found")
        return [user]
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get(config.API_PATH + "/users/{user_uid}", response_model=UserPublic)
def read_user(
    user_uid: str,
    current_user: UserPrivate = Depends(crud.get_current_active_user),
    db: Session = Depends(get_db),
    ):
    db_user = crud.get_user_by_uid(db, user_uid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get(
    config.API_PATH + "/users/me/",
    response_model=UserEnrichedPrivate,
)
async def read_users_me(
    current_user: UserPrivate = Depends(crud.get_current_active_user),
    db: Session = Depends(get_db),
    psid=None,
    ):
    if psid:
        _update_subscription_status(db, current_user, psid)

    account = current_user.account
    if not account:
        # Logging as error to get oncall's attention.
        logger.error(f"User {current_user.uid} 's account doesn't exist. Suspect an account creation error upon signup or accidential account deletion. Since the user has been authenticated, I am creating one.")

        db_account = models.Account(
            is_organization = False,
        )
        account = crud.create_account(db, db_account, current_user)

    current_user.invitation_codes = crud.get_invitation_codes_by_user(db, current_user)

    if config.USE_SUBSCRIPTIONS:
        subs = subscriptions_crud.get_feature_subscriptions_by_account(
            db,
            account,
            include_canceled=False,  # Cancelation date is not until the end of the current period.
        )
        subs = subscriptions_crud.filter_latest_only_per_feature(subs)

        current_user.payment_plans = []
        if config.USE_PAYMENTS:
            current_user.payment_plans = subscriptions_crud.get_eligible_payment_plans(db, account)
            # If expired, check with Payment platform to see if subscription is renewed
            subs = subscriptions_crud.update_subscriptions(db, subs)

        if len(subs) == 0:
            subs = subscriptions_crud.apply_trial_plan(db, account)

        current_user.feature_subscriptions = subs

    return current_user


@router.get(config.API_PATH + "/users/me/settings")
def get_user_settings(
    current_user: UserPrivate = Depends(crud.get_current_active_user),
    db: Session = Depends(get_db),
    ):
    return current_user.account


@router.get(config.API_PATH + "/users/me/notifications")
def get_user_notifications(
    current_user: UserPrivate = Depends(crud.get_current_active_user),
    db: Session = Depends(get_db),
    ):
    return []
