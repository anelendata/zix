import datetime
import uuid
from typing import List, Optional

from zix.server.schemas import BaseModel

# Use this format to import other plugin's models, crud, and schemas
from plugins.users import (
    models as users_models,
    crud as users_crud,
    schemas as users_schemas,
    )


class MyObjectPublic(BaseModel):
    public_info: str = None


class MyObjectPrivate(MyObjectPublic):
    # Add a private field on top of public
    private_info: str = None
