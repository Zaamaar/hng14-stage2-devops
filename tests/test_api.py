import sys
import os
from unittest.mock import patch, MagicMock

# -------------------------------------------------------
# We must patch redis.Redis BEFORE importing main.py
# because main.py calls get_redis_connection() at import
# time and will sys.exit(1) if Redis is not available.
# -------------------------------------------------------

mock_redis_instance = MagicMock()
mock_redis_instance.ping.return_value = True
mock_redis_instance.lpush.return_value = 1
mock_redis_instance.hset.return_value = True
mock_redis_instance.hget.return_value = "queued"

with patch('redis.Redis', return_value=mock_redis_instance):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
    import main as main_module
    from main import app

from fastapi.testclient import TestClient

client = TestClient(app)


# -------------------------------------------------------
# TEST 1 — health check returns 200 and healthy status
# -------------------------------------------------------
def test_health_check():
    """Health check endpoint must return 200 with status healthy."""
    mock_redis_instance.ping.return_value = True
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"


# -------------------------------------------------------
# TEST 2 — creating a job returns a job_id
# -------------------------------------------------------
def test_create_job_returns_id():
    """POST /api/jobs must return a job_id."""
    mock_redis_instance.lpush.return_value = 1
    mock_redis_instance.hset.return_value = True
    response = client.post("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) > 0


# -------------------------------------------------------
# TEST 3 — getting a job that exists returns its status
# -------------------------------------------------------
def test_get_existing_job():
    """GET /api/jobs/{id} must return status for a known job."""
    mock_redis_instance.hget.return_value = "queued"
    response = client.get("/api/jobs/test-job-123")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "queued"
    assert data.get("job_id") == "test-job-123"


# -------------------------------------------------------
# TEST 4 — getting a job that does not exist returns 404
# -------------------------------------------------------
def test_get_missing_job_returns_404():
    """GET /api/jobs/{id} must return 404 when job does not exist."""
    mock_redis_instance.hget.return_value = None
    response = client.get("/api/jobs/does-not-exist")
    assert response.status_code == 404


# -------------------------------------------------------
# TEST 5 — job status progresses correctly (mock side_effect)
# -------------------------------------------------------
def test_job_status_progression():
    """Job status should reflect whatever Redis returns."""
    mock_redis_instance.hget.side_effect = ["queued", "processing", "completed"]
    for expected in ["queued", "processing", "completed"]:
        response = client.get("/api/jobs/some-job-id")
        assert response.status_code == 200
        assert response.json().get("status") == expected
    mock_redis_instance.hget.side_effect = None
