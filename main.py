import strawberry
from fastapi import FastAPI
from contextlib import asynccontextmanager

from strawberry.fastapi import GraphQLRouter
from data.database.connexion import init_database
from graphQL.query import Query
from graphQL.mutation import Mutation
from middleware.context import get_context
from utils.planning.taskiq import broker

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    await broker.startup()
    
    yield

    await broker.shutdown()


schema = strawberry.Schema(query=Query, mutation=Mutation)
qraphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI(
    lifespan=lifespan
)

app.include_router(qraphql_app, prefix="/graphql")
