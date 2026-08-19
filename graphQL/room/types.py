import strawberry

@strawberry.type
class Room:
    id: int
    name: str
    capacity: int