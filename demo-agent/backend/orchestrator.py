"""Main orchestrator — runs the full trip planning workflow.

State machine: RECEIVED → PARSED → VALIDATED → FLIGHT_SEARCHING →
               HOTEL_SEARCHING → OPTION_SCORING → RESPONSE_READY → COMPLETED
"""

from __future__ import annotations

import uuid
from typing import Any, Callable

from audit import AuditLogger
from mock_gateways import (
    flight_search_challenge,
    flight_search_execute,
    hotel_search_challenge,
    hotel_search_execute,
)
from models import (
    ConferenceTripResponse,
    ServiceUsage,
    TaskStatus,
)
from mpp_client import MppExchange, exchange_to_payment_trace, execute_paid_call
from normalizer import normalize
from parser import ParseResult, parse_trip_request
from policy import PolicyEngine, PolicyViolation
from ranker import rank


class Orchestrator:
    def __init__(self, policy: PolicyEngine, audit: AuditLogger):
        self.policy = policy
        self.audit = audit

    def run(self, prompt: str, progress_cb: Callable[[str], None] | None = None) -> ConferenceTripResponse:
        """Execute the full trip planning workflow for a user prompt."""
        task_id = uuid.uuid4().hex[:12]
        self.audit.log_task_created(task_id, prompt)

        def _progress(msg: str) -> None:
            self.audit.log_task_status(task_id, msg)
            if progress_cb:
                progress_cb(msg)

        # ── PARSE ────────────────────────────────────────────────────────
        _progress("PARSING")
        parsed: ParseResult = parse_trip_request(prompt)

        if not parsed.ok:
            return ConferenceTripResponse(
                task_id=task_id,
                status=TaskStatus.NEEDS_CLARIFICATION,
                summary=f"I need a bit more information: {', '.join(parsed.missing_fields)}. Could you provide those details?",
                services_used=[],
                search_spend=[],
            )

        req = parsed.request
        assert req is not None

        # ── VALIDATE ─────────────────────────────────────────────────────
        _progress("VALIDATING")
        try:
            self.policy.check_trip_budget(req.budget_total_usd)
        except PolicyViolation as e:
            return ConferenceTripResponse(
                task_id=task_id,
                status=TaskStatus.SEARCH_BUDGET_EXCEEDED,
                summary=str(e),
                services_used=[],
                search_spend=[],
            )

        normalized = normalize(req)

        # ── FLIGHT SEARCH ────────────────────────────────────────────────
        _progress("FLIGHT_SEARCHING")
        services_used: list[ServiceUsage] = []
        exchanges: list[MppExchange] = []

        try:
            self.policy.authorize_call(
                task_id, "flight-search-gateway", 180000
            )
            flight_exchange = execute_paid_call(
                task_id=task_id,
                service_name="flight-search-gateway",
                challenge_fn=flight_search_challenge,
                execute_fn=flight_search_execute,
                execute_kwargs={
                    "origin": normalized.origin_airport,
                    "destinations": normalized.destination_airports,
                    "date_start": normalized.date_start,
                    "date_end": normalized.date_end,
                },
            )
            exchanges.append(flight_exchange)
            self.audit.log_service_call(task_id, flight_exchange)
            services_used.append(ServiceUsage(
                service_name="flight-search-gateway",
                service_type="flight_search",
                status="ok",
            ))
        except PolicyViolation as e:
            return ConferenceTripResponse(
                task_id=task_id,
                status=TaskStatus.PAYMENT_FAILED,
                summary=f"Flight search payment blocked: {e}",
                services_used=services_used,
                search_spend=[exchange_to_payment_trace(ex) for ex in exchanges],
            )
        except Exception as e:
            self.audit.log_error(task_id, "flight_search_failed", str(e))
            services_used.append(ServiceUsage(
                service_name="flight-search-gateway",
                service_type="flight_search",
                status="error",
            ))
            return ConferenceTripResponse(
                task_id=task_id,
                status=TaskStatus.SERVICE_UNAVAILABLE,
                summary=f"Flight search service failed: {e}",
                services_used=services_used,
                search_spend=[exchange_to_payment_trace(ex) for ex in exchanges],
            )

        # ── HOTEL SEARCH ─────────────────────────────────────────────────
        _progress("HOTEL_SEARCHING")
        try:
            self.policy.authorize_call(
                task_id, "hotel-search-gateway", 220000
            )
            hotel_exchange = execute_paid_call(
                task_id=task_id,
                service_name="hotel-search-gateway",
                challenge_fn=hotel_search_challenge,
                execute_fn=hotel_search_execute,
                execute_kwargs={
                    "city": normalized.destination_city,
                    "nights": normalized.hotel_nights,
                    "date_start": normalized.date_start,
                },
            )
            exchanges.append(hotel_exchange)
            self.audit.log_service_call(task_id, hotel_exchange)
            services_used.append(ServiceUsage(
                service_name="hotel-search-gateway",
                service_type="hotel_search",
                status="ok",
            ))
        except PolicyViolation as e:
            return ConferenceTripResponse(
                task_id=task_id,
                status=TaskStatus.PAYMENT_FAILED,
                summary=f"Hotel search payment blocked: {e}",
                services_used=services_used,
                search_spend=[exchange_to_payment_trace(ex) for ex in exchanges],
            )
        except Exception as e:
            self.audit.log_error(task_id, "hotel_search_failed", str(e))
            services_used.append(ServiceUsage(
                service_name="hotel-search-gateway",
                service_type="hotel_search",
                status="error",
            ))
            return ConferenceTripResponse(
                task_id=task_id,
                status=TaskStatus.SERVICE_UNAVAILABLE,
                summary=f"Hotel search service failed: {e}",
                services_used=services_used,
                search_spend=[exchange_to_payment_trace(ex) for ex in exchanges],
            )

        # ── RANKING ──────────────────────────────────────────────────────
        _progress("OPTION_SCORING")
        top_n = self.policy.return_top_options
        ranked = rank(
            normalized,
            flight_exchange.result,
            hotel_exchange.result,
            top_n=top_n,
        )
        self.audit.log_ranking(task_id, len(ranked))

        if not ranked:
            return ConferenceTripResponse(
                task_id=task_id,
                status=TaskStatus.NO_VALID_ITINERARY,
                summary="No flight + hotel combinations fit your constraints and budget.",
                services_used=services_used,
                search_spend=[exchange_to_payment_trace(ex) for ex in exchanges],
            )

        # ── RESPONSE ─────────────────────────────────────────────────────
        _progress("RESPONSE_READY")
        recommended = ranked[0]
        alternatives = ranked[1:]

        summary_lines = [
            f"**Recommended plan** — ${recommended.estimated_total_usd:.0f} total",
            f"- Outbound: {recommended.flight.label}  {recommended.flight.origin} → {recommended.flight.destination}",
            f"- Return: {recommended.flight.return_label}  {recommended.flight.return_origin} → {recommended.flight.return_destination}",
            f"- Hotel: {recommended.hotel.name} ({recommended.hotel.area}), "
            f"{recommended.hotel.nights} night(s) at ${recommended.hotel.nightly_rate_usd:.0f}/night",
            "",
        ]
        if recommended.why:
            summary_lines.append("**Why this is best**")
            for reason in recommended.why:
                summary_lines.append(f"- {reason}")
            summary_lines.append("")

        if alternatives:
            summary_lines.append("**Alternatives**")
            for alt in alternatives:
                summary_lines.append(
                    f"- Option {alt.rank}: {alt.flight.label} + {alt.hotel.name} — ${alt.estimated_total_usd:.0f}"
                )
            summary_lines.append("")

        total_search_cost = sum(ex.payment.amount / 1_000_000 for ex in exchanges)
        summary_lines.append("**Search spend**")
        for ex in exchanges:
            summary_lines.append(
                f"- {ex.service_name}: {ex.payment.amount / 1_000_000:.2f} pathUSD"
            )
        summary_lines.append(f"- Total search cost: {total_search_cost:.2f} pathUSD")

        _progress("COMPLETED")

        return ConferenceTripResponse(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            recommended_option=recommended,
            alternatives=alternatives,
            summary="\n".join(summary_lines),
            services_used=services_used,
            search_spend=[exchange_to_payment_trace(ex) for ex in exchanges],
        )
