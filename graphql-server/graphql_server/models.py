from django.db import models

class City(models.Model):
    branch = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    rating = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        db_table = "cities"