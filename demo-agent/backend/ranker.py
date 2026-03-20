"""Itinerary ranker — scores and ranks flight + hotel combinations."""

from __future__ import annotations

from typing import Any

from models import FlightOption, HotelOption, NormalizedTripRequest, RankedOption


def _to_flight(outbound: dict[str, Any], inbound: dict[str, Any]) -> FlightOption:
    return FlightOption(
        label=outbound["label"],
        origin=outbound["origin"],
        destination=outbound["destination"],
        departure_time=outbound["departure_time"],
        arrival_time=outbound["arrival_time"],
        return_label=inbound["label"],
        return_origin=inbound["origin"],
        return_destination=inbound["destination"],
        return_departure_time=inbound["departure_time"],
        return_arrival_time=inbound["arrival_time"],
        price_usd=round(outbound["price_usd"] + inbound["price_usd"], 2),
        red_eye=outbound["red_eye"] or inbound["red_eye"],
    )


def _to_hotel(raw: dict[str, Any]) -> HotelOption:
    return HotelOption(
        name=raw["name"],
        area=raw.get("area"),
        nightly_rate_usd=raw["nightly_rate_usd"],
        nights=raw["nights"],
        estimated_total_usd=raw["estimated_total_usd"],
        distance_minutes_to_venue=raw.get("distance_minutes_to_venue"),
    )


def _pick_outbound_flights(flights: list[dict[str, Any]], origin: str) -> list[dict[str, Any]]:
    return [f for f in flights if f["origin"] == origin]


def _pick_return_flights(flights: list[dict[str, Any]], origin: str) -> list[dict[str, Any]]:
    return [f for f in flights if f["destination"] == origin]


def rank(
    req: NormalizedTripRequest,
    raw_flights: list[dict[str, Any]],
    raw_hotels: list[dict[str, Any]],
    top_n: int = 3,
) -> list[RankedOption]:
    """Generate ranked flight+hotel combos.

    Hard filters → score → sort → return top_n.
    """
    outbound = _pick_outbound_flights(raw_flights, req.origin_airport)
    returns = _pick_return_flights(raw_flights, req.origin_airport)

    if not outbound or not returns or not raw_hotels:
        return []

    combos: list[tuple[float, dict[str, Any], dict[str, Any], dict[str, Any], list[str]]] = []

    for ob in outbound:
        for rt in returns:
            for hotel in raw_hotels:
                reasons: list[str] = []
                flight_total = ob["price_usd"] + rt["price_usd"]
                hotel_total = hotel["estimated_total_usd"]
                total = round(flight_total + hotel_total, 2)

                # ── hard filters ────────────────────────────────────
                if total > req.budget_total_usd:
                    continue
                if req.no_red_eye and (ob["red_eye"] or rt["red_eye"]):
                    continue
                if req.hotel_star_min and hotel.get("star_rating", 5) < req.hotel_star_min:
                    continue
                if req.hotel_star_max and hotel.get("star_rating", 1) > req.hotel_star_max:
                    continue
                if (
                    req.max_hotel_distance_minutes
                    and hotel.get("distance_minutes_to_venue")
                    and hotel["distance_minutes_to_venue"] > req.max_hotel_distance_minutes
                ):
                    continue

                # ── scoring (lower is better) ───────────────────────
                score = total  # primary: cheapest

                # Prefer earlier departures for outbound
                try:
                    dep_hour = int(ob["departure_time"].split("T")[1][:2])
                except (IndexError, ValueError):
                    dep_hour = 12
                if dep_hour <= 12:
                    score -= 20
                    reasons.append("Morning departure")

                # Prefer closer hotels
                dist = hotel.get("distance_minutes_to_venue")
                if dist and dist <= 15:
                    score -= 15
                    reasons.append(f"Hotel {dist} min from venue")
                elif dist:
                    reasons.append(f"Hotel {dist} min from venue")

                reasons.insert(0, f"Total ${total} (under ${req.budget_total_usd} budget)")
                if req.no_red_eye:
                    reasons.append("No red-eye flights")

                combos.append((score, ob, rt, hotel, reasons))

    combos.sort(key=lambda c: c[0])

    ranked: list[RankedOption] = []
    seen_pairs: set[str] = set()

    for score, ob, rt, hotel, reasons in combos:
        key = f"{ob['label']}|{rt['label']}|{hotel['name']}"
        if key in seen_pairs:
            continue
        seen_pairs.add(key)

        flight_total = ob["price_usd"] + rt["price_usd"]
        hotel_total = hotel["estimated_total_usd"]

        ranked.append(RankedOption(
            rank=len(ranked) + 1,
            flight=_to_flight(ob, rt),
            hotel=_to_hotel(hotel),
            estimated_total_usd=round(flight_total + hotel_total, 2),
            why=reasons,
        ))
        if len(ranked) >= top_n:
            break

    return ranked
