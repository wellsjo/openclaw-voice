#!/bin/bash
set -e
cd "$(dirname "$0")"
exec python3 scripts/ensure_tts.py --foreground
