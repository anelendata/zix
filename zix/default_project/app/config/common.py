import os
from zix.server.utils import is_plugin_active


API_VERSION = "1"
API_PATH = "/api/v" + API_VERSION

INVITATION_ONLY = False
# Referral is tracked by the invitation code.
USE_REFERRAL = False

USE_AUTH0 = os.getenv("USE_AUTH0", "false").lower() == "true"
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")

USE_GOOGLE_SSO = os.getenv("USE_GOOGLE_SSO", "true").lower() == "true"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

USE_LINKEDIN_SSO = os.getenv("USE_LINKEDIN_SSO", "false").lower() == "true"
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")

USE_GITHUB_SSO = os.getenv("USE_GITHUB_SSO", "false").lower() == "true"
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

USE_PAYMENTS = False

DEFAULT_FEATURE_NAME = "core"
TRIAL_PAYMENT_PLAN = "core-trial"
TRIAL_PAYMENT_PLAN_DESCRIPTION = "Free trial"
FREE_TRIAL_DEFAULT_DAYS = 7

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

DISABLE_ADMIN_PAGE = (os.getenv("DISABLE_ADMIN_PAGE", "False").lower() == "true")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_ACCOUNT_HANDLE = os.environ.get("ADMIN_ACCOUNT_HANDLE")

CODE_DIR, _ = os.path.split(__file__)
STATIC_DIR = os.path.join(CODE_DIR, "../static/compiled")
FRONTEND_DIR = os.path.join(CODE_DIR, "../static/compiled")
SERVER_DIR = os.path.join(CODE_DIR, "../server")

HTTP_DOMAIN = os.getenv("HTTP_DOMAIN", "")
STATIC_HTTP_DOMAIN = os.getenv("STATIC_HTTP_DOMAIN", "")

TOKEN_ENCRYPT_ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in .env/env.yml")

STRIPE_TEST_CLOCK = os.environ.get("STRIPE_TEST_CLOCK")
SENDGRID_KEY = os.environ.get("SENDGRID_KEY")

DATABASE_URL = ""
DB_CONNECT_ARGS = {}
DB_ENGINE_KWARGS = {}
if DATABASE_URL.startswith("sqlite"):
    DB_CONNECT_ARGS.update({"check_same_thread": False})
if DATABASE_URL.startswith("postgresql"):
    DB_ENGINE_KWARGS["pool_size"] = 20
    DB_ENGINE_KWARGS["max_overflow"] = 0
    DB_ENGINE_KWARGS["pool_pre_ping"] = True
    # Have not tried the following disconnect prevention methods yet
    # https://stackoverflow.com/a/60614871
    # DB_ENGINE_KWARGS["pool_recycle"] = 300
    # DB_ENGINE_KWARGS["pool_use_lifo"] = True

WEB_MANIFEST = {
    "short_name": "MyApp",
    "name": "My first app with zix",
    "icons": [
        {
            "src": f"{STATIC_HTTP_DOMAIN}/assets/img/app-icon-192.png",
            "type": "image/png",
            "sizes": "192x192"
        },
        {
            "src": f"{STATIC_HTTP_DOMAIN}/assets/img/app-icon-512.png",
            "type": "image/png",
            "sizes": "512x512"
        }
    ],
    # "id": "/?source=pwa",
    "start_url": "/",
    # "background_color": "#3367D6",
    "display": "standalone",
    "scope": "/",
    # "theme_color": "#3367D6",
    "shortcuts": [
    #    {
    #        "name": "Example shortcut 1",
    #        "short_name": "shortcut_1",
    #        "description": "Example shortcut",
    #        "url": "/shortcut?source=pwa",
    #         "icons": [{ "src": "/images/shortcut.png", "sizes": "192x192" }]
    #    }
    ],
    "description": "My first app with zix",
    "screenshots": [
        {
            "src": f"{STATIC_HTTP_DOMAIN}/assets/img/app-screen.jpg",
            "type": "image/png",
            "sizes": "540x720",
            "form_factor": "narrow"
        },
    ]
}
