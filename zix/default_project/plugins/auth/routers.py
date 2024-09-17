import datetime
import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.responses import RedirectResponse

from zix.server.auth0 import oauth, logout as auth0_logout
from zix.server.database import Session, get_db
from zix.server.logging import get_logger

from . import config, schemas, router
from plugins.users import crud as users_crud, schemas as users_schemas, routers as users_routers

logger = get_logger(logger_name=__name__)


@router.get("/login")
async def login(
    request: Request,
    next: str = "/",
    ):
    auth0 = oauth.create_client("auth0")
    redirect_uri = request.url_for("callback")
    request.session["next"] = next
    return await auth0.authorize_redirect(request, str(redirect_uri))


@router.get("/callback")
async def callback(
    request: Request,
    db: Session = Depends(get_db),
    ):
    auth0 = oauth.create_client("auth0")
    white_list = [
        "mismatching_state",
    ]
    try:
        token = await auth0.authorize_access_token(request)
    except Exception as e:
        # If not in white list, create an error log
        if not any(keyword in str(e) for keyword in white_list):
            logger.error("Auth0 Error: " + str(e))
        else:
            logger.warning("Auth0 Warning: " + str(e))
        return RedirectResponse(url="/?message=Hmm...Something went wrong.<br/>Please try again. If you accessed from in-app browser, please use Safari or Chrome browser instead.")

    resp = await auth0.get("userinfo", token=token)
    userinfo = resp.json()
    email = userinfo["email"].lower()

    invitation_code = None
    code =  request.session.get("invitation_code")
    if code:
        try:
            users_crud.claim_invitation(db, email, code)
        except Exception as e:
            return RedirectResponse(url=f"/?message={str(e)} Please contact the inviter.")
        del request.session["invitation_code"]

    user = users_crud.get_user_by_email(db, email)
    # User not found. Redirect to home page
    if not user:
        if config.INVITATION_ONLY and email != config.ADMIN_EMAIL:
            invitation = users_crud.get_invitations_by_email(db, email).first()
            if not invitation:
                return RedirectResponse(url="/?message=Sorry, invitation only.&success=false")
        new_user = users_schemas.UserCreate(email=email)
        user = users_routers.create_user(new_user, db)
        if config.SENDGRID_KEY:
            try:
                sendgrid.add_onboarding_email_subscriber(email)
            except Exception as e:
                logger.error("Sendgrid Error: " + str(e))

    auth0_user_id = userinfo.get("sub", "").lower()
    if user.auth_app_user_uid:
        if user.auth_app_user_uid.lower() != auth0_user_id:
            return RedirectResponse(url=f"/?message=You used a different login method (Google vs. Email) before. Please try the one you used before. Please contact support@omnicreator.club if you have quesitions.")
    else:
        user.auth_app_user_uid = auth0_user_id
        db.add(user)
        db.commit()

    if not userinfo["email_verified"]:
        return RedirectResponse(url="/?message=Check your inbox/spam folder<br>to verify your email<br>and try again.&success=false")

    access_token = token["access_token"]
    id_token = token["id_token"]
    expires_at = token["expires_at"]

    utcnow = datetime.datetime.utcnow()
    if not user.activated_at:
        user.activated_at = utcnow

    user.last_login = utcnow
    db.add(user)
    db.commit()
    db.refresh(user)

    data = {
        "sub": str(user.uid),
    }
    users_crud.create_access_token(
        db,
        data,
        access_token=access_token,
        id_token=id_token,
        expires_at=expires_at,
        )

    request.session["access_token"] = access_token
    request.session["current_user_uid"] = str(user.uid)
    next_ = request.session.get("next", "/")
    if next_ != "/":
        del request.session["next"]
    return RedirectResponse(url=next_)


@router.get(config.API_PATH + "/logout")
@router.get("/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db),
    ):
    request.session.clear()
    return auth0_logout(request)


@router.post(config.API_PATH + "/logout/")
@router.post("/logout/")
async def logout(
    request: Request,
    current_user: users_schemas.UserPrivate = Depends(users_crud.get_current_active_user),
    db: Session = Depends(get_db),
    ):
    tokens = crud.get_tokens_by_user(db, current_user)
    for t in tokens:
        crud.delete_token(db, t.access_token)
    request.session.clear()
    return auth0_logout(request)
