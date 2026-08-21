from datetime import datetime

from graphql import GraphQLError
import strawberry

from graphQL.user.types import AuthPayload, User
from graphQL.user.inputs import RegisterInput, LoginInput
from data.crud import crud_user
from data.models.user import User as UserModel

from utils.security.hashage import hash_password, check_password
from utils.security.tokenizer import create_access_token

@strawberry.type
class UserMutation:

    @strawberry.mutation
    async def register(self, user: RegisterInput, info: strawberry.Info) -> AuthPayload:
        session = info.context.session
        existing = await crud_user.get_user_by_email(user.email, session)
        if existing:
            raise GraphQLError(
                message="Cet email est déjà associé à un compte.",
                extensions={
                    "code": 400,
                    "timestamp": datetime.now().isoformat()
                }
            )

        hashed = hash_password(user.password)
        db_user = await crud_user.register(
            user=UserModel(pseudo=user.pseudo, email=user.email, hashed_password=hashed),
            session=session
        )

        token = create_access_token(user.email)
        return AuthPayload(
            token=token,
            user=User(
                id=db_user.id,
                pseudo=db_user.pseudo,
                email=db_user.email
            )
        )

    @strawberry.mutation
    async def login(self, user: LoginInput, info: strawberry.Info) -> AuthPayload:
        session = info.context.session
        db_user = await crud_user.get_user_valid_by_email(user.email, session)
        if not db_user or not check_password(user.password, db_user.hashed_password):
            raise GraphQLError(
                message="Identification invalide.",
                extensions={
                    "code": 400,
                    "timestapm": datetime.now()
                }
            )

        token = create_access_token(user.email)
        return AuthPayload(
            token=token,
            user=User(
                id=db_user.id,
                pseudo=db_user.pseudo,
                email=db_user.email
            )
        )



        
