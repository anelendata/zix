import uuid
from typing import Any, Optional, Union

from fastapi import Depends, HTTPException, status, Request

from zix.server import database, logging

import config
from . import models, schemas

# Use this format to import other plugin's models, crud, and schemas
from plugins.users import (
    models as users_models,
    crud as users_crud,
    schemas as users_schemas,
    )

logger = logging.get_logger(logger_name=__name__)

