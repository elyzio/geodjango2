{% load static %}
// var map = L.map('map').setView([-8.5586, 125.5736], 13);

// map tipe
var osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  // attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19,
  attribution: "© OpenStreetMap",
});

var esw = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    maxZoom: 19,
    attribution:
      "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
  }
);

var gom = L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
  maxZoom: 20,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
});

var map = L.map("map", {
  center: [-8.5586, 125.5736],
  zoom: 10,
  layers: osm,
  zoomControl: false,
});

var baseLayers = {
  OpenStreetMap: osm,
  EsriWorldImagery: esw,
  GoogleMaps: gom,
};

L.control
  .zoom({
    position: "topright", // Move zoom buttons to top-right
  })
  .addTo(map);

const layerControl = L.control.layers(baseLayers).addTo(map);

var customIcon = L.icon({
  iconUrl: '{% static "leaflet/images/kiosk.png" %}',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

let allMarkers = [];
let activeMarkers = [];

const pixelThreshold = 50;
function fetchAndDisplayShops(municipalityId = "") {
  const url = municipalityId
    ? `/api/shops/?municipality_id=${municipalityId}`
    : `/api/shops/`;

  fetch(url)
    .then(res => res.json())
    .then(shops => {
      // Clear existing marker arrays
      allMarkers = [];
      activeMarkers.forEach(m => map.removeLayer(m));
      activeMarkers = [];

      // Add new markers
      shops.forEach(shop => {
        if (shop.latitude && shop.longitude) {
          const marker = L.marker([shop.latitude, shop.longitude], {
            icon: customIcon
          });
          marker.shop = shop;
          allMarkers.push(marker);
          marker.on("click", () => showShopDetail(shop));
        }
      });

      updateVisibleMarkers();
      map.on("zoomend moveend", updateVisibleMarkers);
    });
}

function updateVisibleMarkers() {
  // Remove current
  activeMarkers.forEach(m => map.removeLayer(m));
  activeMarkers = [];

  const projected = allMarkers.map(m => {
    const latlng = m.getLatLng();
    return {
      marker: m,
      point: map.latLngToContainerPoint(latlng)
    };
  });

  const shown = [];

  projected.forEach(({ marker, point }) => {
    const isTooClose = shown.some(({ point: other }) => {
      return point.distanceTo(other) < pixelThreshold;
    });

    if (!isTooClose) {
      shown.push({ marker, point });
    }
  });

  shown.forEach(({ marker }) => {
    marker.addTo(map);
    activeMarkers.push(marker);
  });
}

function showShopDetail(shop) {
  document.getElementById("shop-details").style.display = "block";
  const panel = document.getElementById("shop-details");
  panel.classList.add("show");

  const locationParts = [
    shop.municipality || "",
    shop.administrativepost || "",
    shop.village || "",
    shop.aldeia || ""
  ].filter(Boolean).join(", ");

  document.getElementById("detail-name-title").textContent = shop.name || "Shop Information";
  document.getElementById("detail-owner").textContent = shop.owner || "---";
  document.getElementById("detail-contact").textContent = shop.contact || "---";
  document.getElementById("detail-location").textContent = locationParts || "---";
  document.getElementById("detail-gmaps").href = `https://maps.google.com/?q=${shop.latitude},${shop.longitude}`;

  const container = document.getElementById("shop-images");
  container.innerHTML = "";

  if (shop.images && shop.images.length > 0) {
    shop.images.forEach(img => {
      const imgEl = document.createElement("img");
      imgEl.src = img.url;
      imgEl.className = "img-fluid mx-1";
      imgEl.style.height = "150px";
      imgEl.style.width = "100%";
      imgEl.style.objectFit = "cover";
      imgEl.style.scrollSnapAlign = "center";
      container.appendChild(imgEl);
    });
  } else {
    const defaultImg = document.createElement("img");
    defaultImg.src = '{% static "img/default.png" %}';
    defaultImg.alt = "No Image";
    defaultImg.className = "img-fluid mx-1";
    defaultImg.style.height = "150px";
    defaultImg.style.width = "100%";
    defaultImg.style.objectFit = "cover";
    container.appendChild(defaultImg);
  }
}

map.on("click", () => {
  document.getElementById("shop-details").classList.remove("show");
});

document
  .getElementById("shop-filter-form")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    const municipalityId = document.getElementById("shop-filter").value;
    fetchAndDisplayShops(municipalityId);
  });

// Load all on page load
document.addEventListener("DOMContentLoaded", () => {
  fetchAndDisplayShops();
});
