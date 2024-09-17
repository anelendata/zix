import uuid
from pydantic import BaseModel as OrigBaseModel
from typing import Optional

class BaseModel(OrigBaseModel):
    uid: Optional[uuid.UUID] = None

    def dict(self, **kwargs):
        hidden_fields = set(
            attribute_name
            for attribute_name, model_field in self.__fields__.items()
            if model_field.field_info.extra.get("hidden") is True
        )
        kwargs.setdefault("exclude", hidden_fields)
        return super().dict(**kwargs)

    class Config:
        from_attributes = True
        orm_mode = True
