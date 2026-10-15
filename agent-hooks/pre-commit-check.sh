#!/usr/bin/env bash
# Agent Hook: Pre-Commit & Verification Guardrail

set -e

echo "🛡️ Running Agent Pre-Commit Verification Hook..."

# 1. Check for accidental secrets
if grep -rnE "(AIza[0-9A-Za-z-_]{35}|sk-[a-zA-Z0-9]{32,})" . --exclude-dir={.git,.venv,node_modules,brain} > /dev/null 2>&1; then
  echo "❌ CRITICAL: Suspected secret key detected in source code! Commit aborted."
  exit 1
fi

# 2. Check OpenAPI contract existence
if [ ! -f "openapi.yaml" ]; then
  echo "❌ Missing openapi.yaml contract!"
  exit 1
fi

echo "✅ All pre-commit guardrail checks passed."
exit 0
