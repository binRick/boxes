#!/bin/bash
# Smoke test for the Boxes.py web server.
# Usage: .claude/skills/run-boxes/smoke.sh [PORT]
# Creates .venv if missing, starts boxesserver on PORT (default 8765),
# drives it (homepage, generator page, SVG render), then stops it.
set -euo pipefail
cd "$(dirname "$0")/../../.."

PORT="${1:-8765}"
PY=.venv/bin/python

if [ ! -x "$PY" ]; then
  echo "== creating venv and installing requirements =="
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

"$PY" scripts/boxesserver --port "$PORT" &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null || true' EXIT

# wait for the server to accept connections
for i in $(seq 1 20); do
  curl -s -o /dev/null "http://localhost:$PORT/" && break
  sleep 0.5
done

fail() { echo "FAIL: $1"; exit 1; }

code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/")
[ "$code" = 200 ] || fail "homepage returned HTTP $code"
echo "ok: homepage HTTP 200"

# capture first: piping curl into grep -q trips pipefail via SIGPIPE
page=$(curl -s "http://localhost:$PORT/UniversalBox")
grep -q "<title>UniversalBox" <<<"$page" \
  || fail "UniversalBox generator page did not render"
echo "ok: generator page renders"

# no suffix after the Xs: BSD mktemp won't substitute them otherwise
svg=$(mktemp /tmp/boxes_smoke.XXXXXX)
curl -s "http://localhost:$PORT/UniversalBox?x=100&y=100&h=100&render=1" -o "$svg"
head -c 100 "$svg" | grep -q "<?xml" || fail "rendered output is not SVG: $(head -c 200 "$svg")"
[ "$(wc -c < "$svg")" -gt 10000 ] || fail "rendered SVG suspiciously small"
echo "ok: rendered 100x100x100 UniversalBox SVG ($(wc -c < "$svg" | tr -d ' ') bytes) -> $svg"

echo "PASS"
