from datetime import datetime, timedelta

from graphql import GraphQLError
import strawberry

from graphQL.booking.inputs import BookingInput, BookingUpdate
from graphQL.booking.types import Booking


from data.models.user import User as UserModel
from data.models.room import Room as RoomModel
from data.models.booking import Booking as BookingModel
from data.crud import crud_booking, crud_user, crud_room

from taskiq_redis.schedule_source import RedisScheduleSource

from utils.cache.redis import try_to_book
from utils.planning.taskiq import send_email_confirmation, cancel_reservation, schedule_source
import uuid
from taskiq import ScheduledTask


@strawberry.type
class BookingMutation:

    @staticmethod
    async def plan_booking(booking: BookingModel, user: UserModel, room: RoomModel):
        # J'ajoute le planning
        run_confirmation = booking.start_time - timedelta(minutes=30)
        limite_confirmation = str(booking.start_time - timedelta(minutes=15))
        await schedule_source.add_schedule(
            ScheduledTask(
                schedule_id=str(uuid.uuid4()),
                task_name=send_email_confirmation.task_name,
                labels={},
                args=[user.email, user.pseudo, limite_confirmation, room.name, str(
                    booking.start_time.date()), str(booking.start_time.time()), str(booking.end_time.time())],
                kwargs=[],
                time=run_confirmation
            )
        )

        # J'ajoute la vérification si le booking n'a pas été accepté
        run_cancel = booking.start_time - timedelta(minutes=10)
        await schedule_source.add_schedule(
            ScheduledTask(
                schedule_id=str(uuid.uuid4()),
                task_name=cancel_reservation.task_name,
                labels={},
                args=[booking.room_id, booking.start_time],
                kwargs=[],
                time=run_cancel
            )
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

        # Je vérifie si la place n'est pas prise
        booked = await try_to_book(booking.room_id, booking.start_time, booking.end_time)
        if booked is not "OK":
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

        db_user = await crud_user.get_user_by_id(booking.user_id)
        db_room = await crud_room.get_room_by_id(booking.room_id)

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
