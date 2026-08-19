from graphql import GraphQLError
import strawberry

from graphQL.user.types import User
from datetime import datetime

@strawberry.type
class UserQueries:
    
    @strawberry.field
    async def me(self, info: strawberry.Info) -> User | None:
        user = await info.context.get_current_user()
        if user is None:
            raise GraphQLError(
                message="Utilisateur introuvable.",
                extensions={
                    "code": 404,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        return User(
            id=user.id,
            pseudo=user.pseudo,
            email=user.email
        )