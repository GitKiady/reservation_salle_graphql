from datetime import datetime

from graphql import GraphQLError
import strawberry

from graphQL.room.inputs import RoomInput, RoomUpdate
from graphQL.room.types import Room

from data.crud import crud_room
from data.models.room import Room as RoomModel


@strawberry.type
class RoomMutation:

    @strawberry.mutation
    async def createRoom(self, room: RoomInput, info: strawberry.Info) -> Room:
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
        db_room = await crud_room.create_room(
            room=RoomModel(
                name=room.name,
                capacity=room.capacity
            ),
            session=session
        )

        return Room(
            id=db_room.id,
            name=db_room.name,
            capacity=db_room.capacity
        )

    @strawberry.mutation
    async def updateRoom(self, room: RoomUpdate, info: strawberry.Info) -> Room:
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
        fields = {k: v for k, v in {
            "id": room.id,
            "name": room.name,
            "capacity": room.capacity
        }.items() if v is not None}

        db_room = await crud_room.update_room(
            payload=RoomModel(**fields),
            session=session
        )

        return Room(
            id=db_room.id,
            name=db_room.name,
            capacity=db_room.capacity
        )

    @strawberry.mutation
    async def deleteRoom(self, room_id: int, info: strawberry.Info) -> bool:
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
        deleted = await crud_room.delete_room(room_id, session)
        if not deleted:
            raise GraphQLError(
                message="Salle non supprimé.",
                extensions={
                    "code": 400,
                    "timestamp": datetime.now().isoformat()
                }
            )

        return deleted
