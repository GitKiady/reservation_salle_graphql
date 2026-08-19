import redis
import os
from dotenv import load_dotenv
load_dotenv()

class Redis(redis.asyncio.Redis):
    def __init__(self):
        super.__init__(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            decode_responses=True
        )

    def get_host(self):
        return os.getenv("REDIS_HOST")

    def get_port(self):
        return int(os.getenv("REDIS_PORT"))

    def get_url(self):
        return f"redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}"