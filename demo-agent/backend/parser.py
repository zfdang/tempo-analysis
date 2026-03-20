"""Trip request parser — extracts structured fields from natural language."""

from __future__ import annotations

import re
from datetime import date
from typing import Optional

from models import ConferenceTripRequest

# ── City / airport mappings ──────────────────────────────────────────────────

_CITY_ALIASES: dict[str, str] = {
    "nyc": "New York",
    "new york city": "New York",
    "new york": "New York",
    "sf": "San Francisco",
    "san fran": "San Francisco",
    "san francisco": "San Francisco",
    "la": "Los Angeles",
    "los angeles": "Los Angeles",
    "chi": "Chicago",
    "chicago": "Chicago",
    "bos": "Boston",
    "boston": "Boston",
    "sea": "Seattle",
    "seattle": "Seattle",
}

_AIRPORT_TO_CITY: dict[str, str] = {
    "SFO": "San Francisco",
    "JFK": "New York",
    "EWR": "New York",
    "LGA": "New York",
    "LAX": "Los Angeles",
    "ORD": "Chicago",
    "MDW": "Chicago",
    "BOS": "Boston",
    "SEA": "Seattle",
}

_MONTH_MAP: dict[str, int] = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def _resolve_city(text: str) -> Optional[str]:
    low = text.lower().strip()
    for alias, city in _CITY_ALIASES.items():
        if alias in low:
            return city
    return None


def _resolve_origin(text: str) -> Optional[str]:
    lookahead = (
        r"(?=\.|,|$|\s+(?:under|budget|no\b|red[- ]?eye|return|for|with|on\b|to\b|and\b|"
        r"jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|"
        r"sep|september|oct|october|nov|november|dec|december)\b)"
    )
    patterns = [
        rf"(?:depart(?:ing)?(?:\s+from)?|leaving|out of|from)\s+([A-Za-z]{{3}}|[A-Za-z ]+?){lookahead}",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw = m.group(1).strip().rstrip(".,")
            upper = raw.upper()
            if upper in _AIRPORT_TO_CITY:
                return upper
            city = _resolve_city(raw)
            if city:
                # Return the primary airport code for the city
                for code, c in _AIRPORT_TO_CITY.items():
                    if c == city:
                        return code
            return raw
    return None


def _infer_year(month: int, day: int) -> int:
    """Infer the next plausible calendar year for a month/day pair."""
    today = date.today()
    candidate = date(today.year, month, day)
    return today.year if candidate >= today else today.year + 1


def _parse_dates(text: str) -> tuple[Optional[date], Optional[date]]:
    """Try to extract date_start and date_end from the prompt."""
    # Pattern: "Month DD-DD" or "Month DD - DD"
    m = re.search(
        r"(\w+)\s+(\d{1,2})\s*[-–]\s*(\d{1,2})",
        text,
        re.IGNORECASE,
    )
    if m:
        month_str = m.group(1).lower()
        day_start = int(m.group(2))
        day_end = int(m.group(3))
        month = _MONTH_MAP.get(month_str)
        if month:
            year = _infer_year(month, day_start)
            try:
                return date(year, month, day_start), date(year, month, day_end)
            except ValueError:
                pass

    # Pattern: "YYYY-MM-DD to YYYY-MM-DD"
    m = re.search(
        r"(\d{4}-\d{2}-\d{2})\s*(?:to|through|–|-)\s*(\d{4}-\d{2}-\d{2})",
        text,
    )
    if m:
        try:
            return date.fromisoformat(m.group(1)), date.fromisoformat(m.group(2))
        except ValueError:
            pass

    return None, None


def _parse_budget(text: str) -> Optional[float]:
    m = re.search(r"\$\s?([\d,]+)", text)
    if m:
        return float(m.group(1).replace(",", ""))
    m = re.search(r"([\d,]+)\s*(?:dollars|usd|total)", text, re.IGNORECASE)
    if m:
        return float(m.group(1).replace(",", ""))
    return None


def _parse_no_red_eye(text: str) -> bool:
    if re.search(r"(?:allow|with|including)\s+red[- ]?eye", text, re.IGNORECASE):
        return False
    if re.search(r"(?:red[- ]?eyes?\s+ok|red[- ]?eye\s+ok|any flight)", text, re.IGNORECASE):
        return False
    if re.search(r"(?:no|avoid)\s*red[- ]?eye", text, re.IGNORECASE):
        return True
    # Match policy.yaml: allow_red_eye_default = false
    return True


def _parse_destination(text: str) -> Optional[str]:
    boundary = r"(?=\.|,|$|\s+(?:from|under|budget|with|depart|leaving|no\b|return|jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\b)"
    patterns = [
        rf"(?:conference|event|meeting)\s+in\s+([A-Za-z ]+?){boundary}",
        rf"(?:to|in)\s+(?:a\s+)?(?:conference\s+in\s+)?([A-Za-z ]+?){boundary}",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw = m.group(1).strip().rstrip(".,")
            city = _resolve_city(raw)
            if city:
                return city
    return None


class ParseResult:
    def __init__(
        self,
        request: Optional[ConferenceTripRequest] = None,
        missing_fields: Optional[list[str]] = None,
    ):
        self.request = request
        self.missing_fields = missing_fields or []

    @property
    def ok(self) -> bool:
        return self.request is not None


def parse_trip_request(prompt: str) -> ParseResult:
    """Parse a natural-language trip request into a ConferenceTripRequest.

    Returns ParseResult with either a valid request or a list of missing fields
    that the UI should ask the user to clarify.
    """
    destination = _parse_destination(prompt)
    origin = _resolve_origin(prompt)
    date_start, date_end = _parse_dates(prompt)
    budget = _parse_budget(prompt)
    no_red_eye = _parse_no_red_eye(prompt)

    missing: list[str] = []
    if not destination:
        missing.append("destination city")
    if not origin:
        missing.append("departure city or airport")
    if not date_start or not date_end:
        missing.append("trip dates")
    if not budget:
        missing.append("total budget")

    if missing:
        return ParseResult(missing_fields=missing)

    assert destination and origin and date_start and date_end and budget
    if date_end < date_start:
        return ParseResult(missing_fields=["valid trip dates"])
    hotel_nights = max(1, (date_end - date_start).days)

    return ParseResult(
        request=ConferenceTripRequest(
            trip_type="conference",
            origin=origin,
            destination_city=destination,
            date_start=date_start,
            date_end=date_end,
            budget_total_usd=budget,
            no_red_eye=no_red_eye,
            hotel_nights=hotel_nights,
        )
    )
