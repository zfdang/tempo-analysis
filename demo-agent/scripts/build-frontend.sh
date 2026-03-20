#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Installing frontend dependencies..."
cd "$ROOT/frontend"
npm install

echo "==> Building frontend..."
npm run build

echo "==> Frontend built to $ROOT/frontend/dist"
