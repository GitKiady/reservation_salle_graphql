from typing import List

from sqlmodel import SQLModel, Field

class Room(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    capacity: int = Field(gt=0)
    isValid: bool = Field(default=True)
