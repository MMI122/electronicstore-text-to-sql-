
#!/usr/bin/env sh
set -e

# Railway/Railpack start script — install deps if needed, change to the backend
# directory and run gunicorn. Uses PORT env var provided by Railway (defaults
# to 5000 if not set).

# If gunicorn isn't available in the environment (Railpack may not install
# dependencies from a requirements.txt in a subdirectory), install deps first.
if ! command -v gunicorn >/dev/null 2>&1; then
	echo "gunicorn not found — installing dependencies from backend/requirements.txt"
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install --no-cache-dir -r backend/requirements.txt
fi

cd backend
: "${PORT:=5000}"
exec gunicorn --bind 0.0.0.0:${PORT} "app:create_app()"
