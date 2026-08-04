#!/usr/bin/env bash
# verify_checksums.sh — Verify SHA-256 registry against a dataset directory
# Usage: sh verify_checksums.sh <dataset_root>
# Exit 0: all files match. Exit 1: any mismatch or missing file.

set -euo pipefail

DATASET_ROOT="${1:?Usage: verify_checksums.sh <dataset_root>}"
REGISTRY="$DATASET_ROOT/SHA256SUMS"

if [[ ! -f "$REGISTRY" ]]; then
  echo "ERROR: checksum registry not found: $REGISTRY" >&2
  exit 1
fi

failures=0
total=0

while IFS= read -r line; do
  # skip blanks and comments
  [[ -z "$line" || "$line" == \#* ]] && continue
  expected_hash="${line%%  *}"
  rel_path="${line#*  }"
  file_path="$DATASET_ROOT/$rel_path"
  total=$((total + 1))

  if [[ ! -f "$file_path" ]]; then
    echo "MISSING: $rel_path" >&2
    failures=$((failures + 1))
    continue
  fi

  actual_hash=$(sha256sum "$file_path" | awk '{print $1}')
  if [[ "$actual_hash" != "$expected_hash" ]]; then
    echo "MISMATCH: $rel_path (expected $expected_hash, got $actual_hash)" >&2
    failures=$((failures + 1))
  fi
done < "$REGISTRY"

echo "Verified $total files, $failures failure(s)."
[[ $failures -eq 0 ]]
