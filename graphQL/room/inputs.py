from typing import Optional

import strawberry

@strawberry.input
class RoomInput:
    name: str
    capacity: int


@strawberry.input
class RoomUpdate:
    id: int
    name: Optional[str]
    capacity: Optional[int]