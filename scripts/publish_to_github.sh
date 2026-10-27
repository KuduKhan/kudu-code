#!/usr/bin/env bash
# Run AFTER creating an EMPTY repo named kudu-code under KuduKhan.
# Pushing milestones in succession preserves chronological version transitions.
set -euo pipefail
cd "$(dirname "$0")/.."
TARGET="https://github.com/KuduKhan/kudu-code.git"
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "$TARGET"
fi
ACTUAL="$(git remote get-url origin)"
if [[ "$ACTUAL" == *.bundle ]]; then
  git remote set-url origin "$TARGET"
  ACTUAL="$TARGET"
fi
if [[ "$ACTUAL" != "$TARGET" ]]; then
  echo "Refusing push: origin differs from approved target ($TARGET)." >&2
  exit 1
fi
if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
  echo "Refusing sequential push: main already exists on GitHub. Review and reconcile manually." >&2
  exit 1
fi
for v in v0.1.0 v0.2.0 v0.3.0 v0.4.0 v0.5.0 v0.6.0 v0.7.0 v0.8.0 v0.9.0 v1.0.0-preview; do
  echo "Publishing $v ..."
  git push origin "refs/tags/$v:refs/heads/main"
  git push origin "refs/tags/$v:refs/tags/$v"
done
echo 'Milestone history published. Inspect GitHub checks before deploying.'
