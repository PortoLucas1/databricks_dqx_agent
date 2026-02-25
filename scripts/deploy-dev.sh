#!/usr/bin/env bash
# Deploy the bundle to dev using variables from .env
# Usage: from repo root, run: ./scripts/deploy-dev.sh
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

if [ -z "${SQL_WAREHOUSE_ID:-}" ] || [ -z "${SERVICE_PRINCIPAL_NAME:-}" ]; then
  echo "Error: SQL_WAREHOUSE_ID and SERVICE_PRINCIPAL_NAME must be set."
  echo "Copy .env.example to .env and set the values, then run this script again."
  exit 1
fi

VAR_ARGS=(
  --var "sql_warehouse_id=$SQL_WAREHOUSE_ID"
  --var "service_principal_name=$SERVICE_PRINCIPAL_NAME"
)

echo "Validating bundle for target dev..."
databricks bundle validate -t dev "${VAR_ARGS[@]}"

echo "Deploying bundle to dev..."
databricks bundle deploy -t dev "${VAR_ARGS[@]}"

echo "Done."
