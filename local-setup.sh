#!/bin/bash

# Script to test the CI/CD pipeline locally

echo "=== Testing CI/CD Pipeline Locally ==="

# Stage 1: Lint
echo ""
echo "Stage 1: Linting..."
flake8 api/main.py --max-line-length=120 --ignore=E501,W503
flake8 worker/worker.py --max-line-length=120 --ignore=E501,W503
eslint frontend/app.js
hadolint api/Dockerfile
hadolint worker/Dockerfile
hadolint frontend/Dockerfile
echo "✅ Lint passed"

# Stage 2: Test
echo ""
echo "Stage 2: Running tests..."
pip install pytest pytest-cov fakeredis
cd api
pytest ../tests/test_api.py -v --cov=. --cov-report=term
cd ..
echo "✅ Tests passed"

# Stage 3: Build
echo ""
echo "Stage 3: Building images..."
docker build -t api:test ./api
docker build -t worker:test ./worker
docker build -t frontend:test ./frontend
echo "✅ Build passed"

# Stage 4: Security Scan
echo ""
echo "Stage 4: Security scan..."
trivy image api:test --severity CRITICAL --exit-code 0
trivy image worker:test --severity CRITICAL --exit-code 0
trivy image frontend:test --severity CRITICAL --exit-code 0
echo "✅ Security scan passed"

# Stage 5: Integration Test
echo ""
echo "Stage 5: Integration test..."
echo "REDIS_PASSWORD=test123" > .env
docker-compose up -d
sleep 10

python3 -c "
import requests, time
# Test API
r = requests.get('http://localhost:8000/api/health')
assert r.status_code == 200
# Create job
r = requests.post('http://localhost:8000/api/jobs')
job_id = r.json()['job_id']
# Wait for completion
for i in range(30):
    r = requests.get(f'http://localhost:8000/api/jobs/{job_id}')
    if r.json().get('status') == 'completed':
        print('Job completed')
        break
    time.sleep(1)
"

docker-compose down -v
echo "✅ Integration test passed"

echo ""
echo "🎉 All pipeline stages passed locally!"
