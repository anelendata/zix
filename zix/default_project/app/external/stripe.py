import os
import stripe

from zix.server import logging

logger = logging.get_logger(logger_name=__name__)


# It's called api key but actually requires secret
stripe.api_key = os.environ.get("STRIPE_API_SECRET")


def get_or_create_customer(user, test_clock=None):
    if test_clock:
        logger.info(f"Test clock {test_clock}")

    response = stripe.Customer.list(
        email=user.email,
        test_clock=test_clock,
        )
    customers = response.get("data", [])
    if len(customers) > 0:
        if len(customers) > 1:
            logger.warning(f"Found more than one Stripe customer for user {user.uid}")
        customer = customers[0]
    else:
        customer = stripe.Customer.create(
            email=user.email,
            test_clock=test_clock,
        )
    return customer


def create_checkout_session(
    customer_id,
    price_id,
    success_url,
    cancel_url,
    metadata,
    ):
    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            },
        ],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        customer_update={"address":"auto"},
        automatic_tax={"enabled": True},
        metadata=metadata,
    )
    return checkout_session


def get_session(session_id):
    return stripe.checkout.Session.retrieve(session_id)


def get_customer(customer_id):
    return stripe.Customer.retrieve(customer_id)


def get_subscription(subscription_id):
    return stripe.Subscription.retrieve(subscription_id)


def create_portal_session(customer_id, return_url):
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session
