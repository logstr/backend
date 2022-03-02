import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField
from app.api.routes.sessionuser import Sessionuser
from app.graphql.object import Projects, Users, Organizations, Teams, Sessions, Heatmaps, \
    Sessionusers, Views, Recordings
from app.models import Users as UsersModel, Sessionuser as SessionusersModel



class Query(graphene.ObjectType):
    node = relay.Node.Field()

    users = graphene.List(lambda: Users, first_name=graphene.String())

    organizations = SQLAlchemyConnectionField(Organizations)
    teams = SQLAlchemyConnectionField(Teams)
    sessions = SQLAlchemyConnectionField(Sessions)
    projects = SQLAlchemyConnectionField(Projects)
    heatmaps = SQLAlchemyConnectionField(Heatmaps)
    sessionuser = SQLAlchemyConnectionField(Sessionusers)
    views = SQLAlchemyConnectionField(Views)
    recordings = SQLAlchemyConnectionField(Recordings)

    def resolve_users(self, info, first_name=None):
        query = Users.get_query(info)
        if first_name:
            query = query.filter(UsersModel.first_name == first_name)
        return query.all()
