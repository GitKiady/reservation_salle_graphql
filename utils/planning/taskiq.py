from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker, ListRedisScheduleSource
from taskiq import TaskiqDepends, TaskiqScheduler

from data.models.booking import STATUS, Booking as BookingModel
from utils.cache.redis_config import Redis
from utils.cache.redis import del_booking
from utils.mailing.mail import send_email, send_email_cancel

from data.database.connexion import get_session

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
    url=redis.get_url())  # Différent database

# Appeler par la commande: taskiq scheduler utils.planning.taskiq:scheduler
scheduler = TaskiqScheduler(broker, sources=[schedule_source])

# Commande pour appeler taskiq:
# taskiq worker utils.planning.taskiq:broker
# taskiq scheduler utils.planning.taskiq:scheduler


@broker.task
async def send_email_confirmation(receiver: str, destinataire: str, date_limite: datetime, salle: str, date_res: datetime, heure_debut: datetime, heure_fin: datetime):
    """
        Envoie email 30 mins avant start date
    """
    result = await send_email(receiver, destinataire, date_limite,
                              salle, date_res, heure_debut, heure_fin)


@broker.task
async def cancel_reservation(
    receiver: str, destinataire: str, date_limite: datetime, salle: str, date_res: datetime, heure_debut: datetime, heure_fin: datetime,
    booking_id: int,
    session: AsyncSession = TaskiqDepends(get_session)
) -> bool:
    """
        Vérifie si booking n'a pas été confirmé mais toujours en pending
        si non, return none
        Modifie booking en cancel et supprimer la clé dans redis
    """

    booking = await session.get(BookingModel, booking_id)
    if not booking:
        return False

    if booking.status is not STATUS.CONFIRMER:
        booking.status = STATUS.CANCELLED
        try:
            session.add(booking)
            await session.commit()

            await del_booking(booking.room_id, booking.start_time, booking.end_time)

            await send_email_cancel(receiver, destinataire, date_limite,
                                    salle, date_res, heure_debut, heure_fin)

            return True
        except Exception:
            await session.rollback()
            raise
    return False
