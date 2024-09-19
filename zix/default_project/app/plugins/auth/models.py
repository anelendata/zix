import datetime
import hashlib
from zix.server.models import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, MetaData, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType, UUIDType


class Token(Base):
    __tablename__ = "token"

    access_token = Column(String, unique=True, index=True)
    id_token = Column(String)
    expiration = Column(Integer, default=-1)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", backref="tokens")

    @hybrid_property
    def account_name(self):
        return self.user.account.name
