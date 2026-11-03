from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point
from .models import District, Place


# 1. District Serializers (Polygons)
class DistrictListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for district lists"""
    places_count = serializers.IntegerField(source='places.count', read_only=True)

    class Meta:
        model = District
        fields = ['id', 'name', 'code', 'description', 'places_count']


class DistrictGeoJSONSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for district polygons (Mapping)"""
    places_count = serializers.IntegerField(source='places.count', read_only=True)

    class Meta:
        model = District
        geo_field = 'geometry'
        fields = ['id', 'name', 'code', 'description', 'places_count']

class PlaceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for place lists"""
    district_name = serializers.ReadOnlyField(source='district.name')
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = [
            'id', 'name', 'category', 'address', 
            'rating', 'district_name', 'latitude', 'longitude'
        ]

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class PlaceDetailSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for place details"""
    district_name = serializers.ReadOnlyField(source='district.name')
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = [
            'id', 'name', 'category', 'address', 'description',
            'rating', 'district', 'district_name',
            'latitude', 'longitude'
        ]

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class PlaceGeoJSONSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for mapping applications"""
    district_name = serializers.SerializerMethodField()

    class Meta:
        model = Place
        geo_field = 'location'
        fields = [
            'id', 'name', 'category', 'address', 
            'description', 'rating', 'district_name'
        ]

    def get_district_name(self, obj):
        if obj.district:
            return obj.district.name
        return "Dublin"


class PlaceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new places via lat/lon coordinates & district selection"""
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    district_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Place
        fields = [
            'name', 'category', 'address', 'description', 
            'rating', 'district', 'latitude', 'longitude', 'district_name'
        ]
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True, 'default': ''},
            'district': {'required': False, 'allow_null': True, 'default': None},
            'address': {'required': False, 'allow_blank': True, 'default': 'Dublin, Ireland'},
            'rating': {'required': False, 'default': 5.0},
        }

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        district_name = validated_data.pop('district_name', None)

        point = Point(longitude, latitude, srid=4326)
        validated_data['location'] = point

        if district_name:
            district_obj = District.objects.filter(name__iexact=district_name).first()
            
            if not district_obj:
                district_obj = District.objects.filter(name__istartswith=district_name).first()
            if not district_obj:
                district_obj = District.objects.filter(code__iexact=district_name).first()

            if district_obj:
                validated_data['district'] = district_obj

        if not validated_data.get('district'):
            district_obj = None
            try:
                district_obj = District.objects.filter(geometry__contains=point).first()
            except Exception:
                pass
            if not district_obj:
                try:
                    district_obj = District.objects.filter(mpoly__contains=point).first()
                except Exception:
                    pass
            validated_data['district'] = district_obj

        return super().create(validated_data)


# 3. Spatial Query Utility Serializers 

class DistanceSerializer(serializers.Serializer):
    """Serializer for distance-based queries (e.g. nearby search)"""
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    radius_km = serializers.FloatField(min_value=0.1, max_value=100)

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value


class BoundingBoxSerializer(serializers.Serializer):
    """Serializer for bounding box queries (Leaflet viewport filtering)"""
    min_longitude = serializers.FloatField()
    min_latitude = serializers.FloatField()
    max_longitude = serializers.FloatField()
    max_latitude = serializers.FloatField()

    def validate(self, data):
        if data['min_longitude'] >= data['max_longitude']:
            raise serializers.ValidationError("min_longitude must be less than max_longitude")

        if data['min_latitude'] >= data['max_latitude']:
            raise serializers.ValidationError("min_latitude must be less than max_latitude")

        for coord in ['min_longitude', 'max_longitude']:
            if not -180 <= data[coord] <= 180:
                raise serializers.ValidationError(f"{coord} must be between -180 and 180")

        for coord in ['min_latitude', 'max_latitude']:
            if not -90 <= data[coord] <= 90:
                raise serializers.ValidationError(f"{coord} must be between -90 and 90")

        return data