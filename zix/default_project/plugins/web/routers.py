import os
from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.responses import HTMLResponse

from . import config, router, schemas


USE_STRIPE = False


def _page(
    request: Request,
    page="index.html",
    ):
    html_prefix = os.environ.get("HTML_PREFIX", "")
    static_http_domain = os.getenv("STATIC_HTTP_DOMAIN")
    body = None
    if html_prefix == "prod_":
        headers = {'Accept-Encoding': 'identity'}
        url = f"{static_http_domain}/prod_" + page
        r = requests.get(url, headers=headers)
        if r.status_code < 400:
            body = r.content
            if isinstance(body, bytes):
                body =body.decode()

        else:
            logger.warning(f"static URL is not working {static_http_domain}/prod_" + page)
    if not body:
        # dev or fallback
        with open(config.FRONTEND_DIR + f"/" + page, "r") as f:
            body = str(f.read())

    access_token = request.session.get("access_token")
    if access_token:
        del request.session["access_token"]
        body += f'<meta id="_data" data-token="{access_token}">'

    if USE_STRIPE:
        payment_session_id = request.session.get("payment_session_id")
        if payment_session_id:
            del request.session["payment_session_id"]
            body += f'<meta id="_data" data-psid="{payment_session_id}">'

    return HTMLResponse(body)


@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    ):
    return _page(request, "index.html")


@router.get("/stage", response_class=HTMLResponse)
def stage(
    request: Request,
    ):
    if not config.is_local():
        raise HTTPException(status_code=404, detail="Page not found")

    return _page(request, "stage_index.html")


@router.get("/admin", response_class=HTMLResponse)
def admin(
    request: Request,
    ):
    # Reject with the first admin API access
    return _page(request, "admin.html")


@router.get("/manifest.json")
def manifest():
    return config.WEB_MANIFEST
