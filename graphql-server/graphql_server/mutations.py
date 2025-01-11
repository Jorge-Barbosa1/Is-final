import graphene
from .models import City
from .types import CityType

class UpdateCity(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        city = graphene.String(required=False)
        latitude = graphene.String(required=False)
        longitude = graphene.String(required=False)
        rating = graphene.Float(required=False)

    city = graphene.Field(CityType)

    def mutate(self, info, id, city=None, latitude=None, longitude=None, rating=None):
        try:
            city_instance = City.objects.get(pk=id)
            if city:
                city_instance.city = city
            if latitude:
                city_instance.latitude = latitude
            if longitude:
                city_instance.longitude = longitude
            if rating is not None:
                city_instance.rating = rating
            city_instance.save()

            return UpdateCity(city=city_instance)
        except City.DoesNotExist:
            raise Exception("City with given ID does not exist")

class Mutation(graphene.ObjectType):
    update_city = UpdateCity.Field()
