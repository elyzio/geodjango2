var osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    // attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    attribution: '© OpenStreetMap'
});

var esw = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19,
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});

var gom = L.tileLayer('http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
});


{% if page == 'update' %}
{% if shop.latitude and shop.longitude %}
var lat = {{ shop.latitude }} || -8.5586;
var lng = {{ shop.longitude }} || 125.5736;
{% endif %}
{% else %}
var lat = -8.5586;
var lng = 125.5736;
{% endif %}

var map = L.map('map', {
    center: [lat, lng],
    zoom: 10,
    layers: osm
});

var baseLayers = {
    'OpenStreetMap': osm,
    'EsriWorldImagery': esw,
    'GoogleMaps': gom,
};

const layerControl = L.control.layers(baseLayers).addTo(map);

var marker = L.marker([lat, lng], { draggable: true }).addTo(map);

// Set the initial values to form fields
document.getElementById('id_latitude').value = lat;
document.getElementById('id_longitude').value = lng;

// When marker is dragged
marker.on('dragend', function (e) {
    var position = marker.getLatLng();
    document.getElementById('id_latitude').value = position.lat;
    document.getElementById('id_longitude').value = position.lng;
});

// Optional: add a click on map to reposition the marker
map.on('click', function (e) {
    marker.setLatLng(e.latlng);
    document.getElementById('id_latitude').value = e.latlng.lat;
    document.getElementById('id_longitude').value = e.latlng.lng;
});