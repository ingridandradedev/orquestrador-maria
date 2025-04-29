#!/bin/bash
exec uvicorn app.main:app \
  --host 0.0.0.0 --port 8002 \
  --timeout-keep-alive 0    # zero = sem limite