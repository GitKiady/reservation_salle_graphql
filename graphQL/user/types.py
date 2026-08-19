import strawberry

@strawberry.type
class User:
    id: int
    pseudo: str
    email: str


@strawberry.type
class AuthPayload:
    token: str
    user: User