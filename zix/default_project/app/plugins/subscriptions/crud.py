import datetime
import re
import uuid
from typing import Any, Optional, Union
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from starlette.authentication import SimpleUser
from jose import jwt

from zix.server import database, logging

import config
from . import models, schemas

from plugins.users import crud as users_crud


logger = logging.get_logger(logger_name=__name__)


def get_feature_by_name(
    db: database.Session,
    name):
    feature = db.query(models.Feature).filter(
        models.Feature.name == name,
    ).first()
    return feature


def get_or_create_feature(
    db: database.Session,
    name):
    feature = get_feature_by_name(db, name)
    if not feature:
        feature = models.Feature(name=name)
        db.add(feature)
        db.commit()
        db.refresh(feature)
    return feature


def create_feature_subscription(
        db: database.Session,
        account,
        feature_name,
        start_on,
        end_on,
        payment=None,
    ):
    feature = get_feature_by_name(db, feature_name)
    sub = models.FeatureSubscription(
        account=account,
        feature=feature,
        start_on=start_on,
        end_on=end_on,
        payment=payment,
    )

    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def get_feature_subscriptions(
        db: database.Session,
        include_trials=False,
        include_grandfather=False,
        include_test=False,
        include_canceled=False,
    ):
    """
    Note: include_canceld=False still includes the subscriptions with a future cancellation date
    """
    subs = db.query(models.FeatureSubscription).join(models.Payment, models.FeatureSubscription.payment_id == models.Payment.id)

    subs = subs.options(
       joinedload(models.FeatureSubscription.payment),
    )

    if not include_canceled:
        subs = subs.filter(
            or_(models.FeatureSubscription.canceled_on == None,
                datetime.datetime.utcnow() < models.FeatureSubscription.canceled_on
            ),
        )
    excluded_payment_plans = []
    if not include_trials:
        excluded_payment_plans.append(config.TRIAL_PAYMENT_PLAN)
    subquery = db.query(models.PaymentPlan.id).filter(
        database.not_(models.PaymentPlan.name.in_(excluded_payment_plans)))
    if not include_test:
        subquery.filter(database.not_(models.PaymentPlan.is_test))
    subquery = subquery.subquery()

    subs = subs.filter(models.Payment.plan_id.in_(subquery))

    return subs.all()


def get_feature_subscriptions_by_account(
        db: database.Session,
        account,
        include_canceled=False,
    ):
    """
    Note: include_canceld=False still includes the subscriptions with a future cancellation date
    """
    subs = db.query(models.FeatureSubscription).filter(
        models.FeatureSubscription.account == account,
    )
    if not include_canceled:
        subs = subs.filter(
            or_(models.FeatureSubscription.canceled_on == None,
                datetime.datetime.utcnow() < models.FeatureSubscription.canceled_on
            ),
        )

    subs = subs.options(
        joinedload(models.FeatureSubscription.payment)
    )
    return subs.all()


def filter_latest_only_per_feature(subs):
    """Return only the latest from each feature"""
    if len(subs) > 1:
        latests = dict()
        for s in subs:
            if (latests.get(s.feature_id) is None or
                latests[s.feature_id].update_at <= s.update_at):
                latests[s.feature_id] = s
        subs = list(latests.values())
    return subs


def update_subscriptions(db, subscriptions):
    """
    When the current subscription period ends, we want to check with Stripe
    for renewal. If renewed, update our subscriptions as well.
    """
    need_commit = False
    sub_issue_emails = []
    for s in subscriptions:
        if s.payment.app_transaction_id and (not s.is_active or s.payment.status not in models.PAYMENT_NON_ISSUE_STATUS_LIST):
            stripe_sub = None
            logger.debug(f"Getting Stripe info for subscription {s.id}")
            try:
                stripe_sub = stripe.get_subscription(s.payment.app_transaction_id)
            except Exception as e:
                logger.debug(f"Stripe error for subscription {s.uid} {str(e)}")
                continue
            if s.payment.status != stripe_sub.status:
                s.payment.status = stripe_sub.status
                db.add(s)
                need_commit = True
                logger.debug(f"Updating Stripe info for subscription {s.id}")

                # Email once if there is a problem
                if stripe_sub.status in models.PAYMENT_ISSUE_STATUS_LIST:
                    email = {
                        "email": s.account.user.email,
                        "name": s.account.first_name + " " + s.account.last_name,
                        "subject": "Issue with your subscription payment",
                        "content": f"<p>Hi {s.account.first_name},<br><br></p><p>We had an issue with your credit card payment.<br><br></p><p>The credit card may have been expired or payment may have been declined by the issuing bank. (Banks do not share much detail on their reasoning behind these declines.)<br><br></p><p>To continue using OmniCreator, log in and follow the link to Stripe to check your payment status. Please contact your bank or try another credit card if necessary.<br><br></p><p>Let us know if you have any questions.<br><br></p><p>Sincerely,<br>OmniCreator Team</p>",
                    }
                    sub_issue_emails.append(email)

            if s.payment.paid_at != stripe_sub.current_period_start:
                s.payment.paid_at = datetime.datetime.utcfromtimestamp(stripe_sub.current_period_start)
                db.add(s)
                need_commit = True
                logger.debug(f"Updating paid_at for subscription {s.id}")
            if (stripe_sub.current_period_start != s.start_on or
                stripe_sub.current_period_end != s.end_on):
                stripe_start_on = datetime.datetime.utcfromtimestamp(stripe_sub.current_period_start)
                if s.start_on is None or (stripe_start_on < s.start_on):
                    s.start_on = stripe_start_on
                s.end_on = datetime.datetime.utcfromtimestamp(stripe_sub.current_period_end)
                db.add(s)
                need_commit = True
                logger.debug(f"Updating start_on for subscription {s.id}")
            if stripe_sub.canceled_at:
                # To be safe, we set canceled on at the end of this
                # billing period, not the date the user took the cancellation action
                s.canceled_on = datetime.datetime.utcfromtimestamp(stripe_sub.current_period_end)
                db.add(s)
                need_commit = True
                logger.debug(f"Updating canceled_at for subscription {s.id}")
    if need_commit:
        db.commit()

    if len(sub_issue_emails) > 0:
        try:
            sendgrid.send_emails(sub_issue_emails)
        except Exception as e:
            logger.error(e)

    return subscriptions


def apply_trial_plan(db, account):
    invitations = users_crud.get_invitations_by_email(db, account.user.email).all()
    trial_days = 0
    for invitation in invitations:
        if invitation.invitation_code.trial_days > trial_days:
            trial_days = invitation.invitation_code.trial_days
    if trial_days < 1:
        trial_days = config.FREE_TRIAL_DEFAULT_DAYS

    subs = []
    subs_and_canceled = get_feature_subscriptions_by_account(db, account, include_canceled=True)
    if (len(subs_and_canceled) == 0):
        payment_plan = get_payment_plan_by_name(db, config.TRIAL_PAYMENT_PLAN)
        if not payment_plan:
            core_feature = get_or_create_feature(db, config.DEFAULT_FEATURE_NAME)
            payment_plan = models.PaymentPlan(
                name=config.TRIAL_PAYMENT_PLAN,
                description=config.TRIAL_PAYMENT_PLAN_DESCRIPTION,
                enabled_features=[core_feature],
                is_test=config.IS_TEST,
                invitation_only=False,
                platform_name=None,
            )
            core_feature.payment_plans.append(payment_plan)
            db.add(payment_plan)
            db.commit()
            db.refresh(payment_plan)

        dummy_payment = create_payment(db, payment_plan, account.user)
        start_on = datetime.datetime.utcnow()
        end_on = start_on + datetime.timedelta(days=trial_days)
        if account.user.email == config.ADMIN_EMAIL:
            end_on = None
        sub = create_feature_subscription(
                db,
                account,
                config.DEFAULT_FEATURE_NAME,
                start_on=start_on,
                end_on=end_on,
                payment=dummy_payment,
                )
        subs = [sub]
    return subs


def get_payment_plan_by_name(
        db: database.Session,
        name,
    ):
    plan = db.query(models.PaymentPlan).filter(
        models.PaymentPlan.name == name,
    ).first()
    return plan


def get_payment_plan_by_app_price_id(
        db: database.Session,
        app_price_id,
    ):
    plan = db.query(models.PaymentPlan).filter(
        models.PaymentPlan.app_price_id == app_price_id,
    ).first()
    return plan


def get_effective_payment_plans(
        db: database.Session,
        is_organization_plan=False,
        effective_on=None,
        exclude=[],
        is_test=None,
        ):
    """
    This pulls generally available features only
    """
    if is_test is None:
        is_test = config.IS_TEST

    if effective_on is None:
        effective_on = datetime.datetime.utcnow()

    plans = db.query(models.PaymentPlan).filter(
        models.PaymentPlan.is_organization_plan == is_organization_plan,
        or_(models.PaymentPlan.effective_since == None,
            models.PaymentPlan.effective_since <= effective_on),
        or_(models.PaymentPlan.expire_on == None,
            models.PaymentPlan.expire_on > effective_on),
        models.PaymentPlan.is_test == is_test,
        models.PaymentPlan.invitation_only == False,
        models.PaymentPlan.name.not_in(exclude),
    )
    plans = plans.options(
            joinedload(models.PaymentPlan.enabled_features)
            )
    return plans


def get_effective_payment_plans_for_account(
        db: database.Session,
        account,
        exclude=[],
        is_test=None,
        ):
    """
    This pulls generally available features only
    """
    return get_effective_payment_plans(
        db,
        is_organization_plan=account.is_organization,
        effective_on=account.created_at,
        exclude=exclude,
        is_test=is_test,
    )


def get_eligible_payment_plans(db, account, is_test=config.IS_TEST):
    plans = get_effective_payment_plans_for_account(
        db,
        account,
        exclude=[config.TRIAL_PAYMENT_PLAN],
        is_test=is_test,
    ).all()
    if (len(plans) == 0 or len(plans) > 2):
        logger.error(f"Found {len(plans)} payment plans")
    cycles = [plan.billing_cycle for plan in plans]
    if not (models.BILLING_CYCLE["monthly"] in cycles and
            models.BILLING_CYCLE["annual"] in cycles):
        logger.error("We should have one annual and one montly billing cycle")
    return plans


def create_payment(
        db: database.Session,
        payment_plan,
        payer,
        status: str = None,
        paid_at: datetime.datetime = None,
        app_customer_id: str = None,
        app_transaction_id: str = None,
        app_metadata: dict = None,
        is_test:bool = None,  # This is for overwriting the default behavior
        ):
    if is_test is None:
        is_test = config.IS_TEST or payment_plan.is_test

    payment = models.Payment(
        plan=payment_plan,
        is_test=is_test,
        payer=payer,
        status=status,
        paid_at=paid_at,
        app_customer_id=app_customer_id,
        app_transaction_id=app_transaction_id,
        app_metadata=app_metadata,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
