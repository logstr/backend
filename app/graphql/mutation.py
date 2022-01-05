import graphene

from app import db
from app.graphql.object import OrgInput, Users, Organizations
from app.models import Users as UsersModel, Organizations as OrganizationsModel, \
    Teams as TeamsModel

class UsersMutation(graphene.Mutation):
   class Arguments:
       first_name = graphene.String(required=True)
       last_name = graphene.String(required=True)

   user = graphene.Field(lambda: Users)

   def mutate(self, first_name, last_name):
       user = UsersModel(first_name=first_name, last_name=last_name)

       db.session.add(user)
       db.session.commit()

       return UsersMutation(user=user)

class OrganizationMutation(graphene.Mutation):
   class Arguments:
       role = graphene.String(required=True)
       description = graphene.String(required=True)
       user_id = graphene.Int(required=True)
       skills = graphene.List(OrgInput)
       id = graphene.Int()

   organization = graphene.Field(lambda: Organizations)

   def mutate(self, role, description, user_id):
       user = UsersModel.query.get(user_id)

       organization = OrganizationsModel(role=role, description=description)

       return OrganizationMutation(profile=organization)


class Mutation(graphene.ObjectType):
   mutate_user = UsersMutation.Field()
   mutate_organization= OrganizationMutation.Field()