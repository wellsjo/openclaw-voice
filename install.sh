#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 scripts/ensure_tts.py --install-only
