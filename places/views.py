from django.shortcuts import render
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import District, Place
from .serializers import (
    DistrictGeoJSONSerializer,
    PlaceGeoJSONSerializer,
    PlaceCreateSerializer,
)


def parse_search_parameters(data, include_radius=False):
    try:
        lat = float(data["lat"])
        lng = float(data["lng"])
    except (KeyError, TypeError, ValueError):
        return None, Response(
            {"error": "Provide numeric lat and lng values."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    radius_km = None
    if include_radius:
        try:
            radius_km = float(data.get("radius_km", 5)) 
        except (TypeError, ValueError):
            return None, Response(
                {"error": "radius_km must be a number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        return None, Response(
            {
                "error": "Latitude must be between -90 and 90 and longitude between -180 and 180."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if include_radius and not 0 < radius_km <= 20000:
        return None, Response(
            {"error": "radius_km must be greater than 0 and no more than 20000."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return (lat, lng, radius_km), None


def serialize_place(place, rank=None):
    result = {
        "id": place.id,
        "name": place.name,
        "category": place.category,
        "address": place.address,
        "rating": place.rating,
        "district": place.district.name if place.district else None,
        "coordinates": {
            "lat": place.location.y,
            "lng": place.location.x,
        },
        "distance_km": round(place.distance.km, 2), #change to km with 2 decimal places
    }
    if rank is not None:
        result["rank"] = rank
    return result


# (Find Nearest Places)
#POST /api/places/nearest/ find 10 place nearest
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def find_nearest_places(request):
    """
    POST /api/places/nearest/ with {"lat": 53.3498, "lng": -6.2603}
    """
    parameters, error = parse_search_parameters(request.data)
    if error:
        return error

    lat, lng, _ = parameters
    search_point = Point(lng, lat, srid=4326)

    places = (
        Place.objects.filter(location__isnull=False)
        .annotate(distance=Distance("location", search_point))
        .order_by("distance")[:10]
    )

    results = [serialize_place(place, rank) for rank, place in enumerate(places, 1)]

    return Response({
        "search_point": {"lat": lat, "lng": lng},
        "total_found": len(results),
        "nearest_places": results,
    })

#Find 1.5 km Around Selected (API 2)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def places_within_radius(request):
    """
    POST /api/places/radius/ with {"lat": 53.3498, "lng": -6.2603, "radius_km": 2}
    """
    parameters, error = parse_search_parameters(request.data, include_radius=True)
    if error:
        return error

    lat, lng, radius_km = parameters
    #FOUND THE CENTER
    search_point = Point(lng, lat, srid=4326)

    places = (
        Place.objects.filter(
            location__isnull=False,
            location__distance_lte=(search_point, D(km=radius_km)),
        )
        .annotate(distance=Distance("location", search_point))
        .order_by("distance")
    )

    results = [serialize_place(place) for place in places]

    return Response({
        "search_point": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "total_found": len(results),
        "places": results,
    })

#API 3：GET THE DISTRICT (GeoJSON）
@api_view(["GET", "HEAD"])
def get_districts_geojson(request):
    districts = District.objects.all()
    serializer = DistrictGeoJSONSerializer(districts, many=True)
    return Response(serializer.data)

# got all of the place marker
@api_view(["GET", "HEAD"])
def get_places_geojson(request):
    """GET /api/places/geojson/ support data to frontend"""
    places = Place.objects.filter(location__isnull=False)
    serializer = PlaceGeoJSONSerializer(places, many=True)
    return Response(serializer.data)


#for create a new place API, insert lat and lng
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def create_place(request):
    serializer = PlaceCreateSerializer(data=request.data)
    if serializer.is_valid():
        place = serializer.save()
        return Response(
            {"message": "Place created successfully", "id": place.id},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# for frontend connect to index.html
def map_view(request):
    return render(request, "index.html")