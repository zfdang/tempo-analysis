"""Policy engine — enforces budget and service allowlists."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class PolicyViolation(Exception):
    pass


class PolicyEngine:
    def __init__(self, policy_path: str | Path | None = None):
        if policy_path is None:
            policy_path = Path(__file__).parent / "policy.yaml"
        with open(policy_path) as f:
            self._cfg: dict[str, Any] = yaml.safe_load(f)

        self._task_spend: dict[str, float] = {}  # task_id → cumulative USD

    # ── read helpers ─────────────────────────────────────────────────────

    @property
    def max_search_spend_usd(self) -> float:
        return float(self._cfg["task_policy"]["max_search_spend_usd"])

    @property
    def max_trip_budget_usd(self) -> float:
        return float(self._cfg["task_policy"]["max_trip_budget_usd"])

    @property
    def return_top_options(self) -> int:
        return int(self._cfg.get("travel_policy", {}).get("return_top_options", 3))

    def service_allowed(self, service_name: str) -> bool:
        svc = self._cfg.get("services", {}).get(service_name, {})
        return bool(svc.get("allow", False))

    def max_amount_per_call(self, service_name: str) -> int:
        svc = self._cfg.get("services", {}).get(service_name, {})
        return int(svc.get("max_amount_per_call", 0))

    # ── enforcement ──────────────────────────────────────────────────────

    def check_service(self, service_name: str) -> None:
        if not self.service_allowed(service_name):
            raise PolicyViolation(f"Service {service_name!r} is not allowed by policy")

    def check_amount(self, service_name: str, amount: int) -> None:
        cap = self.max_amount_per_call(service_name)
        if cap and amount > cap:
            raise PolicyViolation(
                f"Amount {amount} exceeds per-call cap {cap} for {service_name!r}"
            )

    def check_trip_budget(self, budget_usd: float) -> None:
        if budget_usd > self.max_trip_budget_usd:
            raise PolicyViolation(
                f"Trip budget ${budget_usd} exceeds max ${self.max_trip_budget_usd}"
            )

    def reserve_spend(self, task_id: str, amount_usd: float) -> None:
        current = self._task_spend.get(task_id, 0.0)
        if current + amount_usd > self.max_search_spend_usd:
            raise PolicyViolation(
                f"Search spend would exceed ${self.max_search_spend_usd} for task {task_id}"
            )
        self._task_spend[task_id] = current + amount_usd

    def authorize_call(self, task_id: str, service_name: str, amount: int) -> None:
        """Run all pre-payment checks for a service call."""
        self.check_service(service_name)
        self.check_amount(service_name, amount)
        self.reserve_spend(task_id, amount / 1_000_000)
