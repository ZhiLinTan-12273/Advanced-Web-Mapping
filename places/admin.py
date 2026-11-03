from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin #bring with open street small map
from .models import District, Place 


@admin.register(District)
class DistrictAdmin(GISModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code') #admin able to search area
    
    # make center in Dublin
    gis_widget_kwargs = {
        'attrs': {
            'default_lat': 53.3498,
            'default_lon': -6.2603,
            'default_zoom': 13,
        }
    }

@admin.register(Place)
class PlaceAdmin(GISModelAdmin):
    list_display = ('name', 'category', 'district', 'rating')
    list_filter = ('category', 'district')
    search_fields = ('name', 'address')
    
    gis_widget_kwargs = {
        'attrs': {
            'default_lat': 53.3498,
            'default_lon': -6.2603,
            'default_zoom': 13,
        }
    }