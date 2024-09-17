import datetime
from zix.server.models import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, MetaData, String, Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship


BILLING_CYCLE = {
    "one_time": 0,
    "monthly": 1,
    "annual": 2,
}

# Many to many relationship
feature_to_payment_plan_assoc = Table(
    "feature_to_payment_plan_assoc",
    Base.metadata,
    Column("feature_id", ForeignKey("feature.id")),
    Column("payment_plan_id", ForeignKey("payment_plan.id")),
)


class Feature(Base):
    __tablename__ = "feature"
    name = Column(String, unique=True)
    feature_subscriptions = relationship("FeatureSubscription", back_populates="feature")
    payment_plans = relationship(
        "PaymentPlan",
        secondary=feature_to_payment_plan_assoc,
        back_populates="enabled_features",
        cascade="all, delete",
    )


class FeatureSubscription(Base):
    __tablename__ = "feature_subscription"
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account") #, back_populates="feature_subscriptions")
    feature_id = Column(Integer, ForeignKey('feature.id'))
    feature = relationship("Feature", back_populates="feature_subscriptions")
    start_on = Column(DateTime)
    end_on = Column(DateTime, default=None)
    canceled_on = Column(DateTime, default=None)

    # This subscription is covered by the following payment
    payment_id = Column(Integer, ForeignKey('payment.id'))
    payment = relationship("Payment", back_populates="feature_subscriptions")

    @hybrid_property
    def is_active(self):
        now = datetime.datetime.utcnow()
        return (self.start_on <= now and (self.end_on is None or now < self.end_on))

    @hybrid_property
    def is_trial(self):
        return ("trial" in self.payment.plan.name.lower() or "trial" in self.payment.plan.description.lower())


class PaymentPlan(Base):
    __tablename__ = "payment_plan"
    name = Column(String, index=True, unique=True)
    is_test = Column(Boolean, default=False)
    invitation_only = Column(Boolean, default=True)
    is_organization_plan = Column(Boolean, default=False)
    billing_cycle = Column(Integer, default=None)  # 0: one_time, 1: monthly, 2: annual
    description = Column(String, default=None)
    platform_name = Column(String, default="stripe")
    platform_price_id = Column(String, unique=True, index=True, default=None)
    unit_price_cents = Column(Integer)

    # This plan is effective for the account created between effective_since and
    # expire_on
    # Use crud.feature.make_payment_plan() to ensure the integrity
    # i.e. Make sure there is no overlap between plans
    effective_since = Column(DateTime, default=None)
    expire_on = Column(DateTime, default=None)

    payments = relationship("Payment", back_populates="plan")

    # Feature subscription that corresponds to this payment plan
    enabled_features = relationship(
        "Feature",
        secondary=feature_to_payment_plan_assoc,
        back_populates="payment_plans",
    )

    @hybrid_property
    def is_active(self):
        now = datetime.datetime.utcnow()
        return (self.effective_since <= now and (self.expire_on is None or now < self.expire_on))


class Payment(Base):
    __tablename__ = "payment"
    # Feature subscriptions this payment covers
    feature_subscriptions = relationship("FeatureSubscription", back_populates="payment")

    # Corresponding payment plan
    plan_id = Column(Integer, ForeignKey('payment_plan.id'), default=None)
    plan = relationship("PaymentPlan", back_populates="payments")

    status = Column(String, default=None)

    is_test = Column(Boolean, default=False)

    # Person who made the payment for the individual or organizational account
    payer_id = Column(Integer, ForeignKey('user.id'), default=None)
    payer = relationship("User") #, back_populates="payments")
    paid_at = Column(DateTime, default=None)

    # customer ID on the payment app (e.g. stripe)
    app_customer_id = Column(String, default=None)
    # transaction ID on the payment app
    app_transaction_id = Column(String, default=None)
    # optional metadata on the payment app
    app_metadata = Column(JSON, default=None)


class InvitationCodeToPaymentPlanMap(Base):
    __tablename__ = "invitation_code_to_payment_plan_map"
    invitation_code_id = Column(Integer, ForeignKey("invitation_code.id"))
    invitation_code = relationship("InvitationCode")
    # If payment_plan isn't set, the default payment plan applies to core features
    payment_plan_id = Column(Integer, ForeignKey("payment_plan.id"))
    payment_plan = relationship("PaymentPlan") # , back_populates="invitation_codes")
