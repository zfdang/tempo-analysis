"""Mock flight and hotel search gateways.

Each gateway simulates the MPP 402 flow:
  request  →  402 Payment Required  →  (caller pays)  →  retry  →  results

Since this is a demo, the gateways return hard-coded but realistic-looking data
keyed by destination city.  The 402 challenge is returned as a dict that the
MPP client can process.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

from config import load_settings

# ── Helpers ──────────────────────────────────────────────────────────────────

_HOTEL_NAMES: dict[str, list[dict[str, Any]]] = {
    "New York": [
        {"name": "The Manhattan Inn", "area": "Midtown", "star": 3.5, "rate": 189},
        {"name": "NYC Boutique Hotel", "area": "Chelsea", "star": 4.0, "rate": 229},
        {"name": "Times Square Lodge", "area": "Times Square", "star": 3.0, "rate": 159},
        {"name": "Central Park Suites", "area": "Upper West Side", "star": 4.5, "rate": 319},
        {"name": "Brooklyn Bridge Inn", "area": "DUMBO", "star": 3.5, "rate": 175},
    ],
    "San Francisco": [
        {"name": "Union Square Hotel", "area": "Union Square", "star": 3.5, "rate": 199},
        {"name": "Embarcadero Suites", "area": "Embarcadero", "star": 4.0, "rate": 259},
        {"name": "SoMa Budget Inn", "area": "SoMa", "star": 3.0, "rate": 149},
    ],
}

_DEFAULT_HOTELS = [
    {"name": "City Center Hotel", "area": "Downtown", "star": 3.5, "rate": 169},
    {"name": "Airport Comfort Inn", "area": "Airport", "star": 3.0, "rate": 129},
    {"name": "Grand Plaza", "area": "Downtown", "star": 4.0, "rate": 239},
]

_AIRPORT_MAP: dict[str, list[str]] = {
    "New York": ["JFK", "EWR", "LGA"],
    "San Francisco": ["SFO"],
    "Los Angeles": ["LAX"],
    "Chicago": ["ORD", "MDW"],
    "Boston": ["BOS"],
    "Seattle": ["SEA"],
}

_AIRLINES = ["United", "Delta", "American", "JetBlue", "Southwest", "Alaska"]

FLIGHT_SEARCH_AMOUNT = 180000  # 0.18 pathUSD in base units (6 decimals)
HOTEL_SEARCH_AMOUNT = 220000   # 0.22 pathUSD in base units (6 decimals)


# ── 402 challenge ────────────────────────────────────────────────────────────

def _make_402_challenge(service_name: str, amount: int) -> dict[str, Any]:
    """Simulate a WWW-Authenticate: Payment challenge."""
    settings = load_settings()
    return {
        "status": 402,
        "service_name": service_name,
        "www_authenticate": {
            "scheme": "Payment",
            "intent": "charge",
            "network": "tempo",
            "token": "pathUSD",
            "amount": amount,
            "receiver": settings.demo_service_receiver,
            "max_age": 120,
        },
    }


# ── Flight search gateway ───────────────────────────────────────────────────

def flight_search_challenge() -> dict[str, Any]:
    """Return the 402 challenge for the flight search gateway."""
    return _make_402_challenge("flight-search-gateway", FLIGHT_SEARCH_AMOUNT)


def flight_search_execute(
    origin: str,
    destinations: list[str],
    date_start: date,
    date_end: date,
) -> list[dict[str, Any]]:
    """Return mock flight results after payment is completed."""
    results: list[dict[str, Any]] = []
    rng = random.Random(f"{origin}-{destinations}-{date_start}")

    for dest in destinations:
        for i in range(3):
            dep_hour = rng.randint(6, 20)
            duration_h = rng.uniform(2.5, 6.0)
            price = round(rng.uniform(180, 420), 2)
            is_red_eye = dep_hour >= 22 or dep_hour <= 4

            dep_dt = date_start + timedelta(hours=dep_hour, minutes=rng.randint(0, 55))
            arr_dt = dep_dt + timedelta(hours=duration_h)

            airline = rng.choice(_AIRLINES)
            results.append({
                "label": f"{airline} {rng.randint(100, 9999)}",
                "origin": origin,
                "destination": dest,
                "departure_time": f"{date_start}T{dep_hour:02d}:{rng.randint(0,59):02d}",
                "arrival_time": f"{date_start}T{(dep_hour + int(duration_h)) % 24:02d}:{rng.randint(0,59):02d}",
                "price_usd": price,
                "red_eye": is_red_eye,
            })

        # Return flights
        for i in range(3):
            dep_hour = rng.randint(6, 22)
            duration_h = rng.uniform(2.5, 6.0)
            price = round(rng.uniform(180, 420), 2)
            is_red_eye = dep_hour >= 22 or dep_hour <= 4

            results.append({
                "label": f"{rng.choice(_AIRLINES)} {rng.randint(100, 9999)}",
                "origin": dest,
                "destination": origin,
                "departure_time": f"{date_end}T{dep_hour:02d}:{rng.randint(0,59):02d}",
                "arrival_time": f"{date_end}T{(dep_hour + int(duration_h)) % 24:02d}:{rng.randint(0,59):02d}",
                "price_usd": price,
                "red_eye": is_red_eye,
            })

    return results


# ── Hotel search gateway ────────────────────────────────────────────────────

def hotel_search_challenge() -> dict[str, Any]:
    """Return the 402 challenge for the hotel search gateway."""
    return _make_402_challenge("hotel-search-gateway", HOTEL_SEARCH_AMOUNT)


def hotel_search_execute(
    city: str,
    nights: int,
    date_start: date,
) -> list[dict[str, Any]]:
    """Return mock hotel results after payment is completed."""
    hotels = _HOTEL_NAMES.get(city, _DEFAULT_HOTELS)
    rng = random.Random(f"{city}-{date_start}")

    results = []
    for h in hotels:
        jitter = rng.uniform(0.9, 1.15)
        rate = round(h["rate"] * jitter, 2)
        results.append({
            "name": h["name"],
            "area": h.get("area", "Downtown"),
            "nightly_rate_usd": rate,
            "nights": nights,
            "estimated_total_usd": round(rate * nights, 2),
            "star_rating": h.get("star", 3.0),
            "distance_minutes_to_venue": rng.randint(5, 45),
        })

    return results


def get_destination_airports(city: str) -> list[str]:
    """Map a destination city to likely airport codes."""
    return _AIRPORT_MAP.get(city, [city[:3].upper()])
