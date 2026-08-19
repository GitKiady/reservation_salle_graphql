import strawberry

from datetime import datetime
from typing import List

from graphQL.room.types import Room
from graphql import GraphQLError


from data.crud import crud_room
from middleware.sort.pagination import pagination


@strawberry.type
class RoomQueries:

    @strawberry.field
    async def getRooms(self, page: int, limit: int, info: strawberry.Info) -> List[Room]:
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
        page = pagination(page, limit)
        rooms = await crud_room.get_all_room(session, page.get("skip"), limit)

        return [
            Room(
                id=room.id,
                name=room.name,
                capacity=room.capacity
            ) for room in rooms
        ]

    @strawberry.field
    async def getRoomsValid(self, page: int, limit: int, info: strawberry.Info) -> List[Room]:
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
        current_page = pagination(page, limit)
        rooms = await crud_room.get_all_room_valid(current_page.get("skip"), limit, session)
        return [
            Room(
                id=room.id,
                name=room.name,
                capacity=room.capacity
            ) for room in rooms
        ]

    @strawberry.field
    async def getRoom(self, room_id: int, info: strawberry.Info) -> Room:
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
        room = await crud_room.get_room_by_id(room_id, session)

        return Room(
            id=room.id,
            name=room.name,
            capacity=room.capacity
        )

    @strawberry.field
    async def toggleRoomValidation(self, room_id: int, info: strawberry.Info) -> int:
        user = info.context.get_admin()
        if not user:
            raise GraphQLError(
                message="Utilisateur non autorisé.",
                extensions={
                    "code": 403,
                    "timestamp": datetime.now().isoformat()
                }
            )

        session = info.context.session
        toggle = await crud_room.toggle_room_validation(room_id, session)

        return toggle
