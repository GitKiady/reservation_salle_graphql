import strawberry

@strawberry.input
class RegisterInput:
    pseudo: str
    email: str
    password: str


@strawberry.input
class LoginInput:
    email: str
    password: str