from datetime import datetime

from sqlmodel import SQLModel, Field

from enum import StrEnum

class STATUS(StrEnum):
    PENDING = "PENDING"
    CONFIRMER = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Booking(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    room_id: int = Field(foreign_key="room.id")
    start_time: datetime
    end_time: datetime
    status: str = Field(default=STATUS.PENDING)
