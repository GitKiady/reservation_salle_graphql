from typing import List

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from data.models.room import Room


async def create_room(room: Room, session: AsyncSession) -> Room | None:
    session.add(room)
    await session.commit()
    await session.refresh(room)

    return room


async def get_room_by_id(room_id: int, session: AsyncSession) -> Room | None:
    room = await session.get(Room, room_id)
    return room


async def get_room_by_ids(room_ids: List[int], session: AsyncSession) -> List[Room]:
    room = await session.exec(
        select(Room)
        .where(Room.id.in_(room_ids))
        .where(Room.isValid == True)
    )

    return room.scalars().all()


async def get_all_room(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Room]:
    room = await session.exec(
        select(Room)
        .offset(skip)
        .limit(limit)
    )

    return room.scalars().all()


async def get_all_room_valid(skip: int, limit: int, session: AsyncSession) -> List[Room]:
    room = await session.exec(
        select(Room)
        .offset(skip)
        .limit(limit)
        .where(Room.isValid == True)
    )

    return room.scalars().all()


async def update_room(payload: Room, session: AsyncSession) -> Room | None:
    room = await get_room_by_id(payload.id, session)
    if not room:
        return None

    update = payload.model_dump(exclude_unset=True)
    for k, v in update.items():
        setattr(room, k, v)

    session.add(room)
    await session.commit()
    await session.refresh(room)

    return room


async def toggle_room_validation(room_id: int, session: AsyncSession) -> int:
    room = await get_room_by_id(room_id, session)
    if not room:
        return None

    if room.isValid:
        room.isValid = 0

    else:
        room.isValid = 1

    session.add(room)
    await session.commit()
    await session.refresh(room)

    return room.isValid


async def delete_room(room_id: int, session: AsyncSession) -> bool:
    room = await session.get(Room, room_id)
    if room is None or not room.isValid:
        return False

    await session.delete(room)
    await session.commit()
    return True
