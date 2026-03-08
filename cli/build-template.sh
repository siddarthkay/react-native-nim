#!/bin/bash
# Build the template directory for npm publishing.
# Rsyncs mobile-app/ into cli/template/ with build artifacts excluded.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
DEST="$SCRIPT_DIR/template"

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
  --exclude='libnim_core.a' \
  --exclude='main.h' \
  --exclude='nimbase.h' \
  --exclude='nim_core' \
  --exclude='nim_core.h' \
  --exclude='nim_core.json' \
  --exclude='*.o' \
  "$REPO_ROOT/mobile-app/" "$DEST/"

echo "Template built at $DEST ($(find "$DEST" -type f | wc -l | tr -d ' ') files)"
