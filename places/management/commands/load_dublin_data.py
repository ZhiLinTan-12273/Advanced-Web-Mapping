from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from places.models import District, Place

class Command(BaseCommand):
    help = 'load sample dublin place into PostGIS'

    def handle(self, *args, **kwargs):
        self.stdout.write('1. Clearing existing records...')
        Place.objects.all().delete()
        District.objects.all().delete()

        self.stdout.write('2. Creating districts...')
        
        d1_coords = [
            (-6.2750, 53.3550),
            (-6.2400, 53.3550),
            (-6.2400, 53.3480), 
            (-6.2750, 53.3480), 
            (-6.2750, 53.3550)   
        ]
        poly1 = Polygon(d1_coords)
        d1 = District()
        d1.name = "Dublin 1"
        d1.code = "D01"
        d1.description = "North city centre area including O'Connell Street"
        d1.geometry = MultiPolygon(poly1)
        d1.save()

        d2_coords = [
            (-6.2700, 53.3460),
            (-6.2450, 53.3460),
            (-6.2450, 53.3330),
            (-6.2700, 53.3330),
            (-6.2700, 53.3460)
        ]
        poly2 = Polygon(d2_coords)
        d2 = District()
        d2.name = "Dublin 2"
        d2.code = "D02"
        d2.description = "South city centre area including Trinity College"
        d2.geometry = MultiPolygon(poly2)
        d2.save()

        d7_coords = [
            (-6.2950, 53.3650),
            (-6.2700, 53.3650),
            (-6.2700, 53.3480),
            (-6.2950, 53.3480),
            (-6.2950, 53.3650)
        ]
        poly7 = Polygon(d7_coords)
        d7 = District()
        d7.name = "Dublin 7"
        d7.code = "D07"
        d7.description = "TU Dublin Grangegorman and Smithfield area"
        d7.geometry = MultiPolygon(poly7)
        d7.save()

        self.stdout.write('3. Creating places...')
        p1 = Place()
        p1.name = "The Spire"
        p1.category = "attraction"
        p1.address = "O'Connell Street, Dublin 1"
        p1.description = "Famous stainless steel monument in Dublin"
        p1.rating = 4.3
        p1.district = d1
        p1.location = Point(-6.2603, 53.3499, srid=4326)
        p1.save()

        p2 = Place()
        p2.name = "TU Dublin Grangegorman Campus"
        p2.category = "library"
        p2.address = "Grangegorman Lower, Dublin 7"
        p2.description = "TU Dublin central campus"
        p2.rating = 4.8
        p2.district = d7
        p2.location = Point(-6.2789, 53.3551, srid=4326)
        p2.save()

        p3 = Place()
        p3.name = "Trinity College Library"
        p3.category = "attraction"
        p3.address = "College Green, Dublin 2"
        p3.description = "the Book of Kells"
        p3.rating = 4.8
        p3.district = d2
        p3.location = Point(-6.2573, 53.3438, srid=4326)
        p3.save()

        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))