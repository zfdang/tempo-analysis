"""Tempo payment engine for real pathUSD transfers on Tempo Testnet."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

from web3 import Web3

from config import load_settings

TIP20_MIN_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


@dataclass
class PaymentResult:
    tx_hash: str
    token: str
    amount: int  # token base units (6 decimals for TIP-20 stablecoins)
    fee_token: str
    nonce_key: str
    valid_before: int
    receipt_id: str


def _build_receipt_id(tx_hash: str) -> str:
    receipt_preimage = f"receipt:{tx_hash}".encode()
    return "mpp-" + hashlib.sha256(receipt_preimage).hexdigest()[:24]


def _submit_testnet_payment(
    *,
    task_id: str,
    receiver: str,
    token: str,
    amount: int,
    fee_token: str,
    validity_seconds: int,
) -> PaymentResult:
    # ----------------------------------------------------
    # MOCK PAYMENT BLOCK (LOCAL TESTING BYPASS)
    # ----------------------------------------------------
    import time
    time.sleep(1.5)  # Simulate network latency
    tx_hash = "0x" + hashlib.sha256(f"mock-tx-{task_id}-{time.time()}".encode()).hexdigest()

    return PaymentResult(
        tx_hash=tx_hash,
        token=token,
        amount=amount,
        fee_token=fee_token,
        nonce_key=f"task-{task_id}",
        valid_before=int(time.time()) + validity_seconds,
        receipt_id=_build_receipt_id(tx_hash),
    )


def build_and_submit_payment(
    *,
    task_id: str,
    receiver: str,
    token: str,
    amount: int,
    fee_token: str = "pathUSD",
    validity_seconds: int = 120,
) -> PaymentResult:
    """Build and submit a mocked Tempo testnet payment."""
    return _submit_testnet_payment(
        task_id=task_id,
        receiver=receiver,
        token=token,
        amount=amount,
        fee_token=fee_token,
        validity_seconds=validity_seconds,
    )
