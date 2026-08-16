#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-/home/vincenzo/Development/PySwitch/content}"
TARGET_DIR="${2:-/media/${USER:-$(id -un)}/MIDICAPTAIN}"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

if [ ! -d "$SOURCE_DIR" ]; then
  fail "Source directory not found: $SOURCE_DIR"
fi

echo "[1/4] Clean destination folder: $TARGET_DIR"
if ! mkdir -p "$TARGET_DIR" 2>/dev/null; then
  fail "Cannot create destination folder: $TARGET_DIR. Check permissions or run with sudo."
fi
if ! find "$TARGET_DIR" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} + 2>/dev/null; then
  fail "Cannot clean destination folder: $TARGET_DIR. Check permissions or run with sudo."
fi

echo "[2/4] Copy runtime Python files"
for file in \
  boot.py \
  code.py \
  config.py \
  communication.py \
  communication_gx100.py \
  display.py \
  inputs.py \
  inputs_gx100.py \
  wallpaper.bmp
 do
  if [ ! -f "$SOURCE_DIR/$file" ]; then
    fail "Missing required source file: $SOURCE_DIR/$file"
  fi
  if ! cp -a "$SOURCE_DIR/$file" "$TARGET_DIR/"; then
    fail "Copy failed for $file to $TARGET_DIR. Check disk space or permissions."
  fi
done

echo "[3/4] Copy required fonts and libraries"
if ! mkdir -p "$TARGET_DIR/fonts" 2>/dev/null; then
  fail "Cannot create fonts folder inside $TARGET_DIR. Check permissions."
fi
if ! cp -a "$SOURCE_DIR"/fonts/*.pcf "$TARGET_DIR"/fonts/ 2>/dev/null; then
  fail "Failed to copy font files from $SOURCE_DIR/fonts. Check that the .pcf files exist."
fi

if ! mkdir -p "$TARGET_DIR/lib" 2>/dev/null; then
  fail "Cannot create lib folder inside $TARGET_DIR. Check permissions."
fi
for entry in \
  functools.py \
  adafruit_bitmap_font \
  adafruit_display_shapes \
  adafruit_display_text \
  adafruit_hid \
  adafruit_midi \
  adafruit_misc \
  pymidibridge \
  pyswitch
 do
  if [ ! -e "$SOURCE_DIR/lib/$entry" ]; then
    fail "Missing required library entry: $SOURCE_DIR/lib/$entry"
  fi
  if ! cp -a "$SOURCE_DIR/lib/$entry" "$TARGET_DIR/lib/"; then
    fail "Copy failed for $entry. Check disk space or permissions."
  fi
done

echo "[4/4] Remove non-runtime files and cache"
if ! find "$TARGET_DIR" \( -type d -name '__pycache__' -o -type d -name 'test' -o -type d -name 'tests' \) -prune -exec rm -rf {} + 2>/dev/null; then
  fail "Failed while removing cache/test folders from $TARGET_DIR. Check permissions."
fi
if ! find "$TARGET_DIR" -type f \( -name '*.md' -o -name '*.txt' -o -name '*.rst' -o -name '*.json' -o -name '*.yaml' -o -name '*.yml' -o -name '*.toml' -o -name '*.ini' -o -name '*.cfg' -o -name '*.php' -o -name '*.svg' -o -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.gif' -o -name '*.webp' -o -name '*.pdf' -o -name '*.zip' -o -name '*.gz' -o -name '*.tar' -o -name '*.xz' \) -delete 2>/dev/null; then
  fail "Failed while removing non-runtime files from $TARGET_DIR. Check permissions."
fi

printf '\nCopied minimal PySwitch firmware to: %s\n' "$TARGET_DIR"
printf 'Key files present:\n'
ls -1 "$TARGET_DIR" | sort | head -n 20
