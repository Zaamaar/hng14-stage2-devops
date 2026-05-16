import redis
import time
import os
import signal
import sys

# Try to load dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed, using environment variables")


class GracefulKiller:
    """Handle graceful shutdown signals"""
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        """Handle shutdown signal"""
        print("Received shutdown signal")
        self.kill_now = True


def get_redis_connection():
    """Create Redis connection"""
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_password = os.getenv("REDIS_PASSWORD", None)

    print(f"Connecting to Redis at {redis_host}:{redis_port}")

    return redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True,
        socket_connect_timeout=5,
    )


def process_job(job_id):
    """Process a single job"""
    print(f"Processing job {job_id}")
    try:
        r = get_redis_connection()
        r.hset(f"job:{job_id}", "status", "processing")
        time.sleep(2)  # simulate work
        r.hset(f"job:{job_id}", "status", "completed")
        print(f"Done: {job_id}")
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")


# Connect to Redis with retry
r = get_redis_connection()
max_retries = 10
for attempt in range(max_retries):
    try:
        r.ping()
        print("Connected to Redis successfully")
        break
    except redis.ConnectionError as e:
        print(f"Redis not ready, retrying ({attempt + 1}/{max_retries})... Error: {e}")
        time.sleep(3)
else:
    print("Failed to connect to Redis after max retries")
    sys.exit(1)

killer = GracefulKiller()

print("Worker started, waiting for jobs...")
while not killer.kill_now:
    try:
        result = r.brpop("job", timeout=1)
        if result:
            _, job_id = result
            process_job(job_id)
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        time.sleep(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(1)

print("Worker shutting down gracefully")
sys.exit(0)
