import datetime
from zix.server.models import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, MetaData, String, Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship


class MyObject(Base):
    __tablename__ = "my_model"  # Table name to be created on the database
    # uid, created_at (auto-populated), and updated_at (auto-updated) are inherited from Base
    # Add your fields below
    # Read this: https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
    name = Column(String, unique=True)
