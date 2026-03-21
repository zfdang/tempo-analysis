"""MPP (Machine Payments Protocol) client simulation.

Implements the HTTP 402 → Tempo payment → retry flow described in the spec.
In production this would make real HTTP calls.  Here we call the mock gateways
directly and simulate the challenge/response cycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from models import PaymentTrace
from tempo_payment import PaymentResult, build_and_submit_payment


@dataclass
class MppExchange:
    """Record of one 402 → payment → result cycle."""
    service_name: str
    challenge: dict[str, Any]
    payment: PaymentResult
    result: Any


def execute_paid_call(
    *,
    task_id: str,
    service_name: str,
    challenge_fn: Callable[[], dict[str, Any]],
    execute_fn: Callable[..., Any],
    execute_kwargs: dict[str, Any],
) -> MppExchange:
    """Run the full MPP payment cycle for a single service call.

    1. Get the 402 challenge from the gateway.
    2. Build and submit a Tempo payment.
    3. Call the gateway execute function (simulating the authenticated retry).
    4. Return the exchange record.
    """
    # Step 1: 402 challenge
    challenge = challenge_fn()
    auth = challenge["www_authenticate"]

    # Step 2: Tempo payment
    payment = build_and_submit_payment(
        task_id=task_id,
        receiver=auth["receiver"],
        token=auth["token"],
        amount=auth["amount"],
    )

    # Step 3: Authenticated retry → search result
    result = execute_fn(**execute_kwargs)

    return MppExchange(
        service_name=service_name,
        challenge=challenge,
        payment=payment,
        result=result,
    )


def exchange_to_payment_trace(exchange: MppExchange) -> PaymentTrace:
    """Convert an MppExchange to the response-schema PaymentTrace."""
    return PaymentTrace(
        service_name=exchange.service_name,
        token=exchange.payment.token,
        amount=exchange.payment.amount / 1_000_000,
        tx_hash=exchange.payment.tx_hash,
        receipt_id=exchange.payment.receipt_id,
    )
