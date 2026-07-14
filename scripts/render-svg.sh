#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 INPUT.svg OUTPUT.png" >&2
  exit 2
fi

input=$1
output=$2

if [[ ! -f "$input" ]]; then
  echo "SVG not found: $input" >&2
  exit 1
fi

mkdir -p "$(dirname "$output")"

if command -v resvg >/dev/null 2>&1; then
  resvg "$input" "$output"
elif command -v rsvg-convert >/dev/null 2>&1; then
  rsvg-convert --format=png --output="$output" "$input"
elif command -v inkscape >/dev/null 2>&1; then
  inkscape "$input" --export-type=png --export-filename="$output"
elif command -v magick >/dev/null 2>&1; then
  magick -background none "$input" "$output"
elif command -v convert >/dev/null 2>&1; then
  convert -background none "$input" "$output"
else
  echo "No SVG renderer found." >&2
  echo "Install resvg, librsvg (rsvg-convert), Inkscape, or ImageMagick." >&2
  exit 1
fi

echo "Rendered $output"
