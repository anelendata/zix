import datetime
import uuid
from typing import List, Optional

from zix.server.schemas import BaseModel

from plugins.users import schemas as users_schemas

class PaymentPlan(BaseModel):
    name: str
    app_price_id: Optional[str] = None
    unit_price_cents: Optional[int] = None
    billing_cycle: Optional[int] = None
    description: Optional[str] = None


class Payment(BaseModel):
    plan: PaymentPlan
    status: Optional[str] = None


class Feature(BaseModel):
    name: str


class FeatureSubscriptionPrivate(BaseModel):
    feature: Feature
    is_active: Optional[bool] = None
    is_trial: Optional[bool] = None
    start_on: Optional[datetime.datetime] = None
    end_on: Optional[datetime.datetime] = None
    payment: Optional[Payment] = None


class UserPrivate(users_schemas.UserPrivate):
    pass


class UserEnrichedPrivate(users_schemas.UserEnrichedPrivate):
    feature_subscriptions: List[FeatureSubscriptionPrivate] = []
    payment_plans: List[PaymentPlan] = []
