import logging, json, os
from functools import wraps
from urllib import parse as urlparse

from authlib.integrations.starlette_client import OAuth

import requests
from six.moves.urllib.request import urlopen

from fastapi import Request, status
from fastapi import HTTPException

from starlette.responses import RedirectResponse
from starlette_context import context
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, SimpleUser, UnauthenticatedUser,
    AuthCredentials
)

from jose import jwt

from zix.server.database import Session, get_db

from .logging import get_logger

logger = get_logger(logger_name=__name__)


auth0_client_id = os.environ.get("AUTH0_CLIENT_ID")
auth0_client_secret = os.environ.get("AUTH0_CLIENT_SECRET")
auth0_github_client_id = os.environ.get("AUTH0_GITHUB_CLIENT_ID")
auth0_github_client_secret = os.environ.get("AUTH0_GITHUB_CLIENT_SECRET")
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")

auth0_authorization_base_url = f"https://{AUTH0_DOMAIN}/authorize"
auth0_access_token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
auth0_token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
ALGORITHM = "RS256"
API_AUDIENCE_MANAGEMENT = f"https://{AUTH0_DOMAIN}/api/v2/"
API_AUDIENCE = auth0_client_id
API_AUDIENCE_GITHUB = auth0_github_client_id

oauth = OAuth()
oauth.register(
    name="auth0",
    client_id=auth0_client_id,
    client_secret=auth0_client_secret,
    request_token_url=None,
    request_token_params=None,
    access_token_url=auth0_token_url,
    access_token_params=None,
    authorize_url=auth0_authorization_base_url,
    authorize_params=None,
    api_base_url=f"https://{AUTH0_DOMAIN}",
    client_kwargs={
        "scope": "openid profile email",
    },
)

oauth_github = OAuth()
oauth_github.register(
    name="auth0_github",
    client_id=auth0_github_client_id,
    client_secret=auth0_github_client_secret,
    request_token_url=None,
    request_token_params=None,
    access_token_url=auth0_token_url,
    access_token_params=None,
    authorize_url=auth0_authorization_base_url,
    authorize_params=None,
    api_base_url=f"https://{AUTH0_DOMAIN}",
    client_kwargs={
        "scope": "openid profile email",
    },
)


def get_github_user_info(user_id, access_token):
    payload = {
        "client_id": auth0_github_client_id,
        "client_secret": auth0_github_client_secret,
        "audience": API_AUDIENCE_MANAGEMENT,
        "grant_type": "client_credentials",
    }
    res = requests.post(
        auth0_access_token_url,
        headers={
            "content-type": "application/json"
        },
        json=payload,
    )
    data = res.json()
    res = requests.get(
        f"https://{AUTH0_DOMAIN}/api/v2/users/" + user_id,
        headers={"authorization": data["token_type"] + " " + data["access_token"]})
    return res.json()


def logout(request: Request):
    # Redirect user to logout endpoint
    params = {
            "returnTo": os.getenv("HTTP_DOMAIN"),
            # "returnTo": request.url_for("/", _external=True),
            "client_id": auth0_client_id,
            }
    url = f"https://{AUTH0_DOMAIN}/v2/logout?" + urlparse.urlencode(params)
    # url = f"https://{AUTH0_DOMAIN}/v2/logout?federated&" + urlparse.urlencode(params)
    logger.info(url)
    return RedirectResponse(url=url)


def logout_github(request: Request):
    # Redirect user to logout endpoint
    params = {
            "returnTo": os.getenv("HTTP_DOMAIN"),
            # "returnTo": request.url_for("/", _external=True),
            "client_id": auth0_github_client_id,
            }
    url = f"https://{AUTH0_DOMAIN}/v2/logout?" + urlparse.urlencode(params)
    # url = f"https://{AUTH0_DOMAIN}/v2/logout?federated&" + urlparse.urlencode(params)
    logger.info(url)
    return RedirectResponse(url=url)


# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


class OpenIDAuthBackend(AuthenticationBackend):
    def _get_token_auth_header(self, request: Request):
        """Obtains the Access Token from the Authorization Header
        """
        auth = request.headers.get("Authorization", None)

        if not auth:
            logger.debug("No Auth header found")
            return None

        parts = auth.split()

        if parts[0].lower() != "bearer":
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Authorization header must start with"
                                " Bearer"}, 401)
        elif len(parts) == 1:
            raise AuthError({"code": "invalid_header",
                            "description": "Token not found"}, 401)
        elif len(parts) > 2:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Authorization header must be"
                                " Bearer token"}, 401)

        token = parts[1]
        return token


    async def authenticate(
            self,
            request,
            ):
        """Determines if the Access Token is valid
        """
        access_token = self._get_token_auth_header(request)

        if not self.get_token:
            raise NotImplemented("Must implement get_token method")

        id_token = self.get_token(access_token)

        if not id_token:
            return

        jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        try:
            unverified_header = jwt.get_unverified_header(id_token)
        except jwt.JWTError:
            logger.debug(f"id_token: {id_token}")
            # Probably the token from the traditional login
            return

        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    id_token,
                    rsa_key,
                    algorithms=[ALGORITHM],
                    audience=API_AUDIENCE,
                    issuer="https://" + AUTH0_DOMAIN + "/"
                )
            except jwt.ExpiredSignatureError:
                return {"status": "error",
                        "exception": HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token expired. Please refresh the page.",
                            ),
                        }
            except jwt.JWTClaimsError:
                return {"status": "error",
                        "exception": HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="invalid claims (audience and issuer). "
                                   "Please contact support",
                            ),
                        }
            except Exception:
                return {"status": "error",
                        "exception": HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="invalid headeer. "
                                   "Unable to parse authentication token. "
                                   "Please contact support",
                            ),
                        }

            context.data["userinfo"] = payload
            return AuthCredentials(["authenticated"]), SimpleUser(payload["email"])

        return {"status": "error",
                "exception": HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key",
                    ),
                }
