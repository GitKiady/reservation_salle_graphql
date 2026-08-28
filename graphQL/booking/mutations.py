from datetime import datetime, timedelta, timezone

from graphql import GraphQLError
import strawberry

from graphQL.booking.inputs import BookingInput, BookingUpdate
from graphQL.booking.types import Booking

from sqlmodel.ext.asyncio.session import AsyncSession

from data.models.user import User as UserModel
from data.models.room import Room as RoomModel
from data.models.booking import Booking as BookingModel
from data.crud import crud_booking, crud_user, crud_room

from taskiq_redis.schedule_source import RedisScheduleSource

from utils.cache.redis import try_to_book
from utils.planning.taskiq import send_email_confirmation, cancel_reservation, schedule_source
import uuid
from taskiq import ScheduledTask

import os
from dotenv import load_dotenv
load_dotenv()


@strawberry.type
class BookingMutation:

    @staticmethod
    async def plan_booking(
        booking: BookingModel,
        user: UserModel,
        room: RoomModel
    ):
        # 1. Calcul des heures d'exécution au format UTC conscient (Aware UTC)
        now_utc = datetime.now(timezone.utc)
        
        run_confirmation = (
            booking.start_time - timedelta(minutes=int(os.getenv("MINUTE_CONFIRMATION", 30)))
        ).astimezone(timezone.utc)
        
        limite_confirmation = (
            booking.start_time - timedelta(minutes=int(os.getenv("MINUTE_CANCEL", 15)))
        ).astimezone(timezone.utc) # On utilise utc car le planificateur redis utilise utc. Dans le cas contraire, il y aurait un décalage
        
        run_cancel = limite_confirmation + timedelta(minutes=1)

        # 2. Planification de l'email
        await send_email_confirmation.schedule_by_time(
            schedule_source,
            time=run_confirmation,
            receiver=user.email,
            destinataire=user.pseudo,
            date_limite=booking.start_time - timedelta(minutes=int(os.getenv("MINUTE_CANCEL", 15))),
            salle=room.name,
            date_res=booking.start_time.date(),
            heure_debut=booking.start_time.time(),
            heure_fin=booking.end_time.time(),
        )

        # 3. Planification de l'annulation automatique
        await cancel_reservation.schedule_by_time(
            schedule_source,
            time=run_cancel,
            booking_id=booking.id,
        )


    @strawberry.mutation
    async def createBooking(self, booking: BookingInput, info: strawberry.Info) -> Booking:
        user = await info.context.get_current_user()
        if not user:
            raise GraphQLError(
                message="Utilisateur non authentifié.",
                extensions={
                    "code": 401,
                    "timestamp": datetime.now().isoformat()
                }
            )

        if booking.start_time < datetime.now() or booking.end_time < datetime.now() or booking.start_time > booking.end_time:
            raise GraphQLError(
                message="Date de réservation invalide.",
                extensions={
                    "code": 400,
                    "timestamp": datetime.now().isoformat()
                }
            )  

        # Je vérifie si la place n'est pas prise
        booked = await try_to_book(booking.room_id, booking.start_time, booking.end_time)
        if booked != "OK":
            raise GraphQLError(
                message=booked,
                extensions={
                    "code": 400,
                    "timestamp": datetime.now().isoformat()
                }
            )

        session = info.context.session
        db_booking = await crud_booking.create_booking(
            booking=BookingModel(
                user_id=booking.user_id,
                room_id=booking.room_id,
                start_time=booking.start_time,
                end_time=booking.end_time
            ),
            session=session
        )

        db_user = await crud_user.get_user_by_id(booking.user_id, session)
        db_room = await crud_room.get_room_by_id(booking.room_id, session)

        await BookingMutation.plan_booking(db_booking, db_user, db_room)

        return Booking(
            id=db_booking.id,
            user_id=db_booking.user_id,
            room_id=db_booking.room_id,
            start_time=db_booking.start_time,
            end_time=db_booking.end_time,
            status=db_booking.status
        )

    @strawberry.mutation
    async def updateBooking(self, payload: BookingUpdate, info: strawberry.Info) -> Booking:
        user = info.context.get_current_user()
        if not user:
            raise GraphQLError(
                message="Utilisateur non authentifié.",
                extensions={
                    "code": 401,
                    "timestamp": datetime.now().isoformat()
                }
            )

        session = info.context.session
        fields = {k: v for k, v in {
            "id": payload.id,
            "user_id": payload.user_id,
            "room_id": payload.room_id,
            "start_time": payload.start_time,
            "end_time": payload.end_time,
            "status": payload.status
        }.items() if v is not None}
        booking = await crud_booking.update_booking(
            payload=BookingModel(**fields),
            session=session
        )

        return Booking(
            id=booking.id,
            user_id=booking.user_id,
            room_id=booking.room_id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            status=booking.status
        )

    @strawberry.mutation
    async def deleteBooking(self, booking_id: int, info: strawberry.Info) -> bool:
        user = info.context.get_current_user()
        if not user:
            raise GraphQLError(
                message="Utilisateur non authentifié.",
                extensions={
                    "code": 401,
                    "timestamp": datetime.now().isoformat()
                }
            )

        session = info.context.session
        deleted = await crud_booking.delete_booking(booking_id, session)
        if deleted:
            return True

        return False
