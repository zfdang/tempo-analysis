"""Tempo testnet connectivity and token-balance helpers."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from config import Settings, load_settings

ERC20_MIN_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def make_web3(settings: Settings | None = None) -> Web3:
    cfg = settings or load_settings()
    return Web3(Web3.HTTPProvider(cfg.tempo_rpc_url, request_kwargs={"timeout": 20}))


def get_wallet_address(settings: Settings | None = None) -> str | None:
    cfg = settings or load_settings()
    if cfg.tempo_private_key:
        try:
            account = Web3().eth.account.from_key(cfg.tempo_private_key)
            return account.address
        except Exception:
            return None
    return cfg.agent_wallet_address or None


def get_pathusd_balance(address: str, settings: Settings | None = None) -> float | None:
    cfg = settings or load_settings()
    w3 = make_web3(cfg)
    if not w3.is_connected():
        return None

    token = w3.eth.contract(
        address=Web3.to_checksum_address(cfg.pathusd_address),
        abi=ERC20_MIN_ABI,
    )
    owner = Web3.to_checksum_address(address)
    balance = token.functions.balanceOf(owner).call()
    decimals = token.functions.decimals().call()
    return balance / (10 ** decimals)


def get_network_status(settings: Settings | None = None) -> dict[str, Any]:
    cfg = settings or load_settings()
    w3 = make_web3(cfg)
    connected = w3.is_connected()

    wallet_address = get_wallet_address(cfg)
    balance = None
    if connected and wallet_address:
        try:
            balance = get_pathusd_balance(wallet_address, cfg)
        except Exception:
            balance = None

    chain_id = None
    block_number = None
    gas_price_wei = None
    if connected:
        try:
            chain_id = w3.eth.chain_id
            block_number = w3.eth.block_number
            gas_price_wei = int(w3.eth.gas_price)
        except Exception:
            pass

    return {
        "connected": connected,
        "configured_mode": cfg.payment_mode,
        "resolved_mode": "testnet",
        "rpc_url": cfg.tempo_rpc_url,
        "chain_id": chain_id,
        "expected_chain_id": cfg.tempo_chain_id,
        "block_number": block_number,
        "gas_price_wei": gas_price_wei,
        "pathusd_address": cfg.pathusd_address,
        "wallet_address": wallet_address,
        "wallet_pathusd_balance": balance,
        "service_receiver": cfg.demo_service_receiver,
        "private_key_configured": bool(cfg.tempo_private_key),
        "private_key_source": cfg.tempo_private_key_source,
    }
