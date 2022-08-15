import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Users as UsersModel, Teams as TeamsModel, \
    Organizations as OrganizationsModel, Sessions as SessionsModel, \
        Projects as ProjectsModel, Heatmaps as HeatmapsModel, \
            Recordings as RecordingsModel, Views as ViewsModel, Sessionuser as SessionusersModel, \
                Task as TaskModel, Subscriptions as SubscriptionsModel, Coupon as CouponModel, CreditCard as CreditcardModel, \
                    Invoice as InvoiceModel

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

class Sessions(SQLAlchemyObjectType):
   class Meta:
       model = SessionsModel
       interfaces = (relay.Node,)

class Projects(SQLAlchemyObjectType):
   class Meta:
       model = ProjectsModel
       interfaces = (relay.Node,)

class Heatmaps(SQLAlchemyObjectType):
   class Meta:
       model = HeatmapsModel
       interfaces = (relay.Node,)
class Recordings(SQLAlchemyObjectType):
   class Meta:
       model = RecordingsModel
       interfaces = (relay.Node,)
class Views(SQLAlchemyObjectType):
   class Meta:
       model = ViewsModel
       interfaces = (relay.Node,)
class Sessionusers(SQLAlchemyObjectType):
   class Meta:
       model = SessionusersModel
       interfaces = (relay.Node,)
class Coupon(SQLAlchemyObjectType):
   class Meta:
       model = CouponModel
       interfaces = (relay.Node,)
class Invoice(SQLAlchemyObjectType):
   class Meta:
       model = InvoiceModel
       interfaces = (relay.Node,)
class Creditcard(SQLAlchemyObjectType):
   class Meta:
       model = CreditcardModel
       interfaces = (relay.Node,)
class Tasks(SQLAlchemyObjectType):
   class Meta:
       model = TaskModel
       interfaces = (relay.Node,)
class Subscriptions(SQLAlchemyObjectType):
   class Meta:
       model = SubscriptionsModel
       interfaces = (relay.Node,)
class OrgInput(graphene.InputObjectType):
   name = graphene.String()