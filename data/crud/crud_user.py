from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession
from data.models.user import User
from sqlalchemy import select


async def register(user: User, session: AsyncSession) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
    user = await session.get(User, user_id)
    return user


async def get_users_by_ids(user_ids: List[int], session: AsyncSession) -> List[User]:
    users = await session.exec(
        select(User)
        .where(User.id.in_(user_ids))
        .where(User.isValid == True)
    )

    return users.scalars().all()


async def get_user_valid_by_id(user_id: int, session: AsyncSession) -> User | None:
    user = await session.exec(
        select(User)
        .where(User.id == id, User.isValid == True)
    )

    return user.scalars().one_or_none()


async def get_user_by_email(email: str, session: AsyncSession) -> User | None:
    user = await session.exec(
        select(User)
        .where(User.email == email)
    )

    return user.scalars().one_or_none()


async def get_user_valid_by_email(email: str, session: AsyncSession) -> User | None:
    user = await session.exec(
        select(User)
        .where(User.email == email, User.isValid == True)
    )

    return user.scalars().one_or_none()


async def update_user(user_id: int, payload: User, session: AsyncSession) -> User | None:
    user = await session.get(User, user_id)
    if not user:
        return None

    user.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def invalid_user(user_id: int, session: AsyncSession) -> bool:
    user = await session.get(User, user_id)
    if not user:
        return False

    user.isValid = False

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return True


async def delete_user(user_id: int, session: AsyncSession) -> bool:
    user = await session.get(User, user_id)
    if user is None:
        return False

    await session.delete(user)
    await session.commit()
    return True
