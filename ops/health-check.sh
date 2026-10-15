#!/usr/bin/env bash
# Operational Health Check Script for E-Commerce Support Chat Service

set -e

PORT="${PORT:-8000}"
HOST="${HOST:-localhost}"
URL="http://${HOST}:${PORT}/api/health"

echo "🔍 Probing service health at ${URL}..."

HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" "${URL}" || true)
HTTP_BODY=$(echo "${HTTP_RESPONSE}" | sed '$d')
HTTP_STATUS=$(echo "${HTTP_RESPONSE}" | tail -n1)

if [ "${HTTP_STATUS}" -eq 200 ]; then
  echo "✅ Service is HEALTHY (HTTP 200)"
  echo "Response Payload: ${HTTP_BODY}"
  exit 0
else
  echo "❌ Health check FAILED! Received HTTP status ${HTTP_STATUS}"
  echo "Response: ${HTTP_BODY}"
  exit 1
fi
