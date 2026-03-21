"""Audit logger — records task lifecycle, service calls, and payments."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from mpp_client import MppExchange

logger = logging.getLogger("audit")


@dataclass
class AuditEntry:
    timestamp: str
    task_id: str
    event: str
    data: dict[str, Any] = field(default_factory=dict)


class AuditLogger:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def _log(self, task_id: str, event: str, data: dict[str, Any] | None = None) -> None:
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            event=event,
            data=data or {},
        )
        self._entries.append(entry)
        logger.info("%s [%s] %s %s", entry.timestamp, task_id, event, json.dumps(entry.data))

    def log_task_created(self, task_id: str, prompt: str) -> None:
        self._log(task_id, "task_created", {"prompt_length": len(prompt)})

    def log_task_status(self, task_id: str, status: str) -> None:
        self._log(task_id, "task_status", {"status": status})

    def log_service_call(self, task_id: str, exchange: MppExchange) -> None:
        self._log(task_id, "service_call", {
            "service_name": exchange.service_name,
            "tx_hash": exchange.payment.tx_hash,
            "amount": exchange.payment.amount,
            "token": exchange.payment.token,
            "receipt_id": exchange.payment.receipt_id,
            "result_count": len(exchange.result) if isinstance(exchange.result, list) else 1,
        })

    def log_ranking(self, task_id: str, option_count: int) -> None:
        self._log(task_id, "ranking_complete", {"options": option_count})

    def log_error(self, task_id: str, event: str, message: str) -> None:
        self._log(task_id, event, {"message": message})

    def get_entries(self, task_id: str | None = None) -> list[dict[str, Any]]:
        entries = self._entries
        if task_id:
            entries = [e for e in entries if e.task_id == task_id]
        return [asdict(e) for e in entries]
