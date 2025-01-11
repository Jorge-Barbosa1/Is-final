import graphene
from graphene_django.types import DjangoObjectType
from graphql_server.models import City
from .mutations import UpdateCity

class CityType(DjangoObjectType):
    class Meta:
        model = City
        fields = ("id", "city", "latitude", "longitude")
    
class Query(graphene.ObjectType):
    cities = graphene.List(CityType) 
    city_by_name = graphene.List(CityType, name=graphene.String(required=True))

    def resolve_cities(self, info):
        return City.objects.all()

    def resolve_city_by_name(self, info, name):
        return City.objects.filter(city__icontains=name)

class Mutation(graphene.ObjectType):
    update_city = UpdateCity.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)