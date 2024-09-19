import datetime
import uuid
from typing import List, Optional

from zix.server.schemas import BaseModel


class UserPublic(BaseModel):
    pass


class UserPrivate(BaseModel):
    email: str


class UserCreate(UserPrivate):
    pass


class UserModify(BaseModel):
    email: Optional[str] = None


class OrganizationPublic(BaseModel):
    name: Optional[str] = None
    profile_pic_url: Optional[str] = None


class MembershipPublic(BaseModel):
    organization: OrganizationPublic


class AccountPublic(BaseModel):
    handle: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_organization: bool = False
    profile_pic_url: Optional[str] = None
    memberships: List[MembershipPublic]  = []


class MembershipPrivate(BaseModel):
    role: str
    status: str
    organization: OrganizationPublic


class MembershipCreate(MembershipPrivate):
    organization_uid: str
    user_uid: Optional[str] = None
    role: str = "member"


class MembershipModify(BaseModel):
    role: str
    status: str


class AccountPrivate(BaseModel):
    handle: str = None
    name: str = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_organization: bool
    profile_picture_url: Optional[str] = None
    memberships: List[MembershipPrivate]  = []


class AccountModify(BaseModel):
    handle: str = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_organization: bool = False
    profile_pic_url: Optional[str] = None


class AccountCreate(BaseModel):
    handle: str
    first_name: Optional[str]
    last_name: Optional[str] = None
    is_organization: bool = False
    profile_pic_url: Optional[str] = None


class AppTokenSecret(BaseModel):
    app: str
    token_obj: dict
    expire_on: Optional[datetime.datetime] = None


class InvitationCodeBase(BaseModel):
    code: str
    quota: Optional[int] = None
    num_claimed: Optional[int] = 0
    code_expire_at: Optional[datetime.datetime] = None


class InvitationCode(InvitationCodeBase):
    created_at: datetime.datetime


class UserEnrichedPrivate(UserPrivate):
    account: AccountPrivate
    invitation_codes: List[InvitationCode] = []
