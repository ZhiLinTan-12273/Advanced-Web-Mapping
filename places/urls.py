from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map-view'),

    # output from geojson, draw the map on frontend
    path('districts/geojson/', views.get_districts_geojson, name='districts-geojson'),
    path('places/geojson/', views.get_places_geojson, name='places-geojson'),

    path('places/nearest/', views.find_nearest_places, name='places-nearest'),
    path('places/radius/', views.places_within_radius, name='places-radius'),

    # for create new place then send to postgis
    path('places/create/', views.create_place, name='places-create'),
]