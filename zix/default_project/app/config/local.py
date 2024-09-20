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

STATIC_HTTP_DOMAIN = os.getenv("STATIC_HTTP_DOMAIN")

CORS_ORIGINS = [
        "http://localhost",
        STATIC_HTTP_DOMAIN,
]
