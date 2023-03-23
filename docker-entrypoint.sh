#!/bin/sh
# docker-entrypoint.sh

# Install any new dependencies
pip install --no-cache-dir -r requirements.txt

# Run the application
exec python main.py