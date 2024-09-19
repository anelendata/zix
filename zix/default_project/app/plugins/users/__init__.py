# You usually don't have to change this file
from fastapi import APIRouter

import config

# Always instantiate router before importing routers submodule
from . import routers
from . import schemas
