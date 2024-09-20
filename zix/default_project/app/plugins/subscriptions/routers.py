import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import RedirectResponse, HTMLResponse

from zix.server import logging, utils
from zix.server.database import Session, get_db

import config
from . import crud, models, schemas
from fastapi import APIRouter
router = APIRouter()

from plugins.users import crud as users_crud, schemas as users_schemas

if config.USE_PAYMENTS:
    from external import stripe


logger = logging.get_logger(logger_name=__name__)


@router.post(config.API_PATH + "/payment/checkout/session")
def create_checkout_session(
    data: schemas.Checkout,
    current_user: users_schemas.UserPrivate = Depends(users_crud.get_current_active_user),
    db: Session = Depends(get_db),
    ):
    price_id = data.price_id
    account_uid = data.account_uid
    feature_name = data.feature_name

    if not price_id:
        raise HTTPException(status_code=400, detail="price_id is not set.")
    account_uid = account_uid or "default"

    plan = crud.payment.get_payment_plan_by_app_price_id(db, price_id)

    test_clock = config.STRIPE_TEST_CLOCK if config.IS_TEST and config.STRIPE_TEST_CLOCK else None
    try:
        customer = stripe.get_or_create_customer(
            current_user,
            test_clock=test_clock,
        )
        checkout_session = stripe.create_checkout_session(
            customer.id,
            price_id,
            success_url=config.HTTP_DOMAIN + "/payment/checkout/success?psid={CHECKOUT_SESSION_ID}",
            cancel_url=config.HTTP_DOMAIN,
            metadata={
                "account_uid": account_uid,
                "feature_name": feature_name,
                "payment_plan_name": plan.name,
            },
        )
    except Exception as e:
        logger.error(f"Failed while checking out user {current_user.uid} account {account_uid} feature {feature_name} payment plan {plan.name} {str(e)}")
        return {
            "state": "fail",
            "message": "Reason: {str(e)}",
        }
    return {
        "state": "success",
        "data": {
            "url": checkout_session.url,
        }
    }


@router.post(config.API_PATH + "/payment/portal/session")
def create_portal_session(
    current_user: users_schemas.UserPrivate = Depends(users_crud.get_current_active_user),
    db: Session = Depends(get_db),
    ):
    test_clock = config.STRIPE_TEST_CLOCK if config.IS_TEST else None
    customer = stripe.get_or_create_customer(
        current_user,
        test_clock=test_clock,
    )
    session = stripe.create_portal_session(
        customer.id,
        return_url=config.HTTP_DOMAIN,
    )
    return {
        "state": "success",
        "data": {
            "url": session.url,
        }
    }


@router.get("/payment/checkout/success", response_class=HTMLResponse)
def payment_success(
        request: Request,
        psid=None,
        ):
    if psid:
        request.session["payment_session_id"] = psid
    return RedirectResponse(config.HTTP_DOMAIN)


@router.post(config.API_PATH + "/tasks/payment/status")
def update_payment_status(
    db: Session = Depends(get_db),
    ):
    process_start = datetime.datetime.utcnow()
    # test_clock = config.STRIPE_TEST_CLOCK if config.IS_TEST else None
    subs = crud.get_feature_subscriptions(
        db,
        include_trials=False,
        include_grandfather=False,
        include_test=False,
        include_canceled=False,  # Cancelation date is not until the end of the current period.
    )
    subs = crud.payment.update_subscriptions(db, subs)

    data = len(subs)
    processed_in = (datetime.datetime.utcnow() - process_start).total_seconds()
    ret = {
        "status": "success",
        "message": f"Finished updating payment status.",
        "data": data,
        "processed_in_sec": processed_in,
    }
    logger.info(ret)
    return ret
