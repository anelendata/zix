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


class Account(Base):
    __tablename__ = "account"

    # Human-defined unique name besides uid
    handle = Column(String, unique=True, index=True)

    first_name = Column(String, default=None)
    last_name = Column(String, default=None)
    profile_pic_url = Column(String, default=None)

    # This is used for user account only, not organization
    # One to one (User is the parent)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="account")

    # Indication of the owner for both personal and organization accounts
    owner_user_uid = Column(UUIDType(binary=False, native=False), default=None)

    is_organization = Column(Boolean, default=False)
    memberships = relationship("Membership", back_populates="organization")

    invitation_codes = relationship("InvitationCode", back_populates="owner")
    invitations = relationship("Invitation", back_populates="inviter")

    # Uncomment this to activate bidirectional relationship
    # Depends on plugins/subscriptions
    # feature_subscriptions = relationship("FeatureSubscription", back_populates="account")

    @hybrid_property
    def profile_picture_url(self):
        if self.profile_pic_url:
            return self.profile_pic_url
        email_md5 = hashlib.md5(self.user.email.encode("utf-8")).hexdigest()
        return f"https://gravatar.com/avatar/{email_md5}"

    @hybrid_property
    def name(self):
        name = self.first_name
        if self.last_name:
            name = name + " " + self.last_name
        return name


class User(Base):
    __tablename__ = "user"

    email = Column(EmailType, unique=True, index=True)

    # hashed_password is not stored currently as we do authentication via auth0
    # hashed_password = Column(String)

    # Avoid the user to login using different methods (e.g. Google vs. email/password)
    auth_app_user_uid = Column(String)

    is_staff = Column(Boolean, default=False)
    activated_at = Column(DateTime, default=None)
    deactivated_at = Column(DateTime, default=None)
    last_login = Column(DateTime, default=None)
    last_seen = Column(DateTime, default=None)

    # One to one (User is the parent)
    # uselist=False for one-to-one relationship
    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-one
    account = relationship("Account", back_populates="user", uselist=False)

    memberships = relationship("Membership", back_populates="user")

    # Uncomment this to activate bidirectional relationship
    # Depends on plugins/subscriptions
    # payments = relationship("Payment", back_populates="payer")

    @hybrid_property
    def is_active(self):
        now = datetime.datetime.utcnow()
        return (self.activated_at <= now and (self.deactivated_at is None or now < self.deactivated_at))


class Membership(Base):
    __tablename__ = "membership"

    status = Column(String, default="pending")
    role = Column(String, default="viewer")  # owner, admin, editor, viewer

    # Organization is also Account, so we use User model to identify the member
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="memberships")

    organization_id = Column(Integer, ForeignKey("account.id"))
    organization = relationship("Account", back_populates="memberships")

    @hybrid_property
    def user_profile_pic_url(self):
        return self.user.account.profile_picture_url


class Invitation(Base):
    __tablename__ = "invitation"

    email = Column(EmailType, index=True)
    inviter_id = Column(Integer, ForeignKey('account.id'))
    inviter = relationship("Account", back_populates="invitations")
    invitation_code_id = Column(Integer, ForeignKey("invitation_code.id"))
    invitation_code = relationship("InvitationCode", back_populates="invitations")
    expire_at = Column(DateTime, default=None)


class InvitationCode(Base):
    __tablename__ = "invitation_code"
    code = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("account.id"))
    owner = relationship("Account", back_populates="invitation_codes")
    # quota=None means unlimited invitation
    quota = Column(Integer, default=None)
    num_claimed = Column(Integer, default=0)
    # After code_expire_at, this InvitationCode should not be used
    code_expire_at = Column(DateTime, default=None)
    # Seconds before the invitation expires once it's issued
    invitation_expire_sec = Column(Integer, default=None)
    invitations = relationship("Invitation", back_populates="invitation_code")
