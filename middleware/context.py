from typing import AsyncIterator

from fastapi import Request
from strawberry.fastapi import BaseContext
from data.database.connexion import get_session
from graphQL.loaders.data_loader import Loader
from middleware.security.authentication import AuthenticationContext


class Context(
    BaseContext,
    AuthenticationContext
):
    def __init__(self, request):
        super().__init__()
        self.request = request


async def get_context(request: Request) -> AsyncIterator[Context]:
    async for session in get_session():
        context = Context(request=request)
        context.session = session
        context.loaders = Loader(session)

        yield context