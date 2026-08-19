from typing import Optional

from jwt import InvalidTokenError
from sqlmodel.ext.asyncio.session import AsyncSession
from data.database.connexion import get_session
from data.models.user import User
from data.crud import crud_user

from utils.security.tokenizer import decode_token

class AuthenticationContext:

    async def get_current_user(self) -> Optional[User]:
        auth_header: str = self.request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.removeprefix("Bearer ").strip()
        try:
            email = decode_token(token).get("email")
            async for session in get_session():
                return await crud_user.get_user_valid_by_email(email, session)
            
            return None
        except InvalidTokenError as err:
            raise InvalidTokenError(err) from err


    async def get_admin(self) -> Optional[User]:
        user = await self.get_current_user()
        if user is not None and user.isAdmin:
            return user
        return None
        
        
