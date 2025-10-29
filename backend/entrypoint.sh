#!/bin/sh
set -e

echo "=== entrypoint: running database setup (if needed) ==="

# Run the setup script from the backend working directory
if [ -f "./setup_database.py" ]; then
  python ./setup_database.py
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "Database setup failed with exit code $rc"
    exit $rc
  fi
else
  echo "setup_database.py not found in $(pwd); skipping DB setup"
fi

echo "=== entrypoint: starting gunicorn ==="

# Exec gunicorn so signals propagate correctly
exec gunicorn --bind 0.0.0.0:${PORT:-5000} 'app:create_app()'
