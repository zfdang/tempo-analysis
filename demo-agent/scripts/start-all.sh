#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/backend/.venv"

# ── 1. Ensure Python venv ───────────────────────────────────────────────────
if [ ! -d "$VENV" ]; then
  echo "==> Creating Python venv..."
  python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"
pip install -q -r "$ROOT/backend/requirements.txt"

# ── 2. Ensure frontend deps ────────────────────────────────────────────────
echo "==> Installing frontend dependencies..."
cd "$ROOT/frontend"
npm install --silent

# ── 3. Start backend (background) ──────────────────────────────────────────
echo "==> Starting backend on http://0.0.0.0:8000 ..."
cd "$ROOT/backend"
source "$VENV/bin/activate"
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# ── 4. Start frontend dev server (foreground) ──────────────────────────────
echo "==> Starting frontend on http://localhost:5173 ..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  Backend:  http://localhost:8000  (pid $BACKEND_PID)"
echo "  Frontend: http://localhost:5173  (pid $FRONTEND_PID)"
echo ""
echo "  Press Ctrl+C to stop both."

# ── 5. Cleanup on exit ─────────────────────────────────────────────────────
cleanup() {
  echo ""
  echo "==> Shutting down..."
  kill "$FRONTEND_PID" 2>/dev/null
  kill "$BACKEND_PID" 2>/dev/null
  wait "$FRONTEND_PID" 2>/dev/null
  wait "$BACKEND_PID" 2>/dev/null
  echo "==> Done."
}
trap cleanup EXIT INT TERM

wait
