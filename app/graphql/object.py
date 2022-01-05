import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Users as UsersModel, Teams as TeamsModel, \
    Organizations as OrganizationsModel

class Users(SQLAlchemyObjectType):
   class Meta:
       model = UsersModel
       interfaces = (relay.Node,)

class Organizations(SQLAlchemyObjectType):
   class Meta:
       model = OrganizationsModel
       interfaces = (relay.Node,)


class Teams(SQLAlchemyObjectType):
   class Meta:
       model = TeamsModel
       interfaces = (relay.Node,)

class OrgInput(graphene.InputObjectType):
   name = graphene.String()