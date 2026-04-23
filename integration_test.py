import requests
import time
import sys

def test_integration():
    print("=" * 50)
    print("Starting Integration Tests")
    print("=" * 50)
    
    # Test API health
    print("\n1. Testing API health...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        assert response.status_code == 200
        assert response.json().get("status") == "healthy"
        print("   ✅ API health check passed")
    except Exception as e:
        print(f"   ❌ API health check failed: {e}")
        return False
    
    # Test frontend
    print("\n2. Testing frontend...")
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        assert response.status_code == 200
        print("   ✅ Frontend is accessible")
    except Exception as e:
        print(f"   ❌ Frontend test failed: {e}")
        return False
    
    # Create a job
    print("\n3. Creating test job...")
    try:
        response = requests.post("http://localhost:8000/api/jobs", timeout=5)
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        print(f"   ✅ Job created: {job_id}")
    except Exception as e:
        print(f"   ❌ Job creation failed: {e}")
        return False
    
    # Poll until completion
    print("\n4. Waiting for job to complete...")
    for attempt in range(30):
        try:
            response = requests.get(f"http://localhost:8000/api/jobs/{job_id}", timeout=5)
            status = response.json().get("status")
            print(f"   Attempt {attempt + 1}/30: Status = {status}")
            
            if status == "completed":
                print("   ✅ Job completed successfully!")
                return True
            elif status == "failed":
                print("   ❌ Job failed")
                return False
                
            time.sleep(2)
        except Exception as e:
            print(f"   ⚠️  Error checking status: {e}")
            time.sleep(2)
    
    print("   ❌ Job did not complete within timeout (60 seconds)")
    return False

if __name__ == "__main__":
    success = test_integration()
    print("\n" + "=" * 50)
    print("Integration Tests: PASSED" if success else "Integration Tests: FAILED")
    print("=" * 50)
    sys.exit(0 if success else 1)
