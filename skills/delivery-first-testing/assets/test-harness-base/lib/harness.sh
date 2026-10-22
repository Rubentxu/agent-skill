#!/usr/bin/env bash
# Source from a dedicated bash scenario (not an interactive shell).
# Reuses the runner, never the state of a previous acceptance session.

th_fail() { printf 'HARNESS_ERROR: %s\n' "$*" >&2; return 1; }

th_init() {
  [[ -z "${TH_SESSION_DIR:-}" ]] || { th_fail 'session already initialized'; return 2; }
  [[ "${TH_TARGET_ID:-}" =~ ^[a-zA-Z0-9._:/+-]+$ ]] || {
    th_fail 'TH_TARGET_ID must be a nonempty single-line commit or artifact identifier'; return 2;
  }
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

# Linux start time in /proc/<pid>/stat field 22 (field 20 after the command).
# A PID without its birth time is not proof of ownership.
th_process_birth() {
  local stat
  [[ -r "/proc/$1/stat" ]] || return 1
  stat="$(cat "/proc/$1/stat" 2>/dev/null)" || return 1
  [[ "$stat" == *") "* ]] || return 1
  printf '%s\n' "${stat##*) }" | awk '{print $20}'
}

th_start_service() {
  local name="${1:-}"; shift || return 2
  th_name_ok "$name" && (( $# > 0 )) || { th_fail 'usage: th_start_service name cmd args'; return 2; }
  command -v setsid >/dev/null || { th_fail 'setsid unavailable: BLOCKED'; return 2; }
  setsid "$@" > "$TH_LOGS/$name.log" 2>&1 &
  local pgid=$! birth
  birth="$(th_process_birth "$pgid" || true)"
  if [[ -z "$birth" ]]; then
    # The process may have died before registration: no ownership proof.
    th_fail "service $name exited before its process identity could be captured"
    return 2
  fi
  printf '%s %s\n' "$pgid" "$birth" >> "$TH_SESSION_DIR/pgids"
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
  local status="$1" cleanup_failed=0; trap - EXIT INT TERM
  [[ -n "${TH_SESSION_DIR:-}" && -d "$TH_SESSION_DIR" ]] || return 0
  local engine id pgid birth observed report
  while read -r engine id; do
    [[ -n "$engine" ]] || continue
    if ! "$engine" rm -f -- "$id" >/dev/null 2>&1; then
      printf 'HARNESS_ERROR: failed to remove owned %s container %s\n' "$engine" "$id" >&2
      cleanup_failed=1
    fi
  done < "$TH_SESSION_DIR/containers"

  # Only signal a group while its original leader still matches /proc start time.
  # A reused PID must never allow us to signal a stranger's process group.
  while read -r pgid birth; do
    [[ "$pgid" =~ ^[1-9][0-9]*$ && "$birth" =~ ^[0-9]+$ ]] || { cleanup_failed=1; continue; }
    observed="$(th_process_birth "$pgid" || true)"
    if [[ "$observed" == "$birth" ]]; then
      kill -TERM -- "-$pgid" >/dev/null 2>&1 || :
    fi
  done < "$TH_SESSION_DIR/pgids"
  if [[ -s "$TH_SESSION_DIR/pgids" ]]; then sleep 0.2; fi

  while read -r pgid birth; do
    [[ "$pgid" =~ ^[1-9][0-9]*$ && "$birth" =~ ^[0-9]+$ ]] || continue
    observed="$(th_process_birth "$pgid" || true)"
    if [[ "$observed" == "$birth" ]]; then
      kill -KILL -- "-$pgid" >/dev/null 2>&1 || :
      wait "$pgid" 2>/dev/null || :
    fi
    # If the leader vanished while children stayed, do NOT signal an
    # unverified group. Report incomplete teardown rather than false PASS.
    if kill -0 -- "-$pgid" >/dev/null 2>&1; then
      printf 'HARNESS_ERROR: process group %s remains or identity cannot be verified\n' "$pgid" >&2
      cleanup_failed=1
    fi
  done < "$TH_SESSION_DIR/pgids"

  [[ "$cleanup_failed" -eq 0 || "$status" -ne 0 ]] || status=2
  printf 'run_id=%s\ntarget_id=%s\nexit_status=%s\nscenario=%s\ncleanup=%s\n' \
    "$TH_RUN_ID" "$TH_TARGET_ID" "$status" "${TH_SCENARIO:-unspecified}" \
    "$([[ "$cleanup_failed" -eq 0 ]] && echo complete || echo incomplete)" > "$TH_SESSION_DIR/receipt.txt"
  report="$TH_REPORTS/$TH_RUN_ID"
  if ! (umask 077; cp -R -- "$TH_SESSION_DIR" "$report"); then
    printf 'HARNESS_ERROR: evidence copy failed\n' >&2
    [[ "$status" -ne 0 ]] || status=2
  fi
  case "$TH_SESSION_DIR" in
    "$TH_SESSIONS"/run.*) rm -rf -- "$TH_SESSION_DIR" || status=2 ;;
    *) printf 'HARNESS_ERROR: unsafe cleanup path\n' >&2; status=2 ;;
  esac
  exit "$status"
}
