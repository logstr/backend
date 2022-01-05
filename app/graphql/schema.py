from app.graphql.mutation import Mutation
from app.graphql.query import Query
from graphene.types.schema import Schema


schema = Schema(query=Query, mutation=Mutation)