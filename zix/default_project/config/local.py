import os

from zix.server.utils import str_to_bool

DOCS_URL = "/docs"
REDOC_URL = "/redoc"

APP_NAME = "zix"
IS_TEST = str_to_bool(os.environ.get("IS_TEST"))

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
