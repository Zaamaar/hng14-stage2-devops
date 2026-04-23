import redis
import time
import os
import signal
import sys
from dotenv import load_dotenv

load_dotenv()

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    
    def exit_gracefully(self, *args):
        self.kill_now = True

def get_redis_connection():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD", None),
        decode_responses=True,
        socket_connect_timeout=5,
    )

def process_job(job_id):
    print(f"Processing job {job_id}")
    r = get_redis_connection()
    r.hset(f"job:{job_id}", "status", "processing")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")

# Connect to Redis with retry
r = get_redis_connection()
max_retries = 5
for attempt in range(max_retries):
    try:
        r.ping()
        print("Connected to Redis")
        break
    except redis.ConnectionError:
        print(f"Redis not ready, retrying ({attempt+1}/{max_retries})...")
        time.sleep(2)
else:
    print("Failed to connect to Redis")
    sys.exit(1)

killer = GracefulKiller()

print("Worker started, waiting for jobs...")
while not killer.kill_now:
    try:
        job = r.brpop("job", timeout=1)
        if job:
            _, job_id = job
            process_job(job_id)
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        time.sleep(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(1)

print("Worker shutting down gracefully")
