#!/bin/bash

echo "=== Testing Job Processing System ==="
echo ""

# Test API health
echo "1. Testing API Health..."
curl -s http://localhost:8000/api/health | python3 -m json.tool
echo ""

# Create 3 jobs
echo "2. Creating 3 jobs..."
for i in {1..3}; do
    JOB_ID=$(curl -s -X POST http://localhost:8000/api/jobs | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
    echo "Created Job $i: $JOB_ID"
    JOB_IDS[$i]=$JOB_ID
done
echo ""

# Check each job status
echo "3. Checking job statuses..."
for JOB_ID in "${JOB_IDS[@]}"; do
    echo "Job $JOB_ID:"
    curl -s "http://localhost:8000/api/jobs/$JOB_ID" | python3 -m json.tool
    echo ""
done

# Wait for processing
echo "4. Waiting 5 seconds for worker to process..."
sleep 5

# Check final statuses
echo "5. Final job statuses after processing:"
for JOB_ID in "${JOB_IDS[@]}"; do
    STATUS=$(curl -s "http://localhost:8000/api/jobs/$JOB_ID" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")
    echo "Job $JOB_ID: $STATUS"
done

echo ""
echo "=== Test Complete ==="
echo "Frontend URL: http://localhost:3001"
echo "API Docs: http://localhost:8000/docs"
