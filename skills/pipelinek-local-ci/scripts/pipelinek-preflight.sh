#!/usr/bin/env bash
set -Eeuo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
printf 'pipelinek_preflight=1\n'
printf 'repo_root=%s\n' "$root"
printf 'pipeline_file=%s\n' "$([ -f "$root/pipeline.kts" ] && printf '%s' "$root/pipeline.kts" || printf '<missing>')"

if command -v java >/dev/null 2>&1; then
  printf 'java=%s\n' "$(command -v java)"
  java -version 2>&1 | head -n 1 | sed 's/^/java_version=/'
else
  printf 'java=<missing>\n'
fi

if command -v pipelinek >/dev/null 2>&1; then
  resolved="$(command -v pipelinek)"
  printf 'pipelinek_command=%s\n' "$resolved"
  printf 'pipelinek_realpath=%s\n' "$(readlink -f "$resolved" 2>/dev/null || printf '%s' "$resolved")"
  version_out="$(pipelinek version 2>&1 || true)"
  printf 'pipelinek_version=%s\n' "$(printf '%s' "$version_out" | head -n 1)"
else
  printf 'pipelinek_command=<missing>\n'
fi

if command -v mise >/dev/null 2>&1; then
  printf 'mise=present\n'
  printf 'mise_pipelinek=%s\n' "$(mise which pipelinek 2>/dev/null || printf '<unresolved>')"
else
  printf 'mise=absent\n'
fi

if command -v asdf >/dev/null 2>&1; then
  printf 'asdf=present\n'
  printf 'asdf_pipelinek=%s\n' "$(asdf which pipelinek 2>/dev/null || printf '<unresolved>')"
  printf 'asdf_current=%s\n' "$(asdf current pipelinek 2>/dev/null | tr '\n' ' ' || true)"
else
  printf 'asdf=absent\n'
fi

for f in mise.toml .mise.toml .tool-versions Jenkinsfile .gitlab-ci.yml; do
  [ -e "$root/$f" ] && printf 'project_marker=%s\n' "$f"
done
[ -d "$root/.github/workflows" ] && printf 'project_marker=.github/workflows\n'
printf 'manual_current=%s\n' "$(readlink -f "$HOME/.local/share/pipelinek/current" 2>/dev/null || printf '<none>')"
