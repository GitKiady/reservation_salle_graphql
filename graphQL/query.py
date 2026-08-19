import strawberry

from graphQL.booking.queries import BookingQueries
from graphQL.user.queries import UserQueries
from graphQL.room.queries import RoomQueries

@strawberry.type
class Query(
    UserQueries,
    RoomQueries,
    BookingQueries
):
    pass