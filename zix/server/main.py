import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette_context import plugins as  starlette_plugins
from starlette_context.middleware import RawContextMiddleware

from . import database, logging, utils


LOGGER = logging.get_logger(logger_name=__name__)

# dynamic imports from external directries
CURRENT_DIR =  os.path.join(os.getcwd())
config = utils.dynamic_import(CURRENT_DIR, "config")
# plugins = utils.dynamic_import(CURRENT_DIR, "plugins")
plugins = utils.import_submodules(CURRENT_DIR, "plugins")

MIDDLEWARE= [
    Middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    Middleware(
        RawContextMiddleware,
        plugins=(
            starlette_plugins.RequestIdPlugin(),
            starlette_plugins.CorrelationIdPlugin()
        ),
    ),

    Middleware(
        SessionMiddleware,
        secret_key=config.SECRET_KEY
    ),
]

if config.USE_AUTH0:
    from zix.server import auth0
    from plugins.users import crud as users_crud
    class AuthBackend(auth0.OpenIDAuthBackend):
        def get_token(self, access_token):
            db = next(database.get_db())
            token = users_crud.get_token(db, access_token=access_token)
            if token:
                return token.id_token
            return None

    MIDDLEWARE.append(Middleware(
        AuthenticationMiddleware,
        backend=AuthBackend(),
        )
    )


# Initialize the FastAPI app
app = FastAPI(
        middleware=MIDDLEWARE,
        docs_url=config.DOCS_URL,
        redoc_url=config.REDOC_URL,
        )

if config.DATABASE_URL:
    engine = database.get_engine(
        config.DATABASE_URL,
        config.DB_CONNECT_ARGS,
        config.DB_ENGINE_KWARGS,
        )


# Register plugin routers
plugin_modules = utils.list_submodules(plugins)
for module_name in plugin_modules.keys():
    LOGGER.info(f"Plugin {module_name} has been registered.")
    if hasattr(plugin_modules[module_name], "router"):
        router = getattr(plugin_modules[module_name], "router")
    elif hasattr(plugin_modules[module_name], "routers"):
        routers = getattr(plugin_modules[module_name], "routers")
        router = getattr(routers, "router")
    else:
        continue
    app.include_router(router)
    LOGGER.info(f"Routing {module_name} has been registered.")

# Mount static files. You should replace the static file path with CDN in production.
app.mount(
    "/assets",
    StaticFiles(directory=config.STATIC_DIR + "/assets"),
    name="static",
)
LOGGER.info(f"Mounted /assets to {config.STATIC_DIR}/assets")


# Mount static files. You should replace the static file path with CDN in production.
app.mount(
    "/",
    StaticFiles(directory=config.STATIC_DIR, html=True),
    name="static",
)
LOGGER.info(f"Mounted / to {config.STATIC_DIR}")
