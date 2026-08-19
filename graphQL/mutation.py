import strawberry

from graphQL.booking.mutations import BookingMutation
from graphQL.user.mutations import UserMutation
from graphQL.room.mutations import RoomMutation

@strawberry.type
class Mutation(
    UserMutation,
    RoomMutation,
    BookingMutation
):
    pass