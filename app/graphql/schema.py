import graphene

from app.graphql.mutation import Mutation
from app.graphql.query import Query


from graphene import ObjectType, String
from graphene.types.schema import Schema


schema = Schema(query=Query, mutation=Mutation)