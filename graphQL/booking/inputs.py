from datetime import datetime
from typing import Optional

import strawberry

from data.models.booking import STATUS


@strawberry.input
class BookingInput:
    user_id: int
    room_id: int
    start_time: datetime
    end_time: datetime


@strawberry.input
class BookingUpdate:
    id: int
    user_id: Optional[int]
    room_id: Optional[int]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    status: Optional[STATUS]
