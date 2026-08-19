from typing import Annotated

import strawberry

from datetime import datetime

from data.models.booking import STATUS


@strawberry.type
class Booking:
    id: int
    user_id: strawberry.Private[int]
    room_id: strawberry.Private[int]
    start_time: datetime
    end_time: datetime
    status: STATUS

    @strawberry.field
    async def user(self, info: strawberry.Info) -> Annotated["User", strawberry.lazy("graphQL.user.types")]:
        users = await info.context.loaders.create_user_loader().load(self.user_id)
        from graphQL.user.types import User
        return User(
            id=users.id,
            pseudo=users.pseudo,
            email=users.email
        )

    @strawberry.field
    async def room(self, info: strawberry.Info) -> Annotated["Room", strawberry.lazy("graphQL.room.types")]:
        rooms = await info.context.loaders.create_room_loader().load(self.room_id)

        from graphQL.room.types import Room
        return Room(
            id=rooms.id,
            name=rooms.name,
            capacity=rooms.capacity
        )
