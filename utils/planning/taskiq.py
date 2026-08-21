from datetime import datetime

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker, ListRedisScheduleSource
from taskiq import TaskiqScheduler

from utils.cache.redis_config import Redis
from utils.mailing.mail import send_email

redis = Redis()

result_backend = RedisAsyncResultBackend(
    redis_url=redis.get_url(),
    result_ex_time=1000,
)

broker = RedisStreamBroker(
    url=redis.get_url(),
).with_result_backend(result_backend)

# C'est celui qui enqueue le job
schedule_source = ListRedisScheduleSource(
    url=f"{redis.get_url()}/1")  # Différent database

# Appeler par la commande: taskiq scheduler utils.planning.taskiq:scheduler
scheduler = TaskiqScheduler(broker, sources=[schedule_source])


@broker.task
async def send_email_confirmation(receiver: str, destinataire: str, date_limite: str, salle: str, date_res: str, heure_debut: str, heure_fin: str):
    """
        Envoie email 30 mins avant start date
    """
    send_email(receiver, destinataire, date_limite,
               salle, date_res, heure_debut, heure_fin)


@broker.task
async def cancel_reservation(room_id: int):
    """
        Vérifie si booking n'a pas été confirmé mais toujours en pending
        si non, return none
        Modifie booking en cancel et supprimer la clé dans redis
    """
    ...


@broker.task
async def remove_obs_keys(room_id: int):
    """
        S'execute chaque semains pour nettoyer les clées reservations obselètes
    """
    ...
