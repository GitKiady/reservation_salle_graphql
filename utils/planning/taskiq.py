from datetime import datetime

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from utils.cache.redis_config import Redis

redis = Redis()

result_backend = RedisAsyncResultBackend(
    redis_url=redis.get_url(),
    result_ex_time=1000,
)

broker = RedisStreamBroker(
    url=redis.get_url(),
).with_result_backend(result_backend)


@broker.task
async def send_email_confirmation(room_id: int, start: datetime):
    # Envoie email 30 mins avant start date
    ...