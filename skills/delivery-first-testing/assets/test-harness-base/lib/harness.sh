#!/usr/bin/env bash
# Source from a dedicated bash scenario (not an interactive shell).
# Reuses the runner, never the state of a previous acceptance session.

th_fail() { printf 'HARNESS_ERROR: %s\n' "$*" >&2; return 1; }

th_init() {
  [[ -z "${TH_SESSION_DIR:-}" ]] || { th_fail 'session already initialized'; return 2; }
  [[ -n "${TH_TARGET_ID:-}" ]] || { th_fail 'TH_TARGET_ID (commit or artifact digest) required'; return 2; }
  command -v timeout >/dev/null || { th_fail 'GNU timeout unavailable: BLOCKED'; return 2; }
  local lib_dir
  lib_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)" || return 2
  TH_HOME="$(cd -- "$lib_dir/.." && pwd -P)" || return 2
  TH_SESSIONS="$TH_HOME/.sessions"
  TH_REPORTS="$TH_HOME/.reports"
  (umask 077; mkdir -p -- "$TH_SESSIONS" "$TH_REPORTS") || return 2
  TH_SESSION_DIR="$(umask 077; mktemp -d "$TH_SESSIONS/run.XXXXXXXX")" || return 2
  TH_RUN_ID="${TH_SESSION_DIR##*/}"
  TH_LOGS="$TH_SESSION_DIR/logs"
  export TH_HOME TH_SESSION_DIR TH_RUN_ID TH_LOGS
  trap 'th_finalize "$?"' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  mkdir -p -- "$TH_LOGS" || return 2
  : > "$TH_SESSION_DIR/pgids"
  : > "$TH_SESSION_DIR/containers"
}

th_name_ok() { [[ "$1" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]]; }

th_capture() {
  local name="${1:-}"; shift || return 2
  th_name_ok "$name" || { th_fail "invalid scenario name: $name"; return 2; }
  (( $# > 0 )) || { th_fail 'missing command'; return 2; }
  local limit="${TH_TIMEOUT_SEC:-60}"
  [[ "$limit" =~ ^[1-9][0-9]*$ ]] || { th_fail 'TH_TIMEOUT_SEC must be a positive integer'; return 2; }
  timeout -k 2 "${limit}s" "$@" > "$TH_LOGS/$name.log" 2>&1 || {
    local code=$?
    printf 'Scenario %s failed (exit %s). Output:\n' "$name" "$code" >&2
    cat -- "$TH_LOGS/$name.log" >&2
    return "$code"
  }
}

th_assert_nonempty() {
  [[ -s "$1" ]] || { th_fail "empty or missing output: $1"; return 1; }
}

th_assert_contains() {
  local file="$1" expected="$2"
  grep -Fq -- "$expected" "$file" || { th_fail "expected marker not found: $expected"; return 1; }
}

th_wait_until() {
  local limit="$1"; shift
  [[ "$limit" =~ ^[1-9][0-9]*$ ]] && (( $# > 0 )) || { th_fail 'usage: th_wait_until seconds command args'; return 2; }
  local deadline=$(( $(date +%s) + limit ))
  until "$@" >/dev/null 2>&1; do
    (( $(date +%s) < deadline )) || { th_fail 'readiness timed out'; return 124; }
    sleep 0.2
  done
}

th_start_service() {
  local name="${1:-}"; shift || return 2
  th_name_ok "$name" && (( $# > 0 )) || { th_fail 'usage: th_start_service name cmd args'; return 2; }
  command -v setsid >/dev/null || { th_fail 'setsid unavailable: BLOCKED'; return 2; }
  setsid "$@" > "$TH_LOGS/$name.log" 2>&1 &
  local pgid=$!
  printf '%s\n' "$pgid" >> "$TH_SESSION_DIR/pgids"
  TH_LAST_SERVICE_PID="$pgid"
}

th_register_container() {
  local engine="$1" id="$2"
  [[ "$engine" == podman || "$engine" == docker ]] || { th_fail 'unsupported container engine'; return 2; }
  [[ "$id" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]] || { th_fail 'invalid container identifier'; return 2; }
  command -v "$engine" >/dev/null || { th_fail "$engine unavailable: BLOCKED"; return 2; }
  printf '%s %s\n' "$engine" "$id" >> "$TH_SESSION_DIR/containers"
}

th_finalize() {
  local status="$1"; trap - EXIT INT TERM
  [[ -n "${TH_SESSION_DIR:-}" && -d "$TH_SESSION_DIR" ]] || return 0
  local engine id pgid report
  while read -r engine id; do
    [[ -n "$engine" ]] && "$engine" rm -f -- "$id" >/dev/null 2>&1 || :
  done < "$TH_SESSION_DIR/containers"
  while IFS= read -r pgid; do
    [[ "$pgid" =~ ^[1-9][0-9]*$ ]] && kill -TERM -- "-$pgid" >/dev/null 2>&1 || :
  done < "$TH_SESSION_DIR/pgids"
  # Bounded grace period, then remove only process groups started by this session.
  if [[ -s "$TH_SESSION_DIR/pgids" ]]; then sleep 0.2; fi
  while IFS= read -r pgid; do
    if [[ "$pgid" =~ ^[1-9][0-9]*$ ]]; then
      kill -KILL -- "-$pgid" >/dev/null 2>&1 || :
      wait "$pgid" 2>/dev/null || :
    fi
  done < "$TH_SESSION_DIR/pgids"
  printf 'run_id=%s\ntarget_id=%s\nexit_status=%s\nscenario=%s\n' \
    "$TH_RUN_ID" "$TH_TARGET_ID" "$status" "${TH_SCENARIO:-unspecified}" > "$TH_SESSION_DIR/receipt.txt"
  report="$TH_REPORTS/$TH_RUN_ID"
  if ! (umask 077; cp -R -- "$TH_SESSION_DIR" "$report"); then
    printf 'HARNESS_ERROR: evidence copy failed\n' >&2
    [[ "$status" -ne 0 ]] || status=2
  fi
  # The only path eligible for deletion is the generated mktemp session inside this harness.
  case "$TH_SESSION_DIR" in
    "$TH_SESSIONS"/run.*) rm -rf -- "$TH_SESSION_DIR" || status=2 ;;
    *) printf 'HARNESS_ERROR: unsafe cleanup path\n' >&2; status=2 ;;
  esac
  exit "$status"
}
