#!/usr/bin/env bash
set -Eeuo pipefail
# Example: TH_TARGET_ID=<digest-or-sha> bash test-harness/examples/cli-version.sh /path/to/binary --version
[[ $# -gt 0 ]] || { printf 'usage: %s executable [arguments...]\n' "$0" >&2; exit 2; }
source "$(dirname -- "$0")/../lib/harness.sh"
TH_SCENARIO=cli-version
th_init
th_capture version "$@"
th_assert_nonempty "$TH_LOGS/version.log"
