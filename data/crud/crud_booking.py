from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession
from data.models.booking import STATUS, Booking
from typing import List
from sqlalchemy import select

async def create_booking(booking: Booking, session: AsyncSession) -> Booking:
    session.add(booking)
    await session.commit()
    await session.refresh(booking)

    return booking


async def get_all_booking(skip: int, limit: int, session: AsyncSession) -> List[Booking]:
    booking = await session.exec(
        select(Booking)
        .offset(skip)
        .limit(limit)
    )

    return booking.scalars().all()


async def get_booking_by_id(booking_id: int, session: AsyncSession) -> Booking | None:
    booking = await session.get(Booking, booking_id)
    return booking


async def get_booking_by_user(booking_id: int, user_id: int, session: AsyncSession) -> Booking | None:
    booking = await session.exec(
        select(Booking)
        .where(Booking.id == booking_id, Booking.user_id == user_id)
    )

    return booking.scalars().one_or_none()


async def get_bookings_by_user(skip: int, limit: int, user_id: int, session: AsyncSession) -> List[Booking]:
    bookings = await session.exec(
        select(Booking)
        .where(Booking.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )

    return bookings.scalars().all()


async def get_booking_by_status(status: STATUS, skip: int, limit: int, session: AsyncSession) -> List[Booking]:
    booking = await session.exec(
        select(Booking)
        .offset(skip)
        .limit(limit)
        .where(Booking.status == status)
    )

    return booking.scalars().all()


async def update_booking(payload: Booking, session: AsyncSession) -> Booking | None:
    booking = await get_booking_by_id(payload.id, session)
    if not booking:
        return None

    update = payload.model_dump(exclude_unset=True)
    for k, v in update.items():
        setattr(booking, k, v)

    session.add(booking)
    await session.commit()
    await session.refresh(booking)

    return booking


async def delete_booking(booking_id: int, session: AsyncSession):
    booking = await session.get(Booking, booking_id)
    if booking.status == STATUS.CANCELLED or booking.end_time < datetime.now():
        await session.delete(booking)
        await session.commit()
        return booking

    return None

