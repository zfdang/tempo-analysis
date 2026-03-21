"""Constraint normalizer — turns a parsed request into a normalized internal form."""

from __future__ import annotations

from models import ConferenceTripRequest, NormalizedTripRequest
from mock_gateways import get_destination_airports


def normalize(req: ConferenceTripRequest) -> NormalizedTripRequest:
    """Normalize a parsed trip request into the internal canonical form."""
    dest_airports = get_destination_airports(req.destination_city)
    if req.destination_airport and req.destination_airport not in dest_airports:
        dest_airports = [req.destination_airport] + dest_airports

    origin = req.origin.upper() if len(req.origin) <= 3 else req.origin

    return NormalizedTripRequest(
        origin_airport=origin,
        destination_airports=dest_airports,
        destination_city=req.destination_city,
        date_start=req.date_start,
        date_end=req.date_end,
        budget_total_usd=req.budget_total_usd,
        no_red_eye=req.no_red_eye,
        hotel_nights=req.hotel_nights,
        venue_name=req.venue_name,
        preferred_area=req.preferred_area,
        max_hotel_distance_minutes=req.max_hotel_distance_minutes,
        hotel_star_min=req.hotel_star_min,
        hotel_star_max=req.hotel_star_max,
        preferred_airlines=req.preferred_airlines,
        refundable_only=req.refundable_only or False,
    )
