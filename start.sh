#!/usr/bin/env sh
set -e

# Railway/Railpack start script — change to the backend directory and run gunicorn
# Uses PORT env var provided by Railway (defaults to 5000 if not set)
cd backend
: "${PORT:=5000}"
exec gunicorn --bind 0.0.0.0:${PORT} "app:create_app()"
