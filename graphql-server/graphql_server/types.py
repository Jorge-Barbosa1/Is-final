import graphene
from .models import City

class CityType(graphene.ObjectType):
    id = graphene.ID()
    city = graphene.String()
    latitude = graphene.String()
    longitude = graphene.String()
    rating = graphene.Float()
