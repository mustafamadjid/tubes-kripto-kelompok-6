#!/usr/bin/env bash
# ============================================================
#  E-Voting RSA — one-command setup
#  Usage: ./setup.sh [--reset]
# ============================================================
set -euo pipefail

RESET=false
[[ "${1:-}" == "--reset" ]] && RESET=true

# ── colours ──────────────────────────────────────────────────
GRN="\033[0;32m"; YLW="\033[1;33m"; RED="\033[0;31m"; RST="\033[0m"
info()  { echo -e "${GRN}[setup]${RST} $*"; }
warn()  { echo -e "${YLW}[warn]${RST}  $*"; }
die()   { echo -e "${RED}[error]${RST} $*"; exit 1; }

# ── pre-flight ────────────────────────────────────────────────
command -v docker  >/dev/null 2>&1 || die "Docker not found. Install Docker first."
command -v docker compose version >/dev/null 2>&1 || \
  docker-compose version >/dev/null 2>&1 || \
  die "Docker Compose not found."

DC="docker compose"
command -v docker compose version >/dev/null 2>&1 || DC="docker-compose"

# ── optional hard reset ───────────────────────────────────────
if $RESET; then
  warn "--reset: tearing down existing containers and volumes..."
  $DC down -v --remove-orphans 2>/dev/null || true
fi

# ── .env ─────────────────────────────────────────────────────
if [[ ! -f .env ]]; then
  info "Creating .env from .env.example..."
  cp .env.example .env
fi

# ── build + start ─────────────────────────────────────────────
info "Building and starting containers (postgres + app)..."
$DC up --build -d

# ── wait for app to be ready ──────────────────────────────────
info "Waiting for app to be ready on http://localhost:8000..."
for i in $(seq 1 30); do
  curl -sf http://localhost:8000/ -o /dev/null 2>/dev/null && break
  sleep 2
  [[ $i -eq 30 ]] && die "App did not start in time. Run '$DC logs app' to debug."
done

echo ""
echo -e "${GRN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo -e "${GRN}  ✅  Setup selesai!${RST}"
echo ""
echo -e "  Voter login   → http://localhost:8000/login"
echo -e "  Admin login   → http://localhost:8000/admin/login"
echo ""
echo -e "  Akun demo voter:"
echo -e "    NIM: 122140001  password: password123"
echo -e "    NIM: 122140002  password: password123"
echo -e "    NIM: 122140003  password: password123"
echo ""
echo -e "  Akun admin:"
echo -e "    username: admin   password: admin123"
echo ""
echo -e "  Stop: $DC down"
echo -e "  Logs: $DC logs -f app"
echo -e "${GRN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
