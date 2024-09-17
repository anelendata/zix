import uuid
import datetime
from sqlalchemy import (
    Table, Boolean, Column, DateTime, ForeignKey, Integer,
    String, JSON, and_, or_, not_
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, contains_eager, lazyload, joinedload,selectinload
from sqlalchemy.sql.expression import bindparam
from sqlalchemy_utils import UUIDType


class BaseModel(object):
    def __tablename__(self):
        return self.__name__.lower()

    # Use id (primary key) for internal reference instead of uid
    # for better performance and sorting
    id = Column(Integer, primary_key=True)

    # Use uid as a public identifier
    # Note: do binary=True, native=True on Postgres for better performance
    uid = Column(UUIDType(binary=False, native=False), default=uuid.uuid4)

    created_at = Column(
            DateTime,
            default=datetime.datetime.utcnow
            )

    updated_at = Column(
            DateTime,
            default=datetime.datetime.utcnow,
            onupdate=datetime.datetime.utcnow,
            )

Base = declarative_base(cls=BaseModel)
