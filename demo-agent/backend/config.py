"""Runtime configuration for the Conference Trip Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


DOTENV_PATH = Path(__file__).parent / ".env"
DOTENV_VALUES = {
    key: value
    for key, value in dotenv_values(DOTENV_PATH).items()
    if value is not None
}


@dataclass(frozen=True)
class Settings:
    payment_mode: str
    tempo_rpc_url: str
    tempo_chain_id: int
    tempo_explorer_base: str
    pathusd_address: str
    demo_service_receiver: str
    agent_wallet_address: str
    tempo_private_key: str | None
    tempo_private_key_source: str
    tempo_fee_token: str


def _read_raw(name: str, default: str | None = None) -> str | None:
    if name in os.environ:
        return os.environ[name]
    if name in DOTENV_VALUES:
        return DOTENV_VALUES[name]
    return default


def _read_str(name: str, default: str) -> str:
    value = _read_raw(name, default)
    return default if value is None else value.strip()


def _read_int(name: str, default: int) -> int:
    raw = _read_raw(name, str(default))
    return default if raw is None else int(raw)


def _private_key_source() -> str:
    if "TEMPO_PRIVATE_KEY" in os.environ:
        return "environment"
    return "unset"


def _read_private_key() -> str | None:
    return os.environ.get("TEMPO_PRIVATE_KEY")


def _read_payment_mode() -> str:
    mode = _read_str("PAYMENT_MODE", "testnet").lower()
    if mode != "testnet":
        raise ValueError(
            f"Unsupported PAYMENT_MODE {mode!r}. This backend now supports testnet only."
        )
    return mode


def load_settings() -> Settings:
    return Settings(
        payment_mode=_read_payment_mode(),
        tempo_rpc_url=_read_str("TEMPO_RPC_URL", "https://rpc.moderato.tempo.xyz"),
        tempo_chain_id=_read_int("TEMPO_CHAIN_ID", 42431),
        tempo_explorer_base=_read_str(
            "TEMPO_EXPLORER_BASE",
            "https://explore.testnet.tempo.xyz/tx/",
        ),
        pathusd_address=_read_str(
            "TEMPO_PATHUSD_ADDRESS",
            "0x20c0000000000000000000000000000000000000",
        ),
        demo_service_receiver=_read_str(
            "DEMO_SERVICE_RECEIVER",
            "0x25fBB15755ae6c3E18e17E1D77859D2b3c6560CE",
        ),
        agent_wallet_address=_read_str(
            "DEMO_AGENT_WALLET_ADDRESS",
            "0x25fBB15755ae6c3E18e17E1D77859D2b3c6560CE",
        ),
        tempo_private_key=_read_private_key(),
        tempo_private_key_source=_private_key_source(),
        tempo_fee_token=_read_str("TEMPO_FEE_TOKEN", "pathUSD"),
    )
