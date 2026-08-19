from typing import List

from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    pseudo: str
    email: str = Field(unique=True)
    hashed_password: str
    isValid: bool = Field(default=True)
    isAdmin: bool = Field(default=False)