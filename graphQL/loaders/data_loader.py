from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from strawberry.dataloader import DataLoader

from data.crud import crud_user, crud_room


class Loader:
    def __init__(self, session: AsyncSession):
        self.session = session

    def create_user_loader(self):
        async def batch_load_users(user_ids: List[int]) -> List[Optional["User"]]:
            users = await crud_user.get_users_by_ids(user_ids, self.session)
            srt_user = {s.id: s for s in users}

            return [srt_user.get(s) for s in user_ids]

        return DataLoader(load_fn=batch_load_users)


    def create_room_loader(self):
        async def batch_load_rooms(room_ids: List[int]) -> List[Optional["Room"]]:
            rooms = await crud_room.get_room_by_ids(room_ids, self.session)
            srt_room = {r.id: r for r in rooms}

            return [srt_room.get(r) for r in room_ids]

        return DataLoader(load_fn=batch_load_rooms)
