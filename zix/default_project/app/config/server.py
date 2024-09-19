import os

DOCS_URL = None
REDOC_URL = None

IS_TEST = False
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DATABASE_NAME = os.environ.get("DATABASE")
DOMAIN = os.environ.get("DOMAIN")

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DATABASE_NAME}"

STATIC_HTTP_DOMAIN = os.getenv("STATIC_HTTP_DOMAIN")

CORS_ORIGINS = [
        "https://{DOMAIN}",
        STATIC_HTTP_DOMAIN,
]
