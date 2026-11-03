from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex


class District(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    geometry = models.MultiPolygonField(srid=4326)

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        ordering = ['code']
        indexes = [
            GistIndex(fields=['geometry'], name='district_geom_gist_idx'),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Place(models.Model):
    CATEGORY_CHOICES = [
        ('restaurant', 'Restaurant / Pub'),
        ('shopping', 'Shopping / Market'),
        ('park', 'Park / Outdoors'),
        ('museum', 'Museum'),
        ('attraction', 'Attraction / Culture'),
        ('monument', 'Monument / Landmark'),
        ('transport', 'Transport'),
        ('education', 'Education / Campus'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='attraction')
    address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)
    district = models.ForeignKey(
        District, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='places'
    )
    location = models.PointField(srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Place"
        verbose_name_plural = "Places"
        ordering = ['name']
        indexes = [
            GistIndex(fields=['location'], name='place_location_gist_idx'),
        ]

    def __str__(self):
        return self.name