#!/usr/bin/env bash
set -Eeuo pipefail
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$root"

printf 'repo_root=%s\n' "$root"
for f in gradlew mvnw package.json pnpm-lock.yaml yarn.lock pyproject.toml uv.lock poetry.lock Cargo.toml go.mod Makefile justfile pipeline.kts Jenkinsfile .gitlab-ci.yml; do
  [ -e "$f" ] && printf 'detected=%s\n' "$f"
done
[ -d .github/workflows ] && {
  printf 'detected=.github/workflows\n'
  find .github/workflows -maxdepth 1 -type f -print | sort | sed 's/^/ci_file=/'
}
[ -f package.json ] && printf 'inspect_next=package.json:scripts\n'
[ -f Cargo.toml ] && printf 'inspect_next=Cargo.toml:workspace/features\n'
[ -f pyproject.toml ] && printf 'inspect_next=pyproject.toml:tooling\n'
[ -f Makefile ] && printf 'inspect_next=Makefile:targets\n'
[ -f justfile ] && printf 'inspect_next=justfile:recipes\n'
