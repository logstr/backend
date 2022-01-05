import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField
from app.graphql.object import Users, Organizations, Teams
from app.models import Users as UsersModel

class Query(graphene.ObjectType):
   node = relay.Node.Field()

   users = graphene.List(lambda: Users, first_name=graphene.String())

   def resolve_users(self, info, first_name=None):
       query = Users.get_query(info)
       if first_name:
           query = query.filter(UsersModel.first_name == first_name)
       return query.all()

   organizations = SQLAlchemyConnectionField(Organizations)
   teams = SQLAlchemyConnectionField(Teams)