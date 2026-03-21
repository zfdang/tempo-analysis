"""Pydantic models matching request-schema.json and response-schema.json."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────────────────────────


class ConferenceTripRequest(BaseModel):
    trip_type: str = "conference"
    origin: str = Field(min_length=2)
    destination_city: str = Field(min_length=2)
    destination_airport: Optional[str] = None
    date_start: date
    date_end: date
    budget_total_usd: float = Field(gt=0)
    no_red_eye: bool = True
    hotel_nights: int = Field(ge=1, le=14)
    venue_name: Optional[str] = None
    preferred_area: Optional[str] = None
    max_hotel_distance_minutes: Optional[int] = Field(default=None, ge=1, le=240)
    hotel_star_min: Optional[float] = Field(default=None, ge=1, le=5)
    hotel_star_max: Optional[float] = Field(default=None, ge=1, le=5)
    preferred_airlines: list[str] = Field(default_factory=list)
    refundable_only: Optional[bool] = None


# ── Response sub-models ──────────────────────────────────────────────────────


class FlightOption(BaseModel):
    label: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    return_label: Optional[str] = None
    return_origin: Optional[str] = None
    return_destination: Optional[str] = None
    return_departure_time: Optional[str] = None
    return_arrival_time: Optional[str] = None
    price_usd: float = Field(ge=0)
    red_eye: bool


class HotelOption(BaseModel):
    name: str
    area: Optional[str] = None
    nightly_rate_usd: float = Field(ge=0)
    nights: int = Field(ge=1)
    estimated_total_usd: float = Field(ge=0)
    distance_minutes_to_venue: Optional[int] = Field(default=None, ge=0)


class RankedOption(BaseModel):
    rank: int = Field(ge=1)
    flight: FlightOption
    hotel: HotelOption
    estimated_total_usd: float = Field(ge=0)
    why: list[str] = Field(min_length=1)


class ServiceUsage(BaseModel):
    service_name: str
    service_type: str
    status: str


class PaymentTrace(BaseModel):
    service_name: str
    token: str
    amount: float = Field(ge=0)
    tx_hash: str
    receipt_id: Optional[str] = None


class TaskStatus(str, Enum):
    COMPLETED = "completed"
    NEEDS_CLARIFICATION = "needs_clarification"
    SEARCH_BUDGET_EXCEEDED = "search_budget_exceeded"
    SERVICE_UNAVAILABLE = "service_unavailable"
    PAYMENT_FAILED = "payment_failed"
    NO_VALID_ITINERARY = "no_valid_itinerary"


class ConferenceTripResponse(BaseModel):
    task_id: str = Field(min_length=1)
    status: TaskStatus
    recommended_option: Optional[RankedOption] = None
    alternatives: list[RankedOption] = Field(default_factory=list, max_length=5)
    summary: Optional[str] = None
    services_used: list[ServiceUsage] = Field(default_factory=list)
    search_spend: list[PaymentTrace] = Field(default_factory=list)


# ── Internal workflow models ─────────────────────────────────────────────────


class NormalizedTripRequest(BaseModel):
    """Internal normalized form after constraint normalization."""

    origin_airport: str
    destination_airports: list[str]
    destination_city: str
    date_start: date
    date_end: date
    budget_total_usd: float
    no_red_eye: bool
    hotel_nights: int
    venue_name: Optional[str] = None
    preferred_area: Optional[str] = None
    max_hotel_distance_minutes: Optional[int] = None
    hotel_star_min: Optional[float] = None
    hotel_star_max: Optional[float] = None
    preferred_airlines: list[str] = Field(default_factory=list)
    refundable_only: bool = False
