#!/bin/sh
set -eu

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  alembic upgrade head
fi

if [ "${GENERATE_KEYS_IF_MISSING:-true}" = "true" ]; then
  if [ ! -f "${ADMIN_PRIVATE_KEY_PATH}" ] \
    || [ ! -f "${ADMIN_PUBLIC_KEY_PATH}" ] \
    || [ ! -f "${SYSTEM_PRIVATE_KEY_PATH}" ] \
    || [ ! -f "${SYSTEM_PUBLIC_KEY_PATH}" ]; then
    python scripts/generate_keys.py
  fi
fi

exec "$@"
