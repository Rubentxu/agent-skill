#!/usr/bin/env bash
set -Eeuo pipefail
root="$(cd "$(dirname "$0")/.." && pwd -P)"
work="$(mktemp -d)"
trap 'rm -rf -- "$work"' EXIT
cp -R "$root/assets/test-harness-base" "$work/test-harness"

run=(bash "$work/test-harness/examples/cli-version.sh")
TH_TARGET_ID=abc123 "${run[@]}" /bin/echo v1
[[ $(find "$work/test-harness/.sessions" -mindepth 1 -maxdepth 1 -type d | wc -l) -eq 0 ]]
[[ $(grep -l 'exit_status=0' "$work/test-harness/.reports"/*/receipt.txt | wc -l) -eq 1 ]]
if TH_TARGET_ID=abc123 "${run[@]}" /bin/false 2>/dev/null; then
  echo 'false green' >&2; exit 1
fi
[[ $(grep -l 'exit_status=1' "$work/test-harness/.reports"/*/receipt.txt | wc -l) -eq 1 ]]
if TH_TARGET_ID=abc123 TH_TIMEOUT_SEC=1 "${run[@]}" /bin/sleep 2 2>/dev/null; then
  echo 'timeout false green' >&2; exit 1
fi
[[ $(grep -l 'exit_status=124' "$work/test-harness/.reports"/*/receipt.txt | wc -l) -eq 1 ]]
if "${run[@]}" /bin/true 2>/dev/null; then
  echo 'missing target accepted' >&2; exit 1
fi
bad_id="$(printf 'abc\nexit_status=0')"
if TH_TARGET_ID="$bad_id" "${run[@]}" /bin/true 2>/dev/null; then
  echo 'multiline identity accepted' >&2; exit 1
fi
[[ $(find "$work/test-harness/.sessions" -mindepth 1 -maxdepth 1 | wc -l) -eq 0 ]]

# No service process or its process group may remain after a successful cycle.
cat > "$work/test-harness/examples/service.sh" <<'SVC'
#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/../lib/harness.sh"
TH_SCENARIO=service
th_init
th_start_service sleeper /bin/sleep 100
printf '%s\n' "$TH_LAST_SERVICE_PID" > "$TH_HOME/sleeper.pid"
kill -0 "$TH_LAST_SERVICE_PID"
SVC
TH_TARGET_ID=abc123 bash "$work/test-harness/examples/service.sh"
pid=$(cat "$work/test-harness/sleeper.pid")
if kill -0 "$pid" 2>/dev/null; then
  echo 'worker orphaned' >&2; exit 1
fi

# A simulated OCI failure is NOT success: receipt and exit must name failure.
mkdir -p "$work/fakebin"
cat > "$work/fakebin/docker" <<'FAKE'
#!/usr/bin/env bash
[[ "${1:-}" == rm ]] && exit 31
exit 0
FAKE
chmod +x "$work/fakebin/docker"
cat > "$work/test-harness/examples/container.sh" <<'CTR'
#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "$0")/../lib/harness.sh"
TH_SCENARIO=container-cleanup
th_init
th_register_container docker owned-canary
CTR
if TH_TARGET_ID=abc123 PATH="$work/fakebin:$PATH" bash "$work/test-harness/examples/container.sh" 2>/dev/null; then
  echo 'failed cleanup reported as green' >&2; exit 1
fi
[[ $(grep -l 'cleanup=incomplete' "$work/test-harness/.reports"/*/receipt.txt | wc -l) -eq 1 ]]
[[ $(grep -l 'exit_status=2' "$work/test-harness/.reports"/*/receipt.txt | wc -l) -eq 1 ]]
printf 'harness lifecycle checks passed\n'
