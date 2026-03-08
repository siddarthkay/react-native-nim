#!/bin/bash
# Build the template directory for npm publishing.
# Copies templates/ into cli/templates/ with build artifacts excluded.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
DEST="$SCRIPT_DIR/templates"

rm -rf "$DEST"

rsync -a \
  --exclude='node_modules' \
  --exclude='.yarn' \
  --exclude='.git' \
  --exclude='build' \
  --exclude='.cxx' \
  --exclude='dist' \
  --exclude='__pycache__' \
  --exclude='.kotlin' \
  --exclude='cache_ios_sim' \
  --exclude='cache_android' \
  --exclude='.DS_Store' \
  --exclude='yarn.lock' \
  --exclude='*.log' \
  --exclude='Pods' \
  --exclude='.gradle' \
  "$REPO_ROOT/templates/" "$DEST/"

echo "Template built at $DEST ($(find "$DEST" -type f | wc -l | tr -d ' ') files)"
