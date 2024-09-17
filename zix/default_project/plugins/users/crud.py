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


logger = logging.get_logger(logger_name=__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        access_token = encoded_jwt

    user_uid = data["sub"]
    user = get_user_by_uid(db, user_uid)

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
        user: models.User,
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



async def get_current_user(
        request: Request,
        db: database.Session = Depends(database.get_db),
        token = Depends(oauth2_scheme),
    ):
    if not isinstance(token, str):
        raise credentials_exception

    user = None
    if isinstance(request.user, SimpleUser) and request.user.is_authenticated:
        # Already authenticated via OAuth (Auth0)
        email = request.user.display_name
        user = get_user_by_email(db, email)

        if not user:
            raise HTTP_401_UNAUTHORIZED(detail=f"User with email {email} does not exist")

        if user.is_staff and os.environ.get("LOGIN_AS"):  # and config.is_local():
            # This is for admin to login as another user
            user = get_user_by_email(db, os.environ.get("LOGIN_AS"))
            logger.warning("Logging in as " + os.environ.get("LOGIN_AS"))
        elif user:
            # Record the last_seen in the regular flow
            user.last_seen = datetime.utcnow()
            db.add(user)
            db.commit()
            db.refresh(user)

        if user:
            return user
        logger.debug(f"User {email} is not registered.")
        # Redirect to registration page?

    logger.debug("Trying the traditional login")
    user = _get_user_from_token(db, token)
    if user is None:
        raise credentials_exception
    return user

    data = user.__dict__
    data["profile_url"] = f"https://gravatar.com/avatar/{email_md5}"
    return data


async def get_current_active_user(
        current_user: schemas.UserPrivate = Depends(get_current_user),
        db: database.Session = Depends(database.get_db),
        ):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


def update_user(
        db: database.Session,
        user: schemas.UserModify,
        ):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_account(
    db: database.Session,
    account: schemas.AccountModify,
    ):
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def create_account(
        db: database.Session,
        account: schemas.AccountCreate,
        owner: schemas.UserPublic,
        ):
    db_account = models.Account(
        handle=account.handle,
        first_name=account.first_name,
        last_name=account.last_name,
        is_organization=account.is_organization,
        owner_user_uid=owner.uid,
        profile_pic_url = account.profile_pic_url
    )

    account = update_account(db, db_account)
    if db_account.is_organization == False:
        db_account.user = owner
        owner.account = account
        update_user(db, owner)

    # db_campaign = create_campaign(db, db_account, "default")
    # db_campaign_subscription = create_campaign_subscription(
    #    db,
    #    db_campaign,
    #    db_account,
    #    status="active"
    #)

    return account


def get_admin_account(
        db: database.Session,
        ):
    account_handle = config.ADMIN_ACCOUNT_HANDLE
    return get_account_by_handle(db, account_handle)


def get_accounts(
        db: database.Session,
        offset: int = 0,
        limit: int = 100,
        ):
    return db.query(models.Account).offset(offset).limit(limit).all()


def get_account_by_uid(
        db: database.Session,
        uid: str,
        ):
    return db.query(models.Account).filter(
        models.Account.uid == uid).first()


def get_account_by_handle(
    db: database.Session,
    handle: str,
    ):
    return db.query(models.Account).filter(models.Account.handle == handle).first()


def validate_user_account_access(db, user, account_uid):
    status = None
    role = None
    if isinstance(account_uid, str):
        try:
            account_uid = uuid.UUID(account_uid)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid UID: {account_uid}")
    if account_uid and user.account.uid !=  account_uid:
        account = get_account_by_uid(db, account_uid)
        if not account:
            logger.warning(f"Account {account_uid} not found")
            raise HTTPException(status_code=404, detail="Account not found")
        status, role = get_membership_status_role(db, user, account)
        if not status or status in ["pending", "suspended", "deleted"]:
            logger.warning(f"User account {user.account.uid} does not have permission to access to Account {account_uid}")
            raise HTTPException(status_code=404, detail="Account not found")
    else:
        account = user.account
        status = "active"
        role = "owner"
    return account, status, role


def get_unique_account_handle(
    db: database.Session,
    handle: str,
    ):
    count = 0
    max_retry = 100
    handle_base = handle
    while len(handle) < 3 or (get_account_by_handle(db, handle) is not None and count < max_retry):
        count += 1
        handle = f"{handle_base}0{count}"

    if max_retry <= count:
        raise Exception("Could not come up with an unique handle in 100 iterations")
    return handle

def create_user_and_account(
    db: database.Session,
    user: schemas.UserCreate,
    ):
    db_user = models.User(
        email=user.email.lower(),
    )
    db_user = update_user(db, db_user)

    db_account = models.Account(
        is_organization = False,
    )
    db_account = create_account(db, db_account, db_user)
    db_user.account = db_account

    return db_user


def get_users(
        db: database.Session,
        offset: int = 0,
        limit: int = 100,
        ):
    return db.query(models.User).offset(offset).limit(limit).all()


def get_user(
        db: database.Session,
        user_id: int,
        ):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_uid(
        db: database.Session,
        uid: Union[str, uuid.UUID],
        ):
    if isinstance(uid, str):
        uid = uuid.UUID(uid)
    return db.query(models.User).filter(models.User.uid==uid).first()


def get_user_by_email(
        db: database.Session,
        email: str,
        ):
    email = email.lower()
    return db.query(models.User).filter(models.User.email == email).first()


def get_invitations_by_email(
        db: database.Session,
        invitee_email,
        ):
    invitee_email = invitee_email.lower()
    # Allow to create invitations from differnt people to track the social network
    invitations = db.query(models.Invitation).filter(
        models.Invitation.email == invitee_email,
        or_(models.Invitation.expire_at == None,
            datetime.utcnow() < models.Invitation.expire_at,
        ),
    )
    return invitations


def get_or_create_invitation(
        db: database.Session,
        invitee_email,
        inviter: schemas.AccountPublic,
        invitation_code: models.InvitationCode = None,
        ):
    invitee_email = invitee_email.lower()
    # Allow to create invitations from differnt people to track the social network
    invitation = db.query(models.Invitation).filter(
        models.Invitation.email == invitee_email,
        models.Invitation.inviter == inviter,
        or_(models.Invitation.expire_at == None,
            datetime.utcnow() < models.Invitation.expire_at,
        ),
    )

    if invitation_code:
        invitation = invitation.filter(models.Invitation.invitation_code == invitation_code)

    invitation = invitation.first()
    if invitation:
        return invitation

    expire_at = None
    if invitation_code and invitation_code.invitation_expire_sec:
        expire_at = datetime.utcnow() + timedelta(
                seconds=invitation_code.invitation_expire_sec)
    db_invitation = models.Invitation(
        email=invitee_email,
        inviter=inviter,
        invitation_code=invitation_code,
        expire_at=expire_at,
    )
    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)
    return db_invitation


def get_invitation_code(
    db: database.Session,
    code: str,
    ):
    invitation_code = db.query(models.InvitationCode).filter(
        models.InvitationCode.code == code,
    )
    return invitation_code.first()


def get_invitation_codes_by_user(
    db: database.Session,
    user,
    ):
    invitation_code = db.query(models.InvitationCode).filter(
        models.InvitationCode.owner == user,
        or_(models.InvitationCode.code_expire_at == None,
                     models.InvitationCode.code_expire_at > datetime.utcnow(),
        ),
        or_(models.InvitationCode.quota == None,
                     models.InvitationCode.quota > models.InvitationCode.num_claimed,
        ),
    ).order_by(models.InvitationCode.created_at.desc())
    return invitation_code.all()


def get_invitation_codes_by_payment_plan(
    db: database.Session,
    payment_plan,
    ):
    invitation_codes = db.query(models.InvitationCode).filter(
        models.InvitationCode.payment_plan == payment_plan,
    )
    return invitation_codes


def claim_invitation(
    db: database.Session,
    invitee_email: str,
    invitation_code: str,
    ):
    invitation_code = get_invitation_code(db, invitation_code)
    if not invitation_code:
        raise Exception("Invalid invitation code")
    if invitation_code.quota is not None and invitation_code.quota <= invitation_code.num_claimed:
        raise Exception("Max invitation has reached for this code")
    if invitation_code.code_expire_at is not None and invitation_code.code_expire_at <= datetime.utcnow():
        raise Exception("This invitation code has been expired.")
    inviter = invitation_code.owner
    invitation = get_or_create_invitation(
        db,
        invitee_email,
        inviter,
        invitation_code,
    )
    invitation_code.num_claimed += 1
    db.add(invitation_code)
    db.commit ()
    return invitation
