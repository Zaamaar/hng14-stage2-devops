# FIXES.md

## Issue #1
**File:** `api/main.py`
**Line:** 9
**Problem:** Redis connection hardcoded to `host="localhost"` which fails inside Docker containers because localhost refers to the container's own network namespace, not the Redis container.
**Change:** Changed to `host=os.getenv("REDIS_HOST", "redis")` and added environment variable configuration with fallback value.

## Issue #2
**File:** `api/main.py`
**Line:** 1
**Problem:** Missing `load_dotenv()` function call to read environment variables from the `.env` file. Environment variables from `.env` were not being loaded into the application.
**Change:** Added `from dotenv import load_dotenv` at the top and called `load_dotenv()` immediately after imports.

## Issue #3
**File:** `api/main.py`
**Line:** 14-18
**Problem:** No CORS middleware configured. When frontend runs on port 3001 and backend on port 8000, the browser blocks requests due to same-origin policy, causing CORS errors.
**Change:** Added `CORSMiddleware` from fastapi.middleware.cors with `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, and `allow_headers=["*"]`.

## Issue #4
**File:** `api/main.py`
**Line:** 14
**Problem:** API endpoints were defined as `/jobs` and `/jobs/{job_id}` without the `/api` prefix, causing 404 errors when frontend called `/api/jobs` and `/api/jobs/{id}`.
**Change:** Changed route decorators to `@app.post("/api/jobs")` and `@app.get("/api/jobs/{job_id}")` to match frontend expectations.

## Issue #5
**File:** `api/main.py`
**Line:** 20
**Problem:** The `r.hget()` method returns bytes that need decoding with `.decode()`, and there was no proper error handling for missing keys. The endpoint returned a string instead of proper HTTP status code.
**Change:** Set `decode_responses=True` in Redis connection to automatically handle string conversion, and changed error response to `raise HTTPException(status_code=404, detail="Job not found")`.

## Issue #6
**File:** `api/main.py`
**Line:** 30-34
**Problem:** No health check endpoint for container orchestration. Docker needs a health check to verify the service is ready to accept traffic.
**Change:** Added `/api/health` endpoint that calls `r.ping()` to verify Redis connectivity and returns `{"status": "healthy", "redis": "connected"}` or raises 503 if Redis is unavailable.

## Issue #7
**File:** `api/requirements.txt`
**Line:** N/A
**Problem:** Missing `python-dotenv` dependency which is required to load the `.env` file.
**Change:** Added `python-dotenv` to the requirements.txt file.

## Issue #8
**File:** `api/Dockerfile`
**Line:** N/A (file was missing)
**Problem:** No Dockerfile existed for the API service, making it impossible to containerize.
**Change:** Created a multi-stage Dockerfile with builder stage for dependencies, final stage with Python 3.11-slim, installed curl for healthcheck, created non-root user (appuser, UID 1001), added HEALTHCHECK instruction, and configured CMD to run uvicorn.

## Issue #9
**File:** `worker/worker.py`
**Line:** 7
**Problem:** Redis connection uses `host="localhost"` which fails when worker runs in a separate Docker container because localhost is not the Redis host.
**Change:** Changed to use environment variables: `host=os.getenv("REDIS_HOST", "redis")`, `port=int(os.getenv("REDIS_PORT", 6379))`, and `password=os.getenv("REDIS_PASSWORD", None)`.

## Issue #10
**File:** `worker/worker.py`
**Line:** 13-20
**Problem:** No connection retry logic. If Redis isn't ready when the worker starts (race condition), the worker crashes immediately with ConnectionError.
**Change:** Added a retry loop with 10 attempts and 3-second delays between attempts, with a `r.ping()` test to verify connection before entering main loop.

## Issue #11
**File:** `worker/worker.py`
**Line:** 17
**Problem:** The worker has no graceful shutdown handling for SIGTERM or SIGINT signals. When Docker stops the container, the worker is killed mid-process.
**Change:** Added a `GracefulKiller` class with signal handlers for SIGINT and SIGTERM, and modified the main loop to check `killer.kill_now` flag before each iteration.

## Issue #12
**File:** `worker/worker.py`
**Line:** 25-30
**Problem:** No "processing" status update. Jobs went directly from "queued" to "completed" without indicating they were being worked on.
**Change:** Added `r.hset(f"job:{job_id}", "status", "processing")` at the beginning of the `process_job()` function before the 2-second work simulation.

## Issue #13
**File:** `worker/requirements.txt`
**Line:** N/A
**Problem:** Missing `python-dotenv` dependency for loading environment variables from `.env` file.
**Change:** Added `python-dotenv` to worker/requirements.txt.

## Issue #14
**File:** `worker/Dockerfile`
**Line:** N/A (file was missing)
**Problem:** No Dockerfile existed for the worker service.
**Change:** Created Dockerfile with Python 3.11-slim, created non-root user (appuser, UID 1001), copied requirements.txt and installed dependencies, copied worker.py, added HEALTHCHECK instruction, and set CMD to run worker.py.

## Issue #15
**File:** `frontend/app.js`
**Line:** 6
**Problem:** Syntax error - there was a backslash character `\` at the end of line 6 after the semicolon, causing Node.js to throw "SyntaxError: Invalid or unexpected token".
**Change:** Removed the backslash character from the end of line 6 so the line reads `const API_URL = process.env.API_URL || "http://api:8000"\;`

## Issue #16
**File:** `frontend/app.js`
**Line:** 7
**Problem:** `API_URL` hardcoded to `"http://localhost:8000"` which fails when frontend runs in a Docker container and needs to communicate with the backend container.
**Change:** Changed to `process.env.API_URL || "http://api:8000"` to use environment variable with fallback to Docker service name.

## Issue #17
**File:** `frontend/app.js`
**Line:** 10
**Problem:** Frontend POST endpoint was `/submit` but backend expects `/api/jobs`, causing 404 errors.
**Change:** Changed to `app.post\('/api/submit', ...)` and updated the axios call to `${API_URL}/api/jobs`.

## Issue #18
**File:** `frontend/app.js`
**Line:** 17
**Problem:** Frontend GET endpoint was `/status/:id` but backend expects `/api/jobs/{id}`, causing 404 errors.
**Change:** Changed to `app.get('/api/status/:id', ...)` and updated the axios call to `${API_URL}/api/jobs/${req.params.id}`.

## Issue #19
**File:** `frontend/views/index.html`
**Line:** 36
**Problem:** The `submitJob()` function called `fetch('/submit', { method: 'POST' })` which doesn't match the frontend's API endpoint.
**Change:** Changed to `fetch('/api/submit', { method: 'POST' })` to match the corrected frontend route.

## Issue #20
**File:** `frontend/views/index.html`
**Line:** 39
**Problem:** The `pollJob(id)` function called `fetch(`/status/${id}`)` which doesn't match the frontend's API endpoint.
**Change:** Changed to `fetch(`/api/status/${id}`)` to match the corrected frontend route.

## Issue #21
**File:** `frontend/views/index.html`
**Line:** 45-48
**Problem:** Infinite polling with no timeout or maximum retry limit. If a job never completes (e.g., worker dies), the frontend would poll forever.
**Change:** Added `MAX_POLL_ATTEMPTS = 30` constant and `pollAttempts` object to track retries per job. If max attempts exceeded, stops polling and shows "timeout" status.

## Issue #22
**File:** `frontend/views/index.html`
**Line:** 36-50
**Problem:** No error handling for failed fetch requests. Network errors or server errors would crash the polling mechanism.
**Change:** Added try-catch blocks around all fetch calls, with error state rendering and retry with longer delay (5 seconds instead of 2).

## Issue #23
**File:** `frontend/Dockerfile`
**Line:** N/A (file was missing)
**Problem:** No Dockerfile existed for the frontend service.
**Change:** Created Dockerfile with node:18-alpine, created non-root user (nodeuser, UID 1001), copied package.json and ran `npm ci --only=production`, copied application code, added HEALTHCHECK instruction, and set CMD to run app.js.

## Issue #24
**File:** `.env` (root directory)
**Line:** 1
**Problem:** Redis password was hardcoded in plaintext and would be committed to version control, exposing sensitive credentials.
**Change:** Created `.env.example` template file with placeholder values, added `.env` to `.gitignore`, and updated documentation to show how to set the password via environment variable.

## Issue #25
**File:** `.gitignore` (root directory)
**Line:** N/A (file was missing)
**Problem:** No .gitignore file existed, which would allow sensitive files (.env, node_modules, __pycache__, etc.) to be accidentally committed to version control.
**Change:** Created .gitignore with entries for .env, .env.local, __pycache__, *.pyc, node_modules, package-lock.json, *.log, .DS_Store, and secret files (*.key, *.pem, *.crt).

## Issue #26
**File:** `docker-compose.yml`
**Line:** N/A (file was missing)
**Problem:** No docker-compose.yml file existed to orchestrate the four services (redis, api, worker, frontend).
**Change:** Created docker-compose.yml with all four services, named internal network (app-network), named volume for Redis data, and proper service dependencies.

## Issue #27
**File:** `docker-compose.yml` - Redis service
**Line:** Ports section
**Problem:** Redis would be exposed to the host machine on port 6379 by default, creating a security risk.
**Change:** Removed the ports mapping for Redis entirely so it is only accessible on the internal Docker network, not exposed to the host.

## Issue #28
**File:** `docker-compose.yml` - Service dependencies
**Line:** depends_on section
**Problem:** Services used `depends_on` without health conditions, so they would start before their dependencies were ready (e.g., API starting before Redis is ready).
**Change:** Added `condition: service_healthy` to all depends_on directives, ensuring services only start after their dependencies pass health checks.

## Issue #29
**File:** `docker-compose.yml` - Resource limits
**Line:** deploy section
**Problem:** No CPU or memory limits were set for any service, which could allow a single service to consume all host resources.
**Change:** Added `deploy.resources.limits` for each service with appropriate CPU and memory limits (redis: 0.5 CPU/512M, api: 1.0 CPU/1G, worker: 1.0 CPU/512M, frontend: 0.5 CPU/256M).

## Issue #30
**File:** `frontend/Dockerfile` - Port configuration
**Line:** EXPOSE
**Problem:** Frontend container runs on port 3000 internally, but host port 3000 was already in use by another process, causing port conflict.
**Change:** Changed docker-compose.yml port mapping from `3000:3000` to `3001:3000` while keeping container internal port as 3000, and updated frontend app.js to use PORT environment variable.

