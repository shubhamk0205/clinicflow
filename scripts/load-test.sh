#!/usr/bin/env bash
# Generates traffic against the API so Grafana panels populate and the HPA has CPU to react to.
# Usage: URL=http://<ingress-host>/api/appointments REQUESTS=5000 CONCURRENCY=20 ./scripts/load-test.sh
set -euo pipefail
URL="${URL:-http://clinicflow.local/api/appointments}"
REQUESTS="${REQUESTS:-5000}"
CONCURRENCY="${CONCURRENCY:-20}"

echo "Sending $REQUESTS requests to $URL with concurrency $CONCURRENCY"
seq 1 "$REQUESTS" | xargs -P "$CONCURRENCY" -I{} curl -s -o /dev/null "$URL" || true
echo "Load test completed"
