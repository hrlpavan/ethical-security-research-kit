#!/usr/bin/env bash
# ==============================================================================
# verify_header.sh - Safe Harbor Header & Edge CDN Verification Script
# Usage: ./verify_header.sh <TARGET_URL> <HEADER_VALUE>
# Example: ./verify_header.sh https://www.amd.com "Intigriti-hrlpavan"
# ==============================================================================

set -euo pipefail

TARGET_URL="${1:-https://www.amd.com}"
HEADER_VALUE="${2:-Intigriti-hrlpavan}"
HEADER_NAME="X-Bug-Bounty"

echo "================================================================="
echo "[*] Safe Harbor Terminal Verification"
echo "[*] Target Endpoint: ${TARGET_URL}"
echo "[*] Injected Header: ${HEADER_NAME}: ${HEADER_VALUE}"
echo "================================================================="

# Force HTTP/1.1 and browser user-agent to prevent CDN HTTP/2 stream reset errors
RESPONSE=$(curl --http1.1 -s -I -L \
  -H "${HEADER_NAME}: ${HEADER_VALUE}" \
  -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "${TARGET_URL}")

echo ""
echo "[+] Received Response Headers from Edge CDN:"
echo "-----------------------------------------------------------------"
echo "${RESPONSE}" | head -n 25
echo "-----------------------------------------------------------------"

# Extract HTTP status
STATUS_CODE=$(echo "${RESPONSE}" | grep -E '^HTTP/' | tail -n 1 | awk '{print $2}')

if [[ "${STATUS_CODE}" == "200" ]]; then
  echo -e "\033[0;32m[SUCCESS] Target returned HTTP 200 OK. Header successfully processed by CDN.\033[0m"
elif [[ "${STATUS_CODE}" =~ ^3 ]]; then
  echo -e "\033[0;33m[REDIRECT] Target returned HTTP ${STATUS_CODE} redirect. Route is reachable.\033[0m"
elif [[ "${STATUS_CODE}" == "403" || "${STATUS_CODE}" == "401" ]]; then
  echo -e "\033[0;34m[PROTECTED] Target returned HTTP ${STATUS_CODE}. Endpoint enforces active authorization.\033[0m"
else
  echo -e "\033[0;37m[*] Target returned HTTP ${STATUS_CODE}.\033[0m"
fi
