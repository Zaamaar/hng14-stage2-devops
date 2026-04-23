#!/bin/bash

echo "Running local integration test..."

# Start services
docker-compose up -d
sleep 10

# Run integration test
python3 integration_test.py
RESULT=$?

# Clean up
docker-compose down -v

exit $RESULT
