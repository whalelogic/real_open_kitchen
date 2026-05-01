#!/bin/bash
# Run script for Open Kitchen application

export FLASK_APP=app
export FLASK_ENV=development
export FLASK_RUN_PORT=8080
export FLASK_RUN_HOST=0.0.0.0

echo "Starting Open Kitchen application..."
echo "Visit http://127.0.0.1:8080 or localhost:8080 in your browser"
echo "Press Ctrl+C to stop the server"
echo ""

# Run flask init-db to initialize the database if it doesn't exist
# if [ ! -f "instance/community_kitchen.db" ]; then
#     python3 -m flask init-db
# fi

python3 -m flask run

