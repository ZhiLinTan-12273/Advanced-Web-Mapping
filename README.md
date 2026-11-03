

# Advanced-Web-Mapping Assignment
## Dublin Cultural Heritage & Urban Exploration Map
A Location-Based Services (LBS) web application built with Django (GeoDjango), PostGIS, Leaflet.js, and OpenStreetMap (OSM). The system enables interactive spatial exploration, dynamic radius-based venue discovery, administrative district boundary mapping, and crowdsourced point-of-interest creation across Dublin, Ireland.

## Overview & Features
• Interactive Geospatial Dashboard: Full-screen Leaflet map displaying cultural heritage venues, monuments, and amenities with custom category popups and rating details.
• District Boundary Visualization: Multi-vertex PostGIS polygons representing Dublin administrative districts (e.g., Dublin 1, Dublin 2, D09) rendered with dynamic zoom-to-fit framing.
• 1.5 km Proximity Radius Search: High-performance point-in-radius spatial query calculating spherical distances on the fly to detect all venues within 1.5 km of a selected target coordinate.
• Top 10 Nearest Place Search: Spatial sorting algorithm ranking Dublin cultural sites by true geodesic distance from any user-defined location.
• Interactive Place Creation & Auto-Detection: Click-to-add map functionality allowing users to submit new places, with server-side spatial containment automatically determining the corresponding Dublin administrative district.
• Multi-Filter Search & Live Autocomplete: Instant client-side keyword search paired with category and district filtering to isolate specific heritage types (e.g., museums, parks, pubs, monuments).
• Fully Containerized Database: Isolated Docker environment running PostGIS with persistent volume and spatial GiST indexing.

## Tech Stack & Architecture
• Database Layer: PostgreSQL with PostGIS extension (postgis/postgis Docker image), utilizing spatial GiST indexes and geodesic functions (ST_DWithin, ST_Contains, ST_Distance, ST_SetSRID, ST_MakePoint).
• Spatial Reference System: WGS 84 (SRID 4326) coordinate standard used across all database records and GeoJSON transfers.
• Backend Framework: Python / Django (GeoDjango), Django REST Framework (DRF), and rest_framework_gis.
• Frontend Interface: Modern CSS3 (Collapsible Glassmorphic Floating Panel), Vanilla JavaScript (Async/Await & Fetch API), and Leaflet.js with OpenStreetMap tile services.
• Containerization: Docker for PostGIS spatial database hosting.

## Quick Start & Local Setup
### Prerequisites
• Docker Desktop installed and running.
• Python 3.10+ and Git installed.

### 1. Clone the Repository
git clone https://github.com/your-username/Advanced-Web-Mapping
cd Advanced-Web-Mapping

### 2. Start PostGIS Database Container
Start the PostGIS container via Docker:
docker run --name dublin_postgis -e POSTGRES_DB=european_mapping_db -e POSTGRES_USER=awm_developer -e POSTGRES_PASSWORD=your_password -p 5432:5432 -d postgis/postgis

### 3. Setup Virtual Environment & Run Migrations
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate

### 4. Seed Spatial Database
Import the initial seed script containing Dublin district polygons and curated cultural heritage sites:
python manage.py loaddata seed_data.json
# Or execute the SQL seed scripts directly in pgAdmin / psql

### 5. Run Django Development Server
Launch the server to allow access across the local network:
python manage.py runserver 0.0.0.0:8000

### 6. Access the Application
Open your browser and navigate to:
• Map Dashboard: http://localhost:8000/ (or http://10.156.15.100:8000 on local Wi-Fi)
• District GeoJSON API: http://localhost:8000/api/districts/geojson/
• Places GeoJSON API: http://localhost:8000/api/places/geojson/
• Admin Dashboard: http://localhost:8000/admin/

## REST API Endpoints & Spatial Queries Implemented
• GET /api/districts/geojson/: Returns all Dublin district boundaries formatted as GeoJSON MultiPolygons.
• GET /api/places/geojson/: Returns all heritage venues formatted as GeoJSON Points.
• POST /api/places/radius/ (ST_DWithin & ST_Distance): Accepts target latitude/longitude coordinates and computes all venues located within a 1.5 km radius, annotating exact distance in kilometers.
• POST /api/places/nearest/ (Distance & Ordering): Returns the 10 closest heritage venues to the provided coordinate ordered by physical proximity.
• POST /api/places/create/ (ST_Contains): Ingests user-submitted point coordinates, executes a spatial point-in-polygon check (`geometry__contains=point`) to auto-detect the enclosing district, and persists the record into PostGIS.

## License
This project is developed for educational and assessment purposes under the Web Mapping / Location-Based Services Module.