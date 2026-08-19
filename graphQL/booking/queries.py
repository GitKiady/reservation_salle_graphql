from datetime import datetime
from typing import List

from graphql import GraphQLError
import strawberry

from graphQL.booking.types import Booking

from data.crud import crud_booking
from middleware.sort.pagination import pagination


@strawberry.type
class BookingQueries:

    @strawberry.field
    async def bookings(self, page: int, limit: int, info: strawberry.Info) -> List[Booking]:
        user = await info.context.get_admin()
        if not user:
            raise GraphQLError(
                message="Utilisateur non autorisé.",
                extensions={
                    "code": 403,
                    "timestamp": datetime.now().isoformat()
                }
            )

        session = info.context.session
        current_page = pagination(page, limit)
        booking = await crud_booking.get_all_booking(current_page.get("offset"), limit, session)

        return [
            Booking(
                id=book.id,
                user_id=book.user_id,
                room_id=book.room_id,
                start_time=book.start_time,
                end_time=book.end_time,
                status=book.status
            ) for book in booking
        ]

    @strawberry.field
    async def booking(self, booking_id: int, info: strawberry.Info) -> Booking:
        user = await info.context.get_admin()
        if not user:
            raise GraphQLError(
                message="Utilisateur non autorisé.",
                extensions={
                    "code": 403,
                    "timestamp": datetime.now().isoformat()
                }
            )

        session = info.context.session
        booking = await crud_booking.get_booking_by_id(booking_id, session)

        return Booking(
            id=booking.id,
            user_id=booking.user_id,
            room_id=booking.room_id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            status=booking.status
        )

    @strawberry.field
    async def bookingUser(self, booking_id: int, info: strawberry.Info) -> Booking:
        user = await info.context.get_current_user()
        if not user:
            raise GraphQLError(
                message="Utilisateur non authentifié.",
                extensions={
                    "code": 401,
                    "timestamp": datetime.now().isoformat()
                }
            )

        session = info.context.session
        booking = await crud_booking.get_booking_by_user(booking_id, user.id, session)
        if booking is not None:
            return Booking(
                id=booking.id,
                user_id=booking.user_id,
                room_id=booking.room_id,
                start_time=booking.start_time,
                end_time=booking.end_time,
                status=booking.status
            )

        return None

    @strawberry.field
    async def bookingsUser(self, page: int, limit: int, info: strawberry.Info) -> List[Booking]:
        user = await info.context.get_current_user()
        if not user:
            raise GraphQLError(
                message="Utilisateur non authentifié.",
                extensions={
                    "code": 401,
                    "timestamp": datetime.now().isoformat()
                }
            )

        session = info.context.session
        current_page = pagination(page, limit)
        booking = await crud_booking.get_bookings_by_user(current_page.get("offset"), limit, user.id, session)
        return [
            Booking(
                id=book.id,
                user_id=book.user_id,
                room_id=book.room_id,
                start_time=book.start_time,
                end_time=book.end_time,
                status=book.status
            ) for book in booking
        ]
