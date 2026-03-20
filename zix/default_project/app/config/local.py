import logging
import os

from zix.server.utils import str_to_bool

DOCS_URL = "/docs"
REDOC_URL = "/redoc"

APP_NAME = "zix"
IS_TEST = str_to_bool(os.environ.get("IS_TEST"))

SQLALCHEMY_LOG_LEVEL = os.environ.get("SQLALCHEMY_LOG_LEVEL", "INFO")
if SQLALCHEMY_LOG_LEVEL.lower() == "debug":
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)


if not os.environ.get("DB_HOST"):
    DATABASE_URL = f"sqlite:///./{APP_NAME}.db"
    # DATABASE_URL = f"sqlite+pysqlcipher://:" + os.environ.get("SQLITE_ENCRYPTION_KEY", "") +"@/./{APP_NAME}.db"
else:
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    DATABASE_NAME = os.environ.get("DATABASE")
    DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DATABASE_NAME}"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

USE_LINKEDIN_SSO = os.getenv("USE_LINKEDIN_SSO", "false").lower() == "true"
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")

USE_GITHUB_SSO = os.getenv("USE_GITHUB_SSO", "false").lower() == "true"
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

STATIC_HTTP_DOMAIN = os.getenv("STATIC_HTTP_DOMAIN")

CORS_ORIGINS = [
        "http://localhost",
        STATIC_HTTP_DOMAIN,
]
