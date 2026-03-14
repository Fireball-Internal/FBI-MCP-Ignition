#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/dist"
OUTPUT="$SCRIPT_DIR/caldera-mcp.mcpb"

echo "Cleaning previous build..."
rm -rf "$BUILD_DIR" "$OUTPUT"
mkdir -p "$BUILD_DIR"

echo "Copying extension files..."
cp "$SCRIPT_DIR/manifest.json" "$BUILD_DIR/"
cp "$SCRIPT_DIR/package.json" "$BUILD_DIR/"

echo "Installing dependencies..."
cd "$BUILD_DIR"
npm install --production --no-package-lock
cd "$SCRIPT_DIR"

echo "Packing .mcpb..."
npx @anthropic-ai/mcpb pack "$BUILD_DIR" "$OUTPUT"

echo ""
echo "Built: $OUTPUT"
npx @anthropic-ai/mcpb info "$OUTPUT"
