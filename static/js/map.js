const map = L.map('map').setView([53.3498, -6.2603], 13);

// insert open street map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    minZoom: 2,
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// 
let districtLayer = L.geoJSON(null, {
    style: { color: "#e67e22", weight: 3, opacity: 0.9, fillColor: "#f39c12", fillOpacity: 0.15 }
}).addTo(map);

let placeLayer = L.layerGroup().addTo(map); // for place
let radiusCircle = null; //for record 1.5 km 

let rawDistrictsData = []; //store district for temporary
let rawPlacesData = [];//place
let markersMap = {}; // store market, took by lab 4

// default place on map
let currentCenter = { name: "The Spire", lat: 53.3498, lng: -6.2603 };

// setting center
function setCenter(name, lat, lng) {
    currentCenter = { name: name, lat: lat, lng: lng };
    document.getElementById('selectedInfo').innerHTML = `<b>Target:</b> ${name}<br><b>Lat/Lng:</b> ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
}

function addPlaceMarker(id, lat, lng, name, category, rating, address, districtName, distanceKm = null) {
    let popupContent = `
        <div style="min-width: 170px;">
            <h4 style="margin: 0 0 4px 0; color: #2c3e50;">${name}</h4>
            <p style="margin: 2px 0; font-size: 12px;"><b>District:</b> ${districtName || 'Dublin'}</p>
            <p style="margin: 2px 0; font-size: 12px;"><b>Category:</b> ${category}</p>
            <p style="margin: 2px 0; font-size: 12px;"><b>Rating:</b> ⭐ ${rating}</p>
            <p style="margin: 2px 0; font-size: 12px;"><b>Address:</b> ${address || '-'}</p>
    `;
    if (distanceKm !== null) {
        popupContent += `<p style="margin: 2px 0; font-size: 12px; color: #e74c3c;"><b>Distance:</b> ${distanceKm} km</p>`;
    }
    popupContent += `
            <button style="margin-top: 6px; width: 100%; padding: 4px; font-size: 11px; background-color: #3498db;" onclick="setCenter('${name.replace(/'/g, "\\'")}', ${lat}, ${lng})">
                Select as Search Center
            </button>
        </div>
    `;
    const marker = L.marker([lat, lng]).bindPopup(popupContent);
    placeLayer.addLayer(marker);
    if (id) markersMap[id] = marker;
} //in the end show the detail of place. like category, rating n so on

//  from Lab 4 goToCity 
function goToPlace(lat, lng, id) {
    map.setView([lat, lng], 16);
    if (markersMap[id]) {
        markersMap[id].openPopup();
    }
}

function matchCategory(catStr, filter) {
    if (filter === 'all') return true;
    return catStr === filter;
}

function applyFilters() {
    // step1 ,clear all of the places, district and radius(circle)
    placeLayer.clearLayers();
    districtLayer.clearLayers();
    markersMap = {};
    if (radiusCircle) { map.removeLayer(radiusCircle); radiusCircle = null; }

    const query = document.getElementById('searchInput').value.trim().toLowerCase();
    const selectedDistrict = document.getElementById('districtFilter').value;
    const selectedCategory = document.getElementById('categoryFilter').value;
    const resultsDiv = document.getElementById('searchResults');

    if (selectedDistrict !== 'none') {
        const selectDistrict = rawDistrictsData.find(d => d.properties.name === selectedDistrict);
        if (selectDistrict) {
            districtLayer.addData(selectDistrict);
            if (districtLayer.getBounds().isValid()) {
                //pan and zoom the map viewport to fit the selected zone.
                map.fitBounds(districtLayer.getBounds(), { padding: [25, 25] }); 
            }
        }
    }

    const filteredPlaces = rawPlacesData.filter(f => {
        const p = f.properties;
        const placeDistrict = p.district || p.district_name;

        const matchKeyword = !query || 
            (p.name && p.name.toLowerCase().includes(query)) ||
            (p.address && p.address.toLowerCase().includes(query));
            
        const matchCat = matchCategory(p.category, selectedCategory);
        
        const matchDist = (selectedDistrict === 'none') || (placeDistrict === selectedDistrict);

        return matchKeyword && matchCat && matchDist;
    });

    filteredPlaces.forEach(f => {
        const c = f.geometry.coordinates;
        const p = f.properties;
        addPlaceMarker(f.id || p.id, c[1], c[0], p.name, p.category, p.rating, p.address, p.district || p.district_name);
    });

    if (query.length > 0) {
        if (filteredPlaces.length === 0) {
            resultsDiv.innerHTML = '<div style="padding: 6px; color: #999; font-size: 12px;">No matching places found</div>';
        } else {
            resultsDiv.innerHTML = filteredPlaces.slice(0, 5).map(f => {
                const c = f.geometry.coordinates;
                const p = f.properties;
                return `
                    <div class="search-item" onclick="goToPlace(${c[1]}, ${c[0]}, '${f.id || p.id}')">
                        <b>${p.name}</b> <span style="color:#888;">(${p.category})</span>
                    </div>
                `;
            }).join('');
        }
    } else {
        resultsDiv.innerHTML = '';
    }

    document.getElementById('status').innerText = `Showing ${filteredPlaces.length} places on map.`;
}

// reset map
function resetAll() {
    document.getElementById('searchInput').value = '';
    document.getElementById('districtFilter').value = 'none';
    document.getElementById('categoryFilter').value = 'all';
    document.getElementById('searchResults').innerHTML = '';
    map.setView([53.3498, -6.2603], 13); 
    applyFilters();
}

function searchAroundSelected() {
    placeLayer.clearLayers();
    districtLayer.clearLayers();
    markersMap = {};
    if (radiusCircle) map.removeLayer(radiusCircle);

    radiusCircle = L.circle([currentCenter.lat, currentCenter.lng], {
        radius: 1500,
        color: '#e74c3c',
        fillColor: '#e74c3c',
        fillOpacity: 0.1
    }).addTo(map);

    map.setView([currentCenter.lat, currentCenter.lng], 14);
    document.getElementById('status').innerText = `Searching 1.5 km around ${currentCenter.name}...`;

    fetch('/api/places/radius/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            lat : currentCenter.lat,
            lng : currentCenter.lng,
            radius_km : 1.5
        })
    })
    .then(res => res.json())
    .then(data => {
        data.places.forEach(item => {
            addPlaceMarker(
                item.id, item.coordinates.lat, item.coordinates.lng,
                item.name, item.category, item.rating, item.address, item.district, item.distance_km
            );
        });
        document.getElementById('status').innerText = `Found ${data.total_found} places within 1.5 km of ${currentCenter.name}.`;
    });
}

map.on('click', function(e) { //to create a new place on map(user input data)
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;

    let districtOptionsHtml = `<option value="">Auto-Detect / General Dublin</option>`;
    rawDistrictsData.forEach(d => {
        districtOptionsHtml += `<option value="${d.properties.name}">${d.properties.name} (${d.properties.code})</option>`;
    });

    const formHtml = `
        <div class="form-popup">
            <h4 style="margin: 0 0 6px 0; color: #2c3e50;">Add New Place</h4>
            <label>Place Name:</label>
            <input type="text" id="newPlaceName" placeholder="e.g. Dublin Castle" />
            
            <label>District:</label>
            <select id="newPlaceDistrict">
                ${districtOptionsHtml}
            </select>

            <label>Category:</label>
            <select id="newPlaceCategory">
                <option value="restaurant">Restaurant / Pub</option>
                <option value="shopping">Shopping / Market</option>
                <option value="park">Park / Outdoors</option>
                <option value="museum">Museum</option>
                <option value="attraction">Attraction / Culture</option>
                <option value="monument">Monument / Landmark</option>
                <option value="transport">Transport</option>
                <option value="education">Education / Campus</option>
            </select>

            <button onclick="submitNewPlace(${lat}, ${lng})">Save to PostGIS</button>
            <button style="margin-top: 4px; background: #95a5a6;" onclick="setCenter('Custom Pin', ${lat}, ${lng}); map.closePopup();">Set as Search Center</button>
        </div>
    `;

    L.popup().setLatLng([lat, lng]).setContent(formHtml).openOn(map);
});

window.submitNewPlace = function(lat, lng) {
    const name = document.getElementById('newPlaceName').value.trim();
    const category = document.getElementById('newPlaceCategory').value;
    const district = document.getElementById('newPlaceDistrict').value;

    if (!name) {
        alert("Please enter a place name.");
        return;
    }

    fetch('/api/places/create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: name,
            category: category,
            district_name: district,
            latitude: lat,
            longitude: lng
        })
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed");
        return res.json();
    })
    .then(data => {
        map.closePopup();
        alert(`"${name}" saved successfully!`);
        loadAllPlaces();
    })
    .catch(err => alert("Error saving to database."));
};


function initData() {
    fetch('/api/districts/geojson/')
        .then(res => res.json())
        .then(data => {
            rawDistrictsData = data.features || [];
            const districtSelect = document.getElementById('districtFilter');
            
            rawDistrictsData.forEach(dist => {
                const p = dist.properties;
                const opt = document.createElement('option');
                opt.value = p.name;
                opt.textContent = `${p.name} (${p.code})`;
                districtSelect.appendChild(opt);
            });

            loadAllPlaces();
        })
        .catch(err => console.error("Error loading districts:", err));
}

function loadAllPlaces() {
    fetch('/api/places/geojson/')
        .then(res => res.json())
        .then(data => {
            rawPlacesData = data.features || [];
            applyFilters();
        })
        .catch(err => console.error("Error loading places:", err));
}

document.addEventListener('DOMContentLoaded', function() {
    initData();
    document.getElementById('searchInput').addEventListener('input', applyFilters);
    document.getElementById('districtFilter').addEventListener('change', applyFilters);
    document.getElementById('categoryFilter').addEventListener('change', applyFilters);
});