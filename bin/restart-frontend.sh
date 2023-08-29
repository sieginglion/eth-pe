#!/usr/bin/env bash

set -euo pipefail

pkill -f streamlit
sleep 1
poetry run -- streamlit run --server.port 80 --theme.base dark frontend/main.py 1>frontend.log 2>&1 &
