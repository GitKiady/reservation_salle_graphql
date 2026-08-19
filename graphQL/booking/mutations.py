from datetime import datetime

from graphql import GraphQLError
import strawberry

from graphQL.booking.inputs import BookingInput, BookingUpdate
from graphQL.booking.types import Booking

from data.models.booking import Booking as BookingModel
from data.crud import crud_booking

from utils.cache.redis import try_to_book
from utils.planning.taskiq import send_email_confirmation


@strawberry.type
class BookingMutation:

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

        # C'est ici qu'on ajoute la gestion de disponibilité de la salle
        # ...
        #

        # Je vérifie si la place n'est pas prise
        booked = try_to_book(booking.room_id, booking.start_time, booking.end_time)
        if not booked:
            raise GraphQLError(
                message="La plage horaire n'est pas encore disponible.",
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

        # J'ajoute le planning


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
