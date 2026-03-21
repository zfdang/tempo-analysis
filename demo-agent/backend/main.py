"""FastAPI entry point for the Conference Trip Agent."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from audit import AuditLogger
from config import load_settings
from network import get_network_status
from orchestrator import Orchestrator
from policy import PolicyEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

app = FastAPI(title="Conference Trip Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

policy = PolicyEngine()
audit = AuditLogger()
orchestrator = Orchestrator(policy=policy, audit=audit)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    task_id: str
    status: str
    summary: str | None = None
    recommended_option: dict | None = None
    alternatives: list[dict] = Field(default_factory=list)
    services_used: list[dict] = Field(default_factory=list)
    search_spend: list[dict] = Field(default_factory=list)
    audit_log: list[dict] = Field(default_factory=list)


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = orchestrator.run(req.message)
    return ChatResponse(
        task_id=result.task_id,
        status=result.status.value,
        summary=result.summary,
        recommended_option=result.recommended_option.model_dump() if result.recommended_option else None,
        alternatives=[a.model_dump() for a in result.alternatives],
        services_used=[s.model_dump() for s in result.services_used],
        search_spend=[s.model_dump() for s in result.search_spend],
        audit_log=audit.get_entries(result.task_id),
    )


@app.get("/api/health")
def health():
    network = get_network_status(load_settings())
    return {
        "status": "ok",
        "payment_mode": network["resolved_mode"],
        "wallet_address": network["wallet_address"],
        "private_key_configured": network["private_key_configured"],
        "private_key_source": network["private_key_source"],
        "connected": network["connected"],
    }


@app.get("/api/network")
def network():
    return get_network_status(load_settings())
