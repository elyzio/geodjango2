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

    // var map = L.map('map').setView([-8.5586, 125.5736], 13);
    {% if shop.latitude and shop.longitude %}
    var lat = {{ shop.latitude }};
    var lng = {{ shop.longitude }};
    {% else %}
    var lat = -8.5586;
    var lng = 125.5736;
    {% endif %}
    var map = L.map('map', {
        center: [lat, lng],
        zoom: 15,
        layers: osm
    });

    var baseLayers = {
        'OpenStreetMap': osm,
        'EsriWorldImagery': esw,
        'GoogleMaps': gom,
    };

    const layerControl = L.control.layers(baseLayers).addTo(map);
    {% if shop.latitude != null and shop.longitude != null %}
    L.marker([lat, lng])
        .addTo(map)
        .bindPopup(`Latitude: ${lat.toFixed(5)}, Longitude: ${lng.toFixed(5)}`)
        .openPopup();
    {% endif %}