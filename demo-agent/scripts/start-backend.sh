#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/backend/.venv"

if [ ! -d "$VENV" ]; then
  echo "==> Creating Python venv..."
  python3 -m venv "$VENV"
fi

if [ -z "${TEMPO_PRIVATE_KEY:-}" ]; then
  echo "TEMPO_PRIVATE_KEY must be set in the environment." >&2
  echo "Example:" >&2
  echo "  export PAYMENT_MODE=testnet" >&2
  echo "  export DEMO_AGENT_WALLET_ADDRESS=0x25fBB15755ae6c3E18e17E1D77859D2b3c6560CE" >&2
  echo "  export TEMPO_PRIVATE_KEY=your_testnet_private_key" >&2
  exit 1
fi

echo "==> Activating venv & installing dependencies..."
source "$VENV/bin/activate"
pip install -q -r "$ROOT/backend/requirements.txt"

echo "==> Tempo signer: using TEMPO_PRIVATE_KEY from environment"

echo "==> Starting backend on http://0.0.0.0:8000 ..."
cd "$ROOT/backend"
exec uvicorn main:app --host 0.0.0.0 --port 8000
