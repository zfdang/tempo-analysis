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
    settings = load_settings()
    if token != "pathUSD":
        raise RuntimeError(f"Only pathUSD is supported in testnet mode right now, got {token!r}")
    if not settings.tempo_private_key:
        raise RuntimeError("TEMPO_PRIVATE_KEY is required for testnet payment mode")

    w3 = Web3(Web3.HTTPProvider(settings.tempo_rpc_url, request_kwargs={"timeout": 20}))
    if not w3.is_connected():
        raise RuntimeError(f"Could not connect to Tempo RPC at {settings.tempo_rpc_url}")

    account = w3.eth.account.from_key(settings.tempo_private_key)
    sender = account.address
    if settings.agent_wallet_address and settings.agent_wallet_address.lower() != sender.lower():
        raise RuntimeError(
            f"Configured DEMO_AGENT_WALLET_ADDRESS {settings.agent_wallet_address} "
            f"does not match signer address {sender}"
        )

    token_contract = w3.eth.contract(
        address=Web3.to_checksum_address(settings.pathusd_address),
        abi=TIP20_MIN_ABI,
    )

    nonce = w3.eth.get_transaction_count(sender)
    gas_price = int(w3.eth.gas_price)
    tx = token_contract.functions.transfer(
        Web3.to_checksum_address(receiver),
        int(amount),
    ).build_transaction({
        "chainId": settings.tempo_chain_id,
        "from": sender,
        "nonce": nonce,
        "gasPrice": gas_price,
    })

    estimate = w3.eth.estimate_gas(tx)
    tx["gas"] = max(int(estimate * 1.2), 100000)

    signed = account.sign_transaction(tx)
    tx_hash_bytes = w3.eth.send_raw_transaction(signed.raw_transaction)
    tx_hash = w3.to_hex(tx_hash_bytes)

    # Tempo targets fast finality, so waiting here makes the demo more honest.
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash_bytes, timeout=30)
    if int(receipt["status"]) != 1:
        raise RuntimeError(f"Tempo transaction failed: {tx_hash}")

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
    """Build and submit a real Tempo testnet payment."""
    settings = load_settings()
    if settings.payment_mode != "testnet":
        raise RuntimeError(f"Unsupported PAYMENT_MODE {settings.payment_mode!r}")

    return _submit_testnet_payment(
        task_id=task_id,
        receiver=receiver,
        token=token,
        amount=amount,
        fee_token=fee_token,
        validity_seconds=validity_seconds,
    )
