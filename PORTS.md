# Port Configuration

## Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend Dashboard | http://localhost:3001 | Web UI for submitting jobs |
| API Documentation | http://localhost:8000/docs | FastAPI Swagger docs |
| API Health Check | http://localhost:8000/api/health | Health endpoint |
| Create Job | POST http://localhost:8000/api/jobs | API endpoint |
| Get Job Status | GET http://localhost:8000/api/jobs/\{id\} | API endpoint |

## Why Port 3001?

The frontend uses port **3001** on the host machine because:
- Port 3000 is commonly used by React, Next.js, and other dev servers
- Avoiding conflicts with existing applications
- Container internally uses port 3000, mapped to host port 3001

## Docker Compose Port Mapping

```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Host:Container
  
  api:
    ports:
      - "8000:8000"  # Host:Container
  
  redis:
    # No ports mapped - internal only
