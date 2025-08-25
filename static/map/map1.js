let map;

async function initMap() {
  const position = STATIC_URLS.default_position || { lat: -8.552320, lng: 125.541782 };

  // Load required libraries
  const { Map } = await google.maps.importLibrary("maps");

  // Initialize the map
  map = new Map(document.getElementById("map"), {
    center: position,
    zoom: 10,
    disableDefaultUI: true,
    zoomControl: true,
    streetViewControl: false,
    mapTypeId: 'roadmap',
  });

}
