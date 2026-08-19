from datetime import datetime

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker, ListRedisScheduleSource
from taskiq import TaskiqScheduler

from utils.cache.redis_config import Redis

redis = Redis()

result_backend = RedisAsyncResultBackend(
    redis_url=redis.get_url(),
    result_ex_time=1000,
)

broker = RedisStreamBroker(
    url=redis.get_url(),
).with_result_backend(result_backend)

# C'est celui qui enqueue le job
schedule_source = ListRedisScheduleSource(url=f"{redis.get_url()}/1") # Différent database

# Appeler par la commande: taskiq scheduler utils.planning.taskiq:scheduler
scheduler = TaskiqScheduler(broker, sources=[schedule_source]) 


@broker.task
async def send_email_confirmation(room_id: int, start: datetime):
    # Envoie email 30 mins avant start date
    ...

@broker.task
async def cancel_reservation(room_id: int):
    # vérifie si booking n'a pas été confirmé mais toujours en pending
    # si non, return none
    # Modifie booking en cancel et supprimer la clé dans redis
    ...