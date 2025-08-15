#!/usr/bin/env sh
set -e

# Load OpenAI key from secret if present
if [ -f /run/secrets/openai_api_key ]; then
  # Read, strip CR/LF and non-printable (defensive); avoid BOM issues
  RAW_KEY=$(cat /run/secrets/openai_api_key | tr -d '\r' | tr -d '\n')
  # Remove potential UTF-8 BOM bytes if present
  case "$RAW_KEY" in $'\xEF\xBB\xBF'*) RAW_KEY=${RAW_KEY#$'\xEF\xBB\xBF'} ;; esac
  export OPENAI_API_KEY="$RAW_KEY"
fi

# Remove accidental exposure in env printouts
unset OPENAI_API_KEY_EXPOSE 2>/dev/null || true

echo "[entrypoint] Waiting for databases..."
python wait_for_databases.py

echo "[entrypoint] Starting examples.py"
exec python examples.py
